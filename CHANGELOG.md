# Changelog
All notable changes to this project will be documented in this file.


## [0.8.0][] - 2023-06-04

### Features
- User must now login in a webview instead, to support 2FA and arbitrary redirects
- Automatic packaging of macOS and Windows applications in github actions
- Improved testing strategy
- Descriptions are now saved as HTML files instead of markdown
- Attachments which are only linked from within content are now supported
- Various other minor improvements



## 0.7.0 - 2021-03-03

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



## 0.5.0 - 2021-02-10

### Features
- Added GUI
- Simplified user setup



[0.8.0]: https://github.com/jacobszpz/BlackboardSync/releases/
