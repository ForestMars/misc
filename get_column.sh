#!/usr/bin/env bash

# Usage: ./extract_column.sh -f file.csv column_number

while getopts "f:" opt; do
  case $opt in
    f) file="$OPTARG" ;;
    *) echo "Usage: $0 -f file.csv column_number"; exit 1 ;;
  esac
done

shift $((OPTIND - 1))

col="$1"

if [[ -z "$file" || -z "$col" ]]; then
  echo "Usage: $0 -f file.csv column_number"
  exit 1
fi

# Extract column
awk -F',' -v c="$col" '{print $c}' "$file"
