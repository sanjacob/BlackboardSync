# BlackboardSync
### Automatic Syncing Of Your Blackboard Content

[![Get on PyPI][pypi-shield]][pypi] [![License: GPL  v2][license-shield]][gnu] [![Build][build-shield]][actions]

**BlackboardSync** performs a periodic, incremental download of all your Blackboard content, such as lecture slides, lab sheets, and other attachments.


<div align="center">
	<img src="https://raw.githubusercontent.com/jacobszpz/BlackboardSync/main/blackboard_sync/assets/logo.png" height="auto" width="25%" />
</div>


## About

Being a student in this day and age means constantly having to keep up to date with the files that are uploaded to the student portal. I needed a tool that would take care of retrieving these files for me, allowing me to focus on the work to be done. Something I could set up and forget about.



What I was looking for in such an application was:

- Automatic syncing with minimal intervention after the initial setup
- Graphical interface
- Cross-platform compatibility
- It would make use of the [Blackboard REST API][blackboard-api]

### 30+ Universities Supported Around the World


**Why is my university not supported?**

Simply put, some information is necessary to make the login process compatible with any given university. If you would like to help to add support for your university, or would like to see which universities are currently supported, [start here.](UNIVERSITIES.md)



Built with:

- [Python 3.10][python]
- [PyQt5][pyqt]



## Features

- Supported content:
  - Attachments of any type (e.g. .docx, .pptx, .pdf, etc.)
  - Internet links
  - Content descriptions (saved as html files)
- Cross-platform
  - Linux, Windows, and macOS ready



## Installation

#### Binaries

You can find all releases on [GitHub][releases].
Only MacOS (.dmg) and Windows (.exe) are supported at the moment.

Note: These releases are automatically built on GitHub Actions from source.

**⚠️ ATTENTION MACOS USERS **

On MacOS, you will face an issue when trying to open the application, since it has not
been notarised by Apple. A workaround can be found [here][apple-dev].


#### From PyPI

```bash
python3 -m pip install blackboardsync
python3 -m blackboard_sync # notice the underscore
```



#### From source

##### Requirements

[Python 3.10 & pip][python]

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
pipenv run python -m blackboard_sync
```





## Contributions

Contributions are welcome.

More details available at [CONTRIBUTING.md](CONTRIBUTING.md)



##### Bugs, issues or feature requests?

Open a GitHub issue [here][issues].




## Show Your Support

##### Ko-fi ☕
[![Support BBSync on ko-fi][kofi-shield]][kofi]

##### LiberaPay
[![LiberaPay][lp-shield]][liberapay]

##### Bitcoin ₿

`bc1qhvcs07y3jnf09kahefscs05gxlmvhu542wzvgp`



## License

[![License: GPL  v2][license-shield]][gnu]

This software is distributed under the [General Public License v2.0][license], more information available at the [Free Software Foundation][gnu].



## Acknowledgements

[Blackboard API documentation][blackboard-api]

[PyInstaller][pyinstaller]

README templates/guide by [tonycrosby-tech][tonycrosby], [neildrew][neildrew], and [Rita Łyczywek][bulldogjob]



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
[apple-dev]: https://support.apple.com/en-gb/guide/mac-help/mh40616/mac


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
