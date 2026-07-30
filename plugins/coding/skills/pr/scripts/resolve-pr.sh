#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: resolve-pr.sh <pr-number-or-url> [--repo <owner/name>]" >&2
  exit 2
}

[ "$#" -eq 1 ] || [ "$#" -eq 3 ] || usage
pr_input=$1
repo_args=()
if [ "$#" -eq 3 ]; then
  [ "$2" = "--repo" ] || usage
  repo_args=(--repo "$3")
fi

metadata=$(gh pr view "$pr_input" "${repo_args[@]}" \
  --json number,url,title,body,state,isDraft,baseRefName,baseRefOid,\
headRefName,headRefOid,headRepositoryOwner,changedFiles,additions,deletions,\
author,statusCheckRollup)
url=$(jq -r .url <<<"$metadata")
case "$url" in
  https://github.com/*/*/pull/[0-9]*) ;;
  *) echo "unrecognized canonical PR URL: $url" >&2; exit 2 ;;
esac

path=${url#https://github.com/}
repository=${path%/pull/*}
owner=${repository%%/*}
repo=${repository#*/}

jq --arg owner "$owner" --arg repo "$repo" \
  '. + {owner:$owner, repo:$repo}' <<<"$metadata"
