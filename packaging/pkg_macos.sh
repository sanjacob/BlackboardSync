#!/bin/bash

# Extract the first argument as the DMG filename
DMG_FILENAME="$1"

# Fix issue with PyQt WebView code signing
# See pyinstaller/pyinstaller#6612 and thanks to @rokm
cd dist/BBSync.app/Contents/MacOS
mv PyQt5/ ../Resources/
ln -s ../Resources/PyQt5 .
cd ../Resources/
ln -s ../MacOS/Qt* .
cd ../../../..

# Sign App
codesign --sign "BlackboardSync" --force --deep dist/BBSync.app

# Create temporary directory
mkdir dist/bbsync_dmg

# Create symbolic link to Applications
ln -s "/Applications" "dist/bbsync_dmg/Applications"

# Copy app into temp directory
cp -R dist/BBSync.app dist/bbsync_dmg

# Create disk image
hdiutil create -volname "Blackboard Sync" -srcfolder dist/bbsync_dmg -ov -format UDZO "dist/${DMG_FILENAME}.dmg"

# Sign DMG (Optional)
# codesign --sign "BlackboardSync" --force --deep "dist/${DMG_FILENAME}.dmg"
