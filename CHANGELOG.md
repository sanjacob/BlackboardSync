# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.9.11] - 2023-09-25

### Changed
- Pin dependencies in Pipfile and pyproject.toml for improved stability
- Add some classifiers to show in PyPI

## [0.9.10] - 2023-09-17

### Fixed
- Other issues when migrating to pydantic v2

## [0.9.9] - 2023-09-17

### Fixed
- Bug with pydantic Url typing

## [0.9.8] - 2023-09-07

### Changed
- Multiple dependency updates including a security update

## [0.9.7] - 2023-06-30

### Fixed
- Issues with redownloading all files after changing download location
- Potential issue where remaining downloads would be cancelled at the end of sync

### Changed
- WebDav downloads are now also multithreaded

## [0.9.6] - 2023-06-29

### Changed
- Changing download since to an earlier year will cause a redownload
- PyInstaller has been upgraded to 5.13, and other dependencies have also been upgraded

### Fixed
- Bug where resetting download since to 'all' would not take effect
- Type hints were improved

## [0.9.5] - 2023-06-27

### Added
- Option to go over setup wizard again after initial setup

### Fixed
- Issue with session logging back in immediately after logout

### Changed
- Uninstalling the program in Windows will also delete user configuration


## [0.9.4] - 2023-06-26

### Added
- Option to limit the courses downloaded by earliest creation date
- Release notes from CHANGELOG

### Fixed
- App no longer crashes when downloading internet links on Linux


## [0.9.3] - 2023-06-25

### Added
- Add basic support for 29 universities: Arkansas, UVM, Europea Madrid, ECOTEC, URSE, Palermo,
  Tecnologica del Salvador, Alcala, GWU, APU, Bucks, Northampton, Beds, YSU, Ohio, Princess Nourah,
  Leeds Beckett, Post, UAGM, Alabama, Torrens Australia, Holmes Institute, Trinity College Dublin,
  Georgian College, Cardiff, Sheffield Hallam, West of England, Northumbria, Ulster

### Fixed
- Prereleases are marked correctly on Github

### Changed
- Small tweak to initial desktop notification on first download

## [0.9.0] - 2023-06-21

### Changed
- Finally change data source approach to follow institutional rules


### Added
- Add basic support for 10 universities: Westminster, Reading,
  East Anglia, Durham, Salford, South Wales, Leicester, ICL, Bristol,
  Sheffield


### Removed
- User setting for data source



## [0.8.3] - 2023-06-16

### Fixed
- Opening preferences window would previously crash the program
- WebDav filepaths are now sanitised
- Package workflow not triggering on CI



## [0.8.0] - 2023-06-04

### Features
- User must now login in a webview instead, to support 2FA and arbitrary redirects
- Automatic packaging of macOS and Windows applications in github actions
- Improved testing strategy
- Descriptions are now saved as HTML files instead of markdown
- Attachments which are only linked from within content are now supported
- Various other minor improvements



## [0.7.0] - 2021-03-03

### Features
- New option to choose whether files should be re-downloaded upon changing the sync location.
- Sync frequency is now adjustable.
- If the user session expires, BBSync will reflect this and try to login back in using saved configuration.
- Some improvements to the UI and experience in Windows.
- Sync connection errors are now logged to a file.
- Improved README.
- Added basic build scripts.
- Added contributions policy.
- Added changelog.

### Fixes
- File names are now sanitised to comply with (most) Windows file system requirements.



## [0.5.0] - 2021-02-10

### Features
- Added GUI
- Simplified user setup



[0.8.0]: https://github.com/jacobszpz/BlackboardSync/releases/
