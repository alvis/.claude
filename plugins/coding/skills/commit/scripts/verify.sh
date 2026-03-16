#!/usr/bin/env bash
set -euo pipefail

# verify.sh -- integrity verification + diff
# Interface:  verify.sh [repo-path]                                    # reads from checkpoint
#             verify.sh <git-tree-sha> <content-hash> [repo-path]     # manual override
# Env:        BACKUP_PATH (optional; else from checkpoint)
# Stdout:     GIT_TREE_MATCH=PASS|FAIL  CONTENT_MATCH=PASS|FAIL  POST_GIT_TREE_SHA=<hex>  POST_CONTENT_HASH=<hex>
# Exit:       0=both-pass  1=git-fail  2=content-fail  3=both-fail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$SCRIPT_DIR/common.sh"

detect_sha256

# Parse arguments: either (repo-path) or (git-tree-sha content-hash [repo-path])
BASELINE_GIT_TREE=""
BASELINE_CONTENT=""
REPO_PATH="."

if [ $# -ge 2 ] && [[ "$1" =~ ^[0-9a-f]{40}$ ]]; then
  # Manual override mode
  BASELINE_GIT_TREE="$1"
  BASELINE_CONTENT="$2"
  REPO_PATH="${3:-.}"
else
  REPO_PATH="${1:-.}"
fi

REPO_ROOT="$(cd "$REPO_PATH" && git rev-parse --show-toplevel 2>/dev/null)" \
  || die "Not a git repository: $REPO_PATH" 1

CKPT_BASE="$(checkpoint_dir "$REPO_ROOT")"
CKPT_FILE="${CKPT_BASE}/.checkpoint"

# Read checkpoint if no manual override
if [ -z "$BASELINE_GIT_TREE" ]; then
  [ -f "$CKPT_FILE" ] || die "No checkpoint found at $CKPT_FILE" 1
  while IFS='=' read -r key value; do
    case "$key" in
      GIT_TREE_SHA)  BASELINE_GIT_TREE="$value" ;;
      CONTENT_HASH)  BASELINE_CONTENT="$value" ;;
      BACKUP_PATH)   : "${BACKUP_PATH:=$value}" ;;  # env override takes precedence
      REPO_ROOT)     ;;  # already resolved above
    esac
  done < "$CKPT_FILE"
fi

[ -n "$BASELINE_GIT_TREE" ] || die "Missing baseline GIT_TREE_SHA" 1
[ -n "$BASELINE_CONTENT" ] || die "Missing baseline CONTENT_HASH" 1

# Compute current state
POST_GIT_TREE_SHA="$(cd "$REPO_ROOT" && git rev-parse HEAD^{tree} 2>/dev/null)" \
  || die "Cannot resolve HEAD^{tree}" 1
POST_CONTENT_HASH="$(compute_content_hash "$REPO_ROOT")"

# Compare
GIT_RESULT="PASS"
CONTENT_RESULT="PASS"
EXIT_CODE=0

if [ "$BASELINE_GIT_TREE" != "$POST_GIT_TREE_SHA" ]; then
  GIT_RESULT="FAIL"
  EXIT_CODE=1
fi

if [ "$BASELINE_CONTENT" != "$POST_CONTENT_HASH" ]; then
  CONTENT_RESULT="FAIL"
  if [ "$EXIT_CODE" -eq 1 ]; then
    EXIT_CODE=3
  else
    EXIT_CODE=2
  fi
fi

# Output summary
printf 'GIT_TREE_MATCH=%s\n' "$GIT_RESULT"
printf 'CONTENT_MATCH=%s\n' "$CONTENT_RESULT"
printf 'POST_GIT_TREE_SHA=%s\n' "$POST_GIT_TREE_SHA"
printf 'POST_CONTENT_HASH=%s\n' "$POST_CONTENT_HASH"

# Diff details on git tree failure
if [ "$GIT_RESULT" = "FAIL" ] && [ -n "${BACKUP_PATH:-}" ] && [ -d "${BACKUP_PATH:-}/.git" ]; then
  printf '\n--- Git Tree Diff ---\n'
  GIT_ALTERNATE_OBJECT_DIRECTORIES="$BACKUP_PATH/.git/objects" \
    git -C "$REPO_ROOT" diff-tree -r "$BASELINE_GIT_TREE" "$POST_GIT_TREE_SHA" 2>/dev/null || true
fi

# Diff details on content failure
if [ "$CONTENT_RESULT" = "FAIL" ] && [ -n "${BACKUP_PATH:-}" ] && [ -d "$BACKUP_PATH" ]; then
  printf '\n--- Content Diff ---\n'
  BASELINE_FILES="$(cd "$BACKUP_PATH" && find . -path ./.git -prune -o -type f -print | LC_ALL=C sort)"
  CURRENT_FILES="$(cd "$REPO_ROOT" && find . -path ./.git -prune -o -type f -print | LC_ALL=C sort)"

  ADDED="$(comm -13 <(printf '%s\n' "$BASELINE_FILES") <(printf '%s\n' "$CURRENT_FILES"))"
  DELETED="$(comm -23 <(printf '%s\n' "$BASELINE_FILES") <(printf '%s\n' "$CURRENT_FILES"))"
  COMMON="$(comm -12 <(printf '%s\n' "$BASELINE_FILES") <(printf '%s\n' "$CURRENT_FILES"))"

  [ -n "$ADDED" ] && printf 'ADDED:\n%s\n' "$ADDED"
  [ -n "$DELETED" ] && printf 'DELETED:\n%s\n' "$DELETED"

  # Check for changed files among common
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    if ! cmp -s "$BACKUP_PATH/$f" "$REPO_ROOT/$f"; then
      printf 'CHANGED: %s\n' "$f"
    fi
  done <<< "$COMMON"
fi

# Write verify result
cat > "${CKPT_BASE}/.verify-result" <<RESULT
GIT_TREE_MATCH=$GIT_RESULT
CONTENT_MATCH=$CONTENT_RESULT
POST_GIT_TREE_SHA=$POST_GIT_TREE_SHA
POST_CONTENT_HASH=$POST_CONTENT_HASH
RESULT

exit "$EXIT_CODE"
