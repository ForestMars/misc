git filter-branch -f --env-filter '
if [ "$GIT_COMMIT" = "1bb34f1897512a73bce6d2830d481db80f1bc877" ] || \
   [ "$GIT_COMMIT" = "c65588b2dbfcde0e355943e269ea6878f14e0a37" ] || \
   [ "$GIT_COMMIT" = "c4147514855da45e2916afb098ce8e5de18ca856" ] || \
   [ "$GIT_COMMIT" = "d9b5360697d79ee39a5e6eb5619562786e1e181f" ] || \
   [ "$GIT_COMMIT" = "ad1a210754bd851475148ea52c30ff1abc27ee48" ] || \
   [ "$GIT_COMMIT" = "41bafaea2b6655bda30da1828a42962573e1e89e" ] || \
   [ "$GIT_COMMIT" = "bca4800167cb6ce4b35cc914507ea6ae00bfbd46" ] || \
   [ "$GIT_COMMIT" = "32c8dce9fa21013ed8f72b682b8d903e92c1b6f1" ]; then
    export GIT_AUTHOR_NAME="CowMuon"
    export GIT_AUTHOR_EMAIL="mars@mlops.nyc"
    export GIT_COMMITTER_NAME="CowMuon"
    export GIT_COMMITTER_EMAIL="mars@mlops.nyc"
fi
' --tag-name-filter cat -- --all









