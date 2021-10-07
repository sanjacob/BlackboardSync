Project Structure
-----------------

.. code:: bash

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
  │   │               # also offers limited functionality as a standalone script
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
  ├── README.md
  ├── CONTRIBUTING.md # Contributions policy
  └─── screenshots # Stores the screenshots shown in the README
      ├── login_win.png
      ├── settings_win.png
      ├── tray_win_open.png
      ├── tray_win_overflow.png
      └── tray_win.png
