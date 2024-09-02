# BlackboardSync
### Automatic Downloads Of Your Blackboard Content

[![Get on PyPI][pypi-shield]][pypi] [![License: GPL  v2][license-shield]][gnu] [![Build][build-shield]][actions] [![Matrix][matrix-shield]][matrix]

**BlackboardSync** performs a periodic,
incremental download of all your Blackboard content,
such as lecture slides, lab sheets, and other attachments.

<div align="center">
	<img src="https://github.com/sanjacob/BlackboardSync/assets/52013991/b7414212-034a-42a6-ab20-bb51394d885e" height="auto" width="75%" />
</div>


## About

Being a student in this day and age means constantly having to
keep up to date with the files that are uploaded to the student portal.
I needed a tool that would take care of retrieving these files for me,
allowing me to focus on the work to be done.
Something I could set up and forget about.

What I was looking for in such an application was:

- Automatic syncing with minimal intervention after the initial setup
- Graphical interface
- Cross-platform compatibility
- It would make use of the [Blackboard REST API][blackboard-api]

### [60+ Universities](UNIVERSITIES.md) Supported Around the World

**Why is my university/college not supported?**

To provide support for a specific university, it is necessary to have
some knowledge about its login process.

If you would like to help to add support for your university,
or would like to see which universities are currently supported,
[start here.](UNIVERSITIES.md)

**Built with:**

- [Python 3.11][python]
- [PyQt6][pyqt]


## Features

- Supported content:
  - Attachments of any* type (e.g. .docx, .pptx, .pdf, etc.)
  - Internet links
  - Content descriptions (saved as html files)
- Cross-platform
  - Linux, Windows, and macOS ready

*: Except videos


## Installation

#### Microsoft Store

<a href="https://apps.microsoft.com/detail/9NSXZGKPNX2H?cid=github-readme&mode=mini">
	<img src="https://get.microsoft.com/images/en-us%20dark.svg" width="200"/>
</a>

#### Flathub

<a href="https://flathub.org/apps/app.bbsync.BlackboardSync">
  <img alt="Download on Flathub" src="https://flathub.org/api/badge?svg&locale=en" width="200"/>
</a>

#### Windows (.exe) and MacOS (.dmg)

Please first download the [latest release][stable].

**MacOS Installation**

You will need to confirm the installation in `System Preferences > Security and Privacy`.
You can see the specific steps in the GIF below. After the program has been installed, you may eject the mounted disk.

![MacOSInstall][MacOSInstall]


#### PyPI

```bash
python3 -m pip install blackboardsync
blackboardsync
```

#### From source

##### Requires [Python >=3.10, pip][python], [pipenv][pipenv], [git][git]

```bash
git clone https://github.com/sanjacob/BlackboardSync.git
cd BlackboardSync
pipenv install
pipenv run python -m blackboard_sync
```

#### Previous Releases

You can find all releases on [GitHub][releases].


## Contributions

Contributions are welcome.

More details available at [CONTRIBUTING.md](CONTRIBUTING.md)

**We are looking for beta testers for all platforms!**

##### Bugs, issues or feature requests?

Open a GitHub issue [here][issues].


## Show Your Support

##### Ko-fi ☕
[![Support BBSync on ko-fi][kofi-shield]][kofi]

##### LiberaPay
[![LiberaPay][lp-shield]][liberapay]

##### Bitcoin ₿

`bc1qhvcs07y3jnf09kahefscs05gxlmvhu542wzvgp`

If you wish to contribute in a different way, please inquire.


## License

[![License: GPL  v2][license-shield]][gnu]

This software is distributed under the [General Public License v2.0][license], more information available at the [Free Software Foundation][gnu].


## Acknowledgements

[Blackboard API documentation][blackboard-api]

[PyInstaller][pyinstaller]

README templates/guide by [tonycrosby-tech][tonycrosby], [neildrew][neildrew], and [Rita Łyczywek][bulldogjob]

Flathub team for their quick work in approving the app :heart:


<!-- Project -->

[releases]: https://github.com/sanjacob/BlackboardSync/releases "BlackboardSync Releases"
[issues]: https://github.com/sanjacob/BlackboardSync/issues/new "BlackboardSync Issues"
[stable]: https://github.com/sanjacob/BlackboardSync/releases/latest
[actions]: https://github.com/sanjacob/BlackboardSync/actions
[build-shield]: https://img.shields.io/github/actions/workflow/status/sanjacob/BlackboardSync/build.yml?branch=main
[MacOSInstall]: https://github.com/sanjacob/BlackboardSync/assets/52013991/6be5e390-3f66-4eb4-b8d5-6f3230ae52ef

<!-- Dependencies -->

[git]: https://git-scm.com/	"Git"
[python]: https://www.python.org/ "Python.org"
[pipenv]: https://pipenv.pypa.io/en/latest/ "Pipenv"
[pyqt]: https://pypi.org/project/PyQt6/	"Python Bindings for Qt 6"

<!-- Chat -->

[matrix]: https://matrix.to/#/#blackboardsync:matrix.org
[matrix-shield]: https://img.shields.io/matrix/blackboardsync%3Amatrix.org?logo=matrix

<!-- Packages -->

[pypi]: https://pypi.org/project/blackboardsync
[pypi-shield]: https://img.shields.io/pypi/v/BlackboardSync?color=%23241F21

<!-- Donations -->

[kofi]: https://ko-fi.com/Q5Q17XN36
[liberapay]: https://liberapay.com/BlackboardSync
[kofi-shield]: https://ko-fi.com/img/githubbutton_sm.svg
[lp-shield]: https://img.shields.io/liberapay/receives/BlackboardSync.svg?logo=liberapay

<!-- Licence -->

[license]: LICENSE "General Public License"
[gnu]: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html "Free Software Foundation"
[license-shield]: https://img.shields.io/github/license/sanjacob/BlackboardSync?color=%23241F21

<!-- Acknowledgements & README Templates -->

[blackboard-api]: https://developer.blackboard.com/portal/displayApi	"Blackboard API Reference"
[pyinstaller]: https://www.pyinstaller.org/	"PyInstaller"

[tonycrosby]: https://gist.github.com/tonycrosby-tech/c18c2b6c74900c6080fc097ca0718839	"tonycrosby-tech README template"
[neildrew]: https://github.com/othneildrew/Best-README-Template	"othneildrew README template"
[bulldogjob]: https://bulldogjob.com/news/449-how-to-write-a-good-readme-for-your-github-project	"bulldogjob README guide"
