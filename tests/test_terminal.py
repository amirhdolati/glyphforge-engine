import os
import select
import subprocess
import sys
import time
import unittest


@unittest.skipUnless(os.name == "posix", "POSIX terminal transport")
class TerminalTests(unittest.TestCase):
    def test_restoration_after_success_and_exception(self):
        import pty
        import termios

        for fails in (False, True):
            with self.subTest(exception=fails):
                master, slave = pty.openpty()
                before = termios.tcgetattr(slave)
                script = (
                    "from glyphforge import Terminal, from_text\n"
                    "with Terminal() as terminal:\n"
                    ' terminal.draw(from_text("hello"))\n'
                    + (' raise RuntimeError("expected")\n' if fails else " pass\n")
                )
                proc = subprocess.Popen(
                    [sys.executable, "-c", script],
                    stdin=slave,
                    stdout=slave,
                    stderr=slave,
                )
                output = bytearray()
                try:
                    deadline = time.monotonic() + 8
                    while time.monotonic() < deadline:
                        if select.select([master], [], [], 0.05)[0]:
                            output.extend(os.read(master, 65536))
                        if proc.poll() is not None:
                            while select.select([master], [], [], 0)[0]:
                                output.extend(os.read(master, 65536))
                            break
                    proc.wait(timeout=1)
                    self.assertEqual(proc.returncode, 1 if fails else 0)
                    self.assertIn(b"\x1b[?25h", output)
                    self.assertIn(b"\x1b[?1049l", output)
                    after = termios.tcgetattr(slave)
                    pending = getattr(termios, "PENDIN", 0)
                    before[3] &= ~pending
                    after[3] &= ~pending
                    self.assertEqual(before, after)
                finally:
                    if proc.poll() is None:
                        proc.kill()
                        proc.wait()
                    os.close(master)
                    os.close(slave)

    def test_live_example_resize_and_quit(self):
        import fcntl
        import pty
        import struct
        import termios

        master, slave = pty.openpty()

        def resize(cols, rows):
            fcntl.ioctl(
                slave, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0)
            )

        resize(60, 20)
        proc = subprocess.Popen(
            [sys.executable, "-m", "examples.hello_terminal", "--256"],
            stdin=slave,
            stdout=slave,
            stderr=slave,
        )

        def until(needle):
            captured = bytearray()
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                if select.select([master], [], [], 0.05)[0]:
                    captured.extend(os.read(master, 65536))
                    if needle in captured:
                        return
                if proc.poll() is not None:
                    break
            self.fail(f"Missing {needle!r}: {bytes(captured[-300:])!r}")

        try:
            until(b"\x1b[19;1H")
            resize(30, 10)
            until(b"\x1b[9;1H")
            os.write(master, b"q")
            until(b"\x1b[?1049l")
            proc.wait(timeout=3)
            self.assertEqual(proc.returncode, 0)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
            os.close(master)
            os.close(slave)
