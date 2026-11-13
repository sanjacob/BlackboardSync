# BlackboardSync — agent reference

PyQt6 tray app that logs into a university's Blackboard Learn (via an embedded
browser), then periodically downloads all course content to disk.
Python **3.14** only (`requires-python = ">=3.14,<3.15"`). Deps managed with **uv** (`uv.lock`).
CONTRIBUTING.md still mentions pipenv; that's outdated.

## Setup & checks (mirror `.github/workflows/pytest.yml`)
```bash
uv sync --locked                       # all groups by default (test, lint, docs, package)
uv run flake8 blackboard_sync/qt blackboard_sync/content
uv run mypy --strict blackboard_sync/qt
uv run pytest                          # Qt tests need xvfb + Qt system libs (libegl1, libxcb-*, ...)
uv run python -m blackboard_sync       # run the app; "Fakeboard (dev)" uni = mock server, no account needed
```
Lint/type-check are only enforced on `qt/` and `content/`.

## Architecture (MVC-ish)
`__main__.py` → `SyncController` (`sync_controller.py`) wires the **model** `BlackboardSync`
(`sync.py`) to the **view** `UIManager` (`qt/manager.py`) via Qt signals (`UIManager.Signals`).
The controller is the only place model and UI meet.

Data flow: login webview captures cookies → `BlackboardSync.auth()` builds a
`BlackboardExtended` session (external `bblearn` package, imported as `blackboard`) →
background thread `_sync_task` polls every 10s; when `outdated` or forced, runs
`BlackboardDownload.download()` (`download.py`) → for each course, builds a tree of
content objects then `.write(path, executor)` schedules file writes on `SyncExecutor`
(`executor.py`, a ThreadPoolExecutor that re-raises worker exceptions).

## Where to start for…
| Change | Start here |
|---|---|
| Sync scheduling, login/logout state, error flags | `sync.py` (`BlackboardSync`) |
| Which courses are fetched (year filter, data sources) | `download.py` (`BBMembershipFilter`) |
| Handling a Blackboard content type | `content/content.py` → `Content.get_handler()` match; add a handler module in `content/` |
| Download skip rules (modified-since, availability) | `Content.should_download`, `content/job.py` (`DownloadJob.has_changed`) |
| Folder/file layout on disk | `content/course.py` (`<year>/<course title>/…`), `content/document.py` (single attachment collapses into parent) |
| File attachments / videos filtered | `content/document.py`, `content/attachment.py` |
| HTML descriptions, embedded links & images | `content/body.py`, `content/templates.py` (HTML template), `content/webdav.py` (link extraction, 20 MB / non-video limits) |
| External links (.url/.desktop files) | `content/externallink.py` |
| Low-level write helpers | `content/base.py` (`BStream` bytes, `FStream` text) |
| Persisted settings (ini file in user config dir) | `config.py` (`SyncConfig`; setters auto-save via `@Config.persist`) |
| Add/modify a university | `universities.json` + `UNIVERSITIES.md` + `CHANGELOG.md` (see below) |
| University autodetect by IP | `institutions.py` `autodetect()`, `ip.py` (ipify + RDAP/whoisit) |
| Update check | `updates.py` |
| UI windows | `qt/SetupWizard`, `qt/LoginWebView`, `qt/SettingsWindow`, `qt/SyncTrayIcon`, `qt/dialogs.py`, `qt/notification.py`. Each `.py` loads its `.ui` (Qt Designer) via `qt/assets.py` |
| Translations | `qt/translations/` (loaded in `UIManager.load_translator`) |
| Startup-on-login, open folder, "time ago" | `qt/utils.py` |
| Packaging | `BlackboardSync.spec` (PyInstaller), `packaging/{linux,windows,macos}`, `.github/workflows/build.yml` (tags → release) |
| Docs | `docs/` (Sphinx autodoc, `docs/dev/*.rst`) |

## Gotchas
- **Universities are referenced by list index** (`SyncConfig.university_index`). Never reorder or
  delete entries in `universities.json`; new ones go just before the final `Fakeboard` entry
  (the `uninew.yml` workflow auto-generates PRs from `[New University]` issues this way).
- Version comes from git tags (`setuptools_scm`); no version string to bump by hand.
- Blackboard API models/filters (`BBCourseContent`, `BBResourceType`, `BBMembershipFilter`…) live
  in the external `bblearn` and `bwfilters` packages, not this repo.
- Changes worth noting go under `## [Unreleased]` in `CHANGELOG.md` (Keep a Changelog format).

## Tests (`tests/`)
`test_content.py` (content handlers, mocked session + hypothesis strategies in `strategies.py`),
`test_qt.py` (pytest-qt widgets), `test_sync_config.py`, `test_institutions.py` (JSON validates).
