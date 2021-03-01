set "SRC=blackboard_sync"

pipenv run pyinstaller ^
  --onefile --windowed ^
  --add-data=%SRC%"/qt;qt" ^
  --add-data=%SRC%"/assets;assets" ^
  --name="BlackboardSync" ^
  --icon=%SRC%"/assets/logo.ico" ^
  %SRC%/__main__.py
