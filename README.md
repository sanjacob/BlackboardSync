# BlackboardSync
### Automatic Downloads Of Your Blackboard Content

[![Get on PyPI][pypi-shield]][pypi] [![License: GPL  v2][license-shield]][gnu] [![Build][build-shield]][actions]

**BlackboardSync** performs a periodic, incremental download of all your Blackboard content, such as lecture slides, lab sheets, and other attachments.

<div align="center">
	<img src="https://github.com/jacobszpz/BlackboardSync/assets/52013991/b7414212-034a-42a6-ab20-bb51394d885e" height="auto" width="75%" />
</div>



## About

Being a student in this day and age means constantly having to keep up to date with the files that are uploaded to the student portal. I needed a tool that would take care of retrieving these files for me, allowing me to focus on the work to be done. Something I could set up and forget about.



What I was looking for in such an application was:

- Automatic syncing with minimal intervention after the initial setup
- Graphical interface
- Cross-platform compatibility
- It would make use of the [Blackboard REST API][blackboard-api]

### [30+ Universities](UNIVERSITIES.md) Supported Around the World

**Why is my university not supported?**

Simply put, some information is necessary to make the login process compatible with any given university. If you would like to help to add support for your university, or would like to see which universities are currently supported, [start here.](UNIVERSITIES.md)



**Built with:**

- [Python 3.10][python]
- [PyQt5][pyqt]



## Features

- Supported content:
  - Attachments of any* type (e.g. .docx, .pptx, .pdf, etc.)
  - Internet links
  - Content descriptions (saved as html files)
- Cross-platform
  - Linux, Windows, and macOS ready

*: Except videos



## Installation

#### Windows (.exe) and MacOS (.dmg)

Please first download the [latest release][stable].



**Windows Installation**

You will first need to get around Microsoft SmartScreen by clicking in `More Details > Run Anyway`.

**MacOS Installation**

You will need to confirm the installation in `System Preferences > Security and Privacy`.
You can see the specific steps in the GIF below. After the program has been installed, you may eject the mounted disk.

![MacOSInstall][MacOSInstall]



#### Linux via Flatpak

<a href='https://flathub.org/apps/app.bbsync.BlackboardSync'><img width='240' alt='Download on Flathub' src='https://dl.flathub.org/assets/badges/flathub-badge-en.png'/></a>



Help in creating additional distributions is always welcome.



#### PyPI

```bash
python3 -m pip install blackboardsync
python3 -m blackboard_sync # notice the underscore (0.9.11 and below)
blackboardsync # from 0.9.12 onwards
```



#### From source

##### Requires [Python >=3.10, pip][python], [pipenv][pipenv], [git][git]

```bash
git clone https://github.com/jacobszpz/BlackboardSync.git
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



<!-- LINK REFERENCES -->

[universal-login]: https://github.com/jacobszpz/BlackboardSync/issues/3	"BBSync login"
[pyqt]: https://pypi.org/project/PyQt5/5.15.1/	"Python Bindings for Qt 5"
[pypi]: https://pypi.org/project/blackboardsync
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

[releases]: https://github.com/jacobszpz/BlackboardSync/releases/
[stable]: https://github.com/jacobszpz/BlackboardSync/releases/latest




<!-- README TEMPLATES -->

[tonycrosby]: https://gist.github.com/tonycrosby-tech/c18c2b6c74900c6080fc097ca0718839	"tonycrosby-tech README template"
[neildrew]: https://github.com/othneildrew/Best-README-Template	"othneildrew README template"
[bulldogjob]: https://bulldogjob.com/news/449-how-to-write-a-good-readme-for-your-github-project	"bulldogjob README guide"



<!-- SHIELDS -->

[pypi-shield]: https://img.shields.io/pypi/v/BlackboardSync
[license-shield]: https://img.shields.io/github/license/jacobszpz/BlackboardSync
[build-shield]: https://img.shields.io/github/actions/workflow/status/jacobszpz/BlackboardSync/build.yml?branch=main
[kofi-shield]: https://ko-fi.com/img/githubbutton_sm.svg
[lp-shield]: https://img.shields.io/liberapay/receives/BlackboardSync.svg?logo=liberapay



<!-- SHIELD LINKS -->

[actions]: https://github.com/jacobszpz/BlackboardSync/actions
[kofi]: https://ko-fi.com/Q5Q17XN36
[liberapay]: https://liberapay.com/BlackboardSync



<!-- GIFS -->

[MacOSInstall]: https://github.com/jacobszpz/BlackboardSync/assets/52013991/6be5e390-3f66-4eb4-b8d5-6f3230ae52ef
