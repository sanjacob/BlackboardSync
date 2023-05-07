BlackboardSync resides in your system tray.

In windows, this looks like:

![][tray-win] 



Initially, it may appear in the overflow menu.

![][tray-win-of]

To place it in the system tray, simply drag the icon there.



To get started, type in the details of your blackboard account. You may choose to save your login details to avoid typing them every time your session expires or you quit the application. However, be warned this will store your password in the keychain.

At any time you can keep track of the status by right-clicking on the tray icon.

Left-clicking on the icon will instead open the sync location on the file explorer.



#### Build an executable

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





<!-- MARKDOWN IMAGE REFERENCES -->

[tray-win]: screenshots/tray_win.png
[tray-win-of]: screenshots/tray_win_overflow.png
