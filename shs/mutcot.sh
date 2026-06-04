# Set the new author info
export NEW_NAME="CowMuon"
export NEW_EMAIL="mars@mlops.nyc"

# List the two commit hashes you want to change
COMMITS=("580e834" 
"7a09909" 
"44e1b64" 
"d9b5360" 
"ad1a210" 
"41bafae" 
"bca4800" 
"32c8dce"
)

git filter-branch --env-filter '
for commit in "${COMMITS[@]}"; do
  if [ $GIT_COMMIT = $commit ]
  then
    export GIT_AUTHOR_NAME="$NEW_NAME"
    export GIT_AUTHOR_EMAIL="$NEW_EMAIL"
    export GIT_COMMITTER_NAME="$NEW_NAME"
    export GIT_COMMITTER_EMAIL="$NEW_EMAIL"
  fi
done
' --tag-name-filter cat -- --all

