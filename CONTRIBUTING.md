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

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
Write each subject in English, start the summary with a verb, and aim for
72 characters or fewer. Use `type: summary` or `type(scope): summary`.

| Type | Use for |
| --- | --- |
| `feat` | New functionality |
| `fix` | Bug fixes |
| `docs` | Documentation |
| `build` | Build tools, dependencies, and packaging |
| `ci` | CI configuration and workflows |
| `refactor` | Code changes that preserve behavior |
| `perf` | Performance improvements |
| `test` | Tests |
| `chore` | Other project maintenance |

For example, use `docs: clarify the quick start` or
`fix(terminal): restore the cursor on exit`. Mark breaking changes with
`!` before the colon or a `BREAKING CHANGE:` footer.

Write project documentation in English. Use the README for the project
overview, prerequisites, and quick start. Link to the relevant guides from
the README and put longer guides in `docs/`. Use descriptive headings,
relative links for repository files, and alt text for screenshots.
