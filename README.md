# BlackboardSync
### Automatic Syncing Of Your Blackboard Content

[![License: GPL  v2][license-shield]][gnu] [![Build][build-shield]][actions] [![ReadTheDocs][docs-shield]][rtd]

**BlackboardSync** performs a periodic, incremental download of all your Blackboard content, such as lecture slides, lab sheets, and other attachments.


<div align="center">
	<img src="blackboard_sync/assets/logo.png" height="auto" width="25%" />
</div>


## About

Being a student in this day and age means constantly having to keep up to date with the files that are uploaded to the student portal. I needed a tool that would take care of retrieving these files for me, allowing me to focus on the work to be done. Something I could set up and forget about.



What I was looking for in such an application was:

- Automatic syncing with minimal intervention after the initial setup
- Graphical interface
- Cross-platform compatibility
- It would make use of the [Blackboard REST API][blackboard-api]



**Why is my university not supported?**

Simply put, some information is necessary to make the login process compatible with any given university. If you would like to help to add support for your university, or would like to see which universities are currently supported, [start here.](UNIVERSITIES.md)



Built with:

- [Python 3.9][python]
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

Currently unavailable (until a more stable version).

Alternatively, you can run the python package [directly](#running-without-building), or build an executable yourself by following [these steps](#building-from-source).



#### Via pip

```bash
python3 -m pip install BlackboardSync
```



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

[README template by tonycrosby-tech][tonycrosby]

[README template by neildrew][neildrew]

[README guide by Rita Łyczywek][bulldogjob]



<!-- LINK REFERENCES -->

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

[releases]: https://github.com/jacobszpz/BlackboardSync/releases/


<!-- README TEMPLATES -->

[tonycrosby]: https://gist.github.com/tonycrosby-tech/c18c2b6c74900c6080fc097ca0718839	"tonycrosby-tech README template"
[neildrew]: https://github.com/othneildrew/Best-README-Template	"othneildrew README template"
[bulldogjob]: https://bulldogjob.com/news/449-how-to-write-a-good-readme-for-your-github-project	"bulldogjob README guide"



<!-- SHIELDS -->

[license-shield]: https://img.shields.io/github/license/jacobszpz/BlackboardSync
[build-shield]: https://img.shields.io/github/workflow/status/jacobszpz/BlackboardSync/Python%20CI/master
[docs-shield]: https://img.shields.io/readthedocs/BlackboardSync
[kofi-shield]: https://ko-fi.com/img/githubbutton_sm.svg
[lp-shield]: https://img.shields.io/liberapay/receives/BlackboardSync.svg?logo=liberapay



<!-- SHIELD LINKS -->

[actions]: https://github.com/jacobszpz/BlackboardSync/actions
[kofi]: https://ko-fi.com/Q5Q17XN36
[liberapay]: https://liberapay.com/BlackboardSync
