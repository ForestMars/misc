i#!/bin/bash

# Set the new author info
NEW_NAME="CowMuon"
NEW_EMAIL="mars@mlops.nyc"

# List the commit hashes you want to change
COMMITS=("580e834" "7a09909" "44e1b64" "d9b5360" "ad1a210" "41bafae" "bca4800" "32c8dce")

# Join the commit hashes into a regex pattern
COMMITS_PATTERN="$(IFS='|'; echo "${COMMITS[*]}")"

git filter-branch --env-filter "
if echo \"$COMMITS_PATTERN\" | grep -wq \$GIT_COMMIT; then
    export GIT_AUTHOR_NAME=\"$NEW_NAME\"
    export GIT_AUTHOR_EMAIL=\"$NEW_EMAIL\"
    export GIT_COMMITTER_NAME=\"$NEW_NAME\"
    export GIT_COMMITTER_EMAIL=\"$NEW_EMAIL\"
fi
" --tag-name-filter cat -- --all
