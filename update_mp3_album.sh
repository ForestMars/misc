#!/bin/bash

# Directory where the mp3 files are located
DIR="$1"

# The album name to set
ALBUM_NAME="$2"

# Ensure both arguments are provided
if [ -z "$DIR" ] || [ -z "$ALBUM_NAME" ]; then
  echo "Usage: $0 <directory> <album_name>"
  exit 1
fi

# Check if the provided directory exists
if [ ! -d "$DIR" ]; then
  echo "Directory does not exist: $DIR"
  exit 1
fi

# Loop through all mp3 files in the directory
for file in "$DIR"/*.mp3; do
  if [ -f "$file" ]; then
    echo "Updating album name for: $file"
    eyed3 --album "$ALBUM_NAME" "$file"
  fi
done

echo "Album name update completed."

