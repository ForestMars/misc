#!/bin/bash

# Initialize variables
verbose=0
temp_count_file=$(mktemp)

# Check for -v flag
while getopts "v" opt; do
    case $opt in
        v) verbose=1 ;;
        ?) echo "Usage: $0 [-v]"; exit 1 ;;
    esac
done

# Store the starting directory
start_dir="$(pwd)"

# Process all epub and pdf files in all subdirectories
find . -type f \( -name "*.epub" -o -name "*.pdf" \) -print0 | while IFS= read -r -d '' file; do
    # Get the directory and filename
    dir="$(dirname "$file")"
    filename="$(basename "$file")"
    
    # Only process if the filename contains the target string
    if [[ "$filename" == *" (z-lib.org)"* ]]; then
        # Change to the directory containing the file
        if cd "$dir"; then
            new_name="${filename/ (z-lib.org)/}"
            if [ $verbose -eq 1 ]; then
                mv -v "$filename" "$new_name"
            else
                mv "$filename" "$new_name" >/dev/null 2>&1
            fi
            # Increment counter in the temp file
            echo 1 >> "$temp_count_file"
            # Return to the starting directory
            cd "$start_dir" || exit 1
        else
            echo "Failed to enter directory: $dir" >&2
        fi
    fi
done

# Count the number of lines in the temp file to get total updates
updated_files=$(wc -l < "$temp_count_file")
rm "$temp_count_file"

# Print final report
echo "Updated $updated_files files"