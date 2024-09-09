#!/bin/bash

# Extract the first argument as the DMG filename
DMG_FILENAME="$1"

# Sign App
codesign --sign "{{ title }}" --force --deep dist/*.app

# Create temporary directory
mkdir dist/bbsync_dmg

# Create symbolic link to Applications
ln -s "/Applications" "dist/bbsync_dmg/Applications"

# Copy app into temp directory
cp -R dist/*.app dist/bbsync_dmg

# Create disk image
hdiutil create -volname "{{ title }}" -srcfolder dist/bbsync_dmg -ov -format UDZO "dist/${DMG_FILENAME}.dmg"

# Sign DMG (Optional)
# codesign --sign "BlackboardSync" --force --deep "dist/${DMG_FILENAME}.dmg"
