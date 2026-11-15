# BlackboardSync — agent reference

PyQt6 tray app: logs into Blackboard Learn via an embedded browser, then periodically downloads course content.
Python 3.14–3.15 (builds use 3.15), deps via **uv** (CONTRIBUTING.md's pipenv instructions are outdated).

```bash
uv sync --locked
uv run flake8 blackboard_sync/qt blackboard_sync/content && uv run mypy --strict blackboard_sync/qt
uv run pytest                     # needs xvfb + Qt system libs
uv run python -m blackboard_sync  # "Fakeboard (dev)" uni = mock server, no account needed
```

## Architecture
`SyncController` (`sync_controller.py`) connects the model `BlackboardSync` (`sync.py`: auth, sync thread,
scheduling) to the view `UIManager` (`qt/manager.py`) via Qt signals. Each sync runs `BlackboardDownload`
(`download.py`, course filtering), which builds a tree of `content/*` handlers that write files on a thread pool.

## Where to start
- **New/changed content type:** `Content.get_handler()` in `content/content.py`; skip rules in `Content.should_download` and `content/job.py`
- **Disk layout:** `content/course.py` (`<year>/<course>/…`), `content/document.py`
- **Attachments, descriptions, links:** `content/{attachment,body,webdav,externallink,templates}.py`
- **Settings persistence:** `config.py` (`SyncConfig`, auto-saved ini)
- **Universities:** `universities.json` (+ `UNIVERSITIES.md`, `CHANGELOG.md`); IP autodetect in `institutions.py`, `ip.py`
- **UI:** `qt/*.py` + matching Designer `.ui` files; translations in `qt/translations/`
- **Packaging/CI:** `BlackboardSync.spec`, `packaging/`, `.github/workflows/`

## Gotchas
- Config stores the university **by list index**: never reorder/delete `universities.json` entries; add new ones just before the final `Fakeboard` entry.
- Version comes from git tags (`setuptools_scm`).
- Blackboard API models/filters come from the external `bblearn` (`blackboard`) and `bwfilters` packages.
- Log notable changes under `## [Unreleased]` in `CHANGELOG.md`.
