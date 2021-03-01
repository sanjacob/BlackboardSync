# BlackboardSync for UCLan
### Automatic Syncing Of Your Blackboard Content

BlackboardSync does a periodic, incremental download of all your Blackboard content, such as lecture slides, lab sheets, and other attachments.



<img src="blackboard_sync/assets/logo.png" height="auto" width="25%" />



## Table Of Contents

1. [About](#about)
2. [Features](#features)
3. [Installation](#installation)
   - [Binaries](#binaries)
   - [Running w/o building](#running-without-building)
   - [Building from source](#building-from-source)
4. [Usage](#usage)
5. [Contributions](#contributions)
6. [Project Structure](#project-structure)
7. [Show Your Support](#show-your-support)
8. [License](#license)
9. [Acknowledgements](#acknowledgements)



## About

Being a student in this day and age means constantly having to keep up to date with the files that are uploaded to the student portal. I needed a tool that would take care of retrieving these files for me, allowing me to focus on the work to be done. Something I could set up and forget about.



What I was looking for in such an application was:

- Automatic syncing with minimal intervention after the initial setup
- No console required
- Cross-platform compatibility
- It would make use of the [Blackboard REST API][blackboard-api]



**Why just for UCLan?**

While most of the application is not bound to the UCLan portal, the auth process is. Other universities might have a very different login process which I cannot account for. However, if you have an idea about how to implement this across the board, say so [here][universal-login].



If you want to adapt this for your own institution / personal use, that is perfectly possible and easy, just fork the repo and overwrite the `auth` method of `BlackboardSession` in the [`blackboard/api.py`](blackboard_sync/blackboard/api.py) file.



Built with:

- [Python 3.9][python]
- [PyQt5][pyqt]



## Features

- Supported content:
  - Attachments of any type (e.g. .docx, .pptx, .pdf, etc.)
  - Internet links
  - Content descriptions (saved as markdown files [^1])
- Cross-platform
  - Linux, Windows, and macOS ready



[^1]: You can view markdown files with [Typora][typora]



## Installation

#### Binaries

Currently unavailable (until a more stable version).

Alternatively, you can run the python package [directly](#running-without-building), or build an executable yourself by following [these steps](#building-from-source).



#### Running without building

##### Requirements

[Python 3.9 & pip][python]

[Pipenv][pipenv]

[Git][git]



From your command line:

Clone the repository

```bash
git clone https://github.com/jacobszpz/BlackboardSync.git
cd BlackboardSync
```



To fetch the dependencies, run

```bash
pipenv install
```



To start the program

```bash
cd blackboard_sync
pipenv run python blackboard_sync
```



#### Building from source

##### Requirements

[Python 3.9 & pip][python]

[Pipenv][pipenv]

[Git][git]



```bash
# Clone the repository
git clone https://github.com/jacobszpz/BlackboardSync.git
cd BlackboardSync
# Create virtual environment and install dependencies
pipenv install -d
```



##### Linux & macOS

```bash
# Execute build script
$ chmod +x build.sh
$ ./build.sh
# An executable will be generated, run with
$ dist/BlackboardSync
# You can also move it to a more convenient location
```



##### Windows

```batch
# Execute build script
build.bat
# An executable will be generated, run with
dist\BlackboardSync.exe
# You can also move it to a more convenient location
```



## Usage

BlackboardSync resides in your system tray.

In windows, this looks like:

![][tray-win] 



Initially, it may appear in the overflow menu.
![][tray-win-of]

To place it in the system tray, simply drag the icon there.



##### Login

To get started, type in the details of your UCLan account. You may choose to save your login details to avoid typing them every time your session expires or you quit the application. However, be warned this will store your password in plain-text somewhere on your device.



![][login-win]



After you login, the first download will start right away. It may take upwards of 20 minutes to get all your files, specially if you have a large amount of content or a slow internet connection. This only needs to be done once, the downloads to follow will only include files that were added/modified after the last download, which will only take a few seconds in most cases.



##### Tray

At any time you can keep track of the status by right-clicking on the tray icon.

![][tray-win-open]



| Menu Option | Action                                                       |
| ----------- | ------------------------------------------------------------ |
| Sync Now    | Forces BBSync to fetch new files as soon as possible         |
| Preferences | Opens the preferences dialog                                 |
| Last Synced | Normally displays the last time the app checked for / downloaded new files |
| Quit        | Closes the program (may take a few seconds)                  |



Left-clicking on the icon will instead open the sync location on the file explorer.



##### Settings

![][settings-win]



| Setting           | Description                                                  | Modifiable    |
| ----------------- | ------------------------------------------------------------ | ------------- |
| Download Location | The location of downloaded files (changing this will cause all files to be downloaded again to the new location) | Yes           |
| Sync Every        | Changes the time to wait between each sync                   | Yes           |
| Data Source       | Internal setting that affects which modules to download content from | Currently not |
| User Session      | Shows the current user and allows to log out of the session  | Yes           |

\* Settings won't take effect unless saved



## Contributions

Contributions are welcome.

More details available at [CONTRIBUTING.md](CONTRIBUTING.md)



##### Bugs, issues or feature requests?

Open a GitHub issue [here][issues].



## Project Structure

```bash
.
├── blackboard_sync # Contains the python code and assets
│   ├── __about__.py # Project metadata, such as version and author
│   ├── __main__.py # Python package entrypoint
│   ├── assets # Icons used in the application
│   │   ├── alert.png
│   │   ├── alert.svg
│   │   ├── logo.ico # Windows executable icon
│   │   └── logo.png
│   ├── blackboard # Blackboard API
│   │   ├── api.py
│   │   └── blackboard.py
│   ├── download.py # Simple script that handles downloading content from blackboard,
│ 	│ 				# also offers limited functionality as a standalone script
│   ├── qt # Qt interface files
│   │   ├── LoginWindow.ui
│   │   ├── PersistenceWarning.ui
│   │   ├── qt_elements.py # Code to create the graphical interface and interact with it
│   │   └── SettingsWindow.ui
│   ├── sync_controller.py # Connects sync.py and qt/qt_elements.py
│   ├── sync.py # The core of BlackboardSync as an application
│   └── tests # Development tests
│       ├── api_tests.py
│       ├── bb_tests.py
│       └── qt_tests.py
├── build.bat # Windows build script
├── build.sh # *nix build script
├── LICENSE
├── Pipfile # Contains dependencies, used by pipenv
├── Pipfile.lock # Used by pipenv
├── README.md # The file you are currently reading
├── CONTRIBUTING.md # Contributions policy
└─── screenshots # Stores the screenshots shown in this file
    ├── login_win.png
    ├── settings_win.png
    ├── tray_win_open.png
    ├── tray_win_overflow.png
    └── tray_win.png
```




## Show Your Support

##### Bitcoin ₿

`bc1qhvcs07y3jnf09kahefscs05gxlmvhu542wzvgp`

##### Dogecoin 🐶

`DU7nuPHcphHMKp2932LurnWbVzozmrkKmt`



## License

[![License: GPL  v2][license-badge]][gnu]


This software is distributed under the [General Public License v2.0][license], more information available at the [Free Software Foundation][gnu].



## Acknowledgements

[Blackboard API documentation][blackboard-api]

[PyInstaller][pyinstaller]

[README template by tonycrosby-tech][tonycrosby]

[README template by neildrew][neildrew]

[README guide by Rita Łyczywek][bulldogjob]



<!-- MARKDOWN LINK REFERENCES -->

[universal-login]: https://github.com/jacobszpz/BlackboardSync/issues/3	"BBSync login"
[pyqt]: https://pypi.org/project/PyQt5/5.15.1/	"Python Bindings for Qt 5"
[typora]: https://typora.io/ "Typora"
[releases]: https://github.com/jacobszpz/BlackboardSync/releases "BlackboardSync Releases"
[issues]: https://github.com/jacobszpz/BlackboardSync/issues/new "BlackboardSync Issues"
[git]: https://git-scm.com/	"Git"
[python]: https://www.python.org/ "Python.org"
[pipenv]: https://pipenv.pypa.io/en/latest/ "Pipenv"
[license]: LICENSE "General Public License"
[gnu]: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html "Free Software Foundation"
[blackboard-api]: https://developer.blackboard.com/portal/displayApi	"Blackboard API Reference"
[pyinstaller]: https://www.pyinstaller.org/	"PyInstaller"



<!-- RELEASES -->

[release-win]: https://github.com/jacobszpz/BlackboardSync/releases/	"Windows Release of BlackboardSync"
[release-win-64]: https://github.com/jacobszpz/BlackboardSync/releases/	"Windows x64 Release of BlackboardSync"
[release-mac]: https://github.com/jacobszpz/BlackboardSync/releases/	"macOS Release of BlackboardSync"
[release-mac-64]: https://github.com/jacobszpz/BlackboardSync/releases/	"macOS x64 Release of BlackboardSync"
[release-nix]: https://github.com/jacobszpz/BlackboardSync/releases/	"Linux Release of BlackboardSync"
[release-nix-64]: https://github.com/jacobszpz/BlackboardSync/releases/	"Linux x64 Release of BlackboardSync"



<!-- README TEMPLATES -->

[tonycrosby]: https://gist.github.com/tonycrosby-tech/c18c2b6c74900c6080fc097ca0718839	"tonycrosby-tech README template"
[neildrew]: https://github.com/othneildrew/Best-README-Template	"othneildrew README template"
[bulldogjob]: https://bulldogjob.com/news/449-how-to-write-a-good-readme-for-your-github-project	"bulldogjob README guide"



<!-- MARKDOWN IMAGE REFERENCES -->

[license-badge]: https://img.shields.io/badge/License-GPL%20v2-blue.svg
[tray-win]: screenshots/tray_win.png
[tray-win-of]: screenshots/tray_win_overflow.png
[tray-win-open]: screenshots/tray_win_open.png
[login-win]: screenshots/login_win.png
[settings-win]: screenshots/settings_win.png

