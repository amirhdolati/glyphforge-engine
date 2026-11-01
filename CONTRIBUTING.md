# Contributing

Use Python 3.10 or newer. Keep the core free of runtime dependencies, keep user-facing documentation in English, and preserve upstream notices in vendored files.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
ruff check src examples tests tools --select F
ruff format --check src examples tests tools
python -m build
```

For rendering changes, include a focused regression test and an example frame. Test at small and non-square resolutions. Terminal changes should preserve cleanup under exceptions and should not bind keys to game-specific actions. New demos must support offline output through the shared runner.

Regenerate previews with `PYTHONPATH=src:. python tools/render_gallery.py` when visual behavior changes. Do not edit screenshots to claim output the renderer does not produce.

Keep `_vendor` changes narrow and explain their upstream impact. Open an issue with a minimal reproduction, Python version, operating system, terminal name, dimensions and color mode when reporting a bug. Do not include credentials or private assets.
