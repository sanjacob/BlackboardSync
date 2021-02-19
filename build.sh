#!/bin/bash
SRC='blackboard_sync'
pipenv run pyinstaller \
  --onefile --windowed \
  --add-data=$SRC"/qt:qt" \
  --add-data=$SRC"/assets:assets" \
  --name="BlackboardSync" \
  $SRC/start.py
