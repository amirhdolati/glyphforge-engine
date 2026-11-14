# Contributing

Use Python 3.10 or newer. Keep the core free of runtime dependencies and preserve upstream notices in vendored files.

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

## Commit messages and documentation

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

| Type | Use for |
| --- | --- |
| `feat` | New user-facing capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `build` | Build system, dependencies, packaging |
| `refactor` | Code change that is neither feat nor fix |
| `test` | Tests only |
| `chore` | Maintenance that does not change product behavior |

Format: `<type>(optional-scope): <imperative summary>`

Examples:

- `feat(camera): add dolly path helpers for mesh demos`
- `fix(terminal): restore the alternate screen after SIGINT`
- `docs: document moving cameras and gallery exports`

Keep the subject under ~72 characters, use the imperative mood, and write in English.

All project documentation (`README`, `docs/`, `CONTRIBUTING`, examples READMEs, and contributor-facing comments) must be in English. Do not add localized documentation files.

