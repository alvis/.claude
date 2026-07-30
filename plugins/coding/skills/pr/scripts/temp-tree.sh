#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: temp-tree.sh open-git|open-jj <repo> <revision> | close <lease>" >&2
  exit 2
}

lease_guard() {
  local temp_root=${TMPDIR:-/tmp}
  temp_root=${temp_root%/}
  case "$1" in
    "$temp_root"/pr-tree-lease-*) ;;
    *) echo "refusing unrecognized lease: $1" >&2; exit 2 ;;
  esac
}

close_lease() {
  local lease=$1 kind repo tree lease_real tree_real
  lease_guard "$lease"
  [ -d "$lease" ] || return 0
  lease_real=$(cd "$lease" && pwd -P)
  kind=$(<"$lease/kind")
  repo=$(<"$lease/repo")
  tree=$(<"$lease/tree")
  tree_real=$(cd "$tree" && pwd -P)
  [ "$tree_real" = "$lease_real/checkout" ] || {
    echo "lease checkout escaped its root" >&2
    exit 2
  }
  case "$kind" in
    git) git -C "$repo" worktree remove --force "$tree_real" ;;
    jj) jj --repository "$repo" workspace forget "$(basename "$tree_real")" ;;
    *) echo "unknown lease kind: $kind" >&2; exit 2 ;;
  esac
  rm -rf -- "$lease_real"
}

open_tree() {
  local kind=$1 repo=$2 revision=$3 lease tree temp_root
  repo=$(cd "$repo" && pwd -P)
  temp_root=${TMPDIR:-/tmp}
  temp_root=${temp_root%/}
  lease=$(mktemp -d "$temp_root/pr-tree-lease-XXXXXX")
  tree="$lease/checkout"
  printf '%s\n' "$kind" >"$lease/kind"
  printf '%s\n' "$repo" >"$lease/repo"
  printf '%s\n' "$tree" >"$lease/tree"
  trap 'close_lease "$lease"' ERR HUP INT TERM
  case "$kind" in
    git) git -C "$repo" worktree add --detach "$tree" "$revision" >&2 ;;
    jj) jj --repository "$repo" workspace add --revision "$revision" "$tree" >&2 ;;
    *) usage ;;
  esac
  trap - ERR HUP INT TERM
  jq -n --arg lease "$lease" --arg tree "$tree" \
    '{lease:$lease, tree:$tree}'
}

case "${1:-}" in
  open-git)
    [ "$#" -eq 3 ] || usage
    open_tree git "$2" "$3"
    ;;
  open-jj)
    [ "$#" -eq 3 ] || usage
    open_tree jj "$2" "$3"
    ;;
  close)
    [ "$#" -eq 2 ] || usage
    close_lease "$2"
    ;;
  *)
    usage
    ;;
esac
