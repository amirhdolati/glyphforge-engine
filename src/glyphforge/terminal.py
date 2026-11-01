"""POSIX terminal ownership with restoration on exit and exceptions."""

import os
import select
import signal
import sys
from .ansi import FrameSnapshot, encode
from .input import Input, Event


def truecolor_supported():
    if os.environ.get("TERM_PROGRAM") == "Apple_Terminal":
        return False
    return (
        os.environ.get("COLORTERM", "").lower() in ("truecolor", "24bit")
        or any(
            n in os.environ.get("TERM", "").lower()
            for n in ("kitty", "direct", "ghostty", "wezterm")
        )
        or os.environ.get("TERM_PROGRAM", "").lower()
        in ("vscode", "iterm.app", "wezterm", "ghostty")
    )


class Terminal:
    def __init__(self, truecolor=None):
        self.truecolor = truecolor_supported() if truecolor is None else truecolor
        self.input = Input()
        self.old = None
        self.signals = {}
        self.frame_snapshot = FrameSnapshot()

    def __enter__(self):
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise RuntimeError(
                "Interactive rendering requires a TTY; use an offline exporter for previews."
            )
        if os.name != "posix":
            raise RuntimeError(
                "Interactive rendering needs a POSIX terminal (macOS, Linux, or WSL)."
            )
        import termios, tty

        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        try:
            tty.setraw(self.fd)
            for sig in (signal.SIGTERM, signal.SIGHUP):
                self.signals[sig] = signal.signal(sig, self._interrupt)
            sys.stdout.write(
                "\x1b[22;0t\x1b]2;GlyphForge Engine\x07"
                "\x1b[?1049h\x1b[?25l\x1b[?7l\x1b[>11u\x1b[?1004h\x1b[2J"
            )
            sys.stdout.flush()
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self

    @staticmethod
    def _interrupt(*args):
        raise KeyboardInterrupt

    def __exit__(self, *args):
        import termios

        try:
            sys.stdout.write(
                "\x1b[?2026l\x1b[?1003l\x1b[?1006l\x1b[?1004l\x1b[<u"
                "\x1b[0m\x1b[?7h\x1b[?25h\x1b[?1049l\x1b[23;0t"
            )
            sys.stdout.flush()
        finally:
            if self.old is not None:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
            for sig, handler in self.signals.items():
                signal.signal(sig, handler)

    def size(self):
        try:
            return os.get_terminal_size(sys.stdout.fileno())
        except OSError:
            return 80, 24

    def aspect(self):
        import fcntl, struct, termios

        try:
            rows, cols, xp, yp = struct.unpack(
                "HHHH", fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, b"\0" * 8)
            )
            value = (xp / cols) / (yp / rows)
            if 0.25 <= value <= 1:
                return value
        except (OSError, ZeroDivisionError):
            pass
        return 0.5

    def events(self):
        data = b""
        while select.select([self.fd], [], [], 0)[0]:
            chunk = os.read(self.fd, 4096)
            if not chunk:
                return [Event("exit")]
            data += chunk
        return self.input.feed(data)

    def mouse(self, enabled):
        sys.stdout.write(
            "\x1b[?1006h\x1b[?1003h" if enabled else "\x1b[?1003l\x1b[?1006l"
        )
        sys.stdout.flush()

    def clear(self):
        self.frame_snapshot.invalidate()
        sys.stdout.write("\x1b[0m\x1b[2J")

    def draw(self, buf, x=1, y=1, delta=False):
        buf = tuple(tuple(row) for row in buf)
        payload = (
            self.frame_snapshot.encode(buf, self.truecolor, x, y)
            if delta
            else encode(buf, self.truecolor, x, y)
        )
        if not delta:
            # Keep the optional delta cache synchronized with full redraws.
            self.frame_snapshot.previous = tuple(tuple(row) for row in buf)
            self.frame_snapshot.config = (bool(self.truecolor), x, y)
            self.frame_snapshot.force_full = False
        sys.stdout.write("\x1b[?2026h" + payload + "\x1b[?2026l")
        sys.stdout.flush()
