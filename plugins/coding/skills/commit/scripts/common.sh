# common.sh -- shared utilities for commit skill scripts
# Sourced by other scripts; do not execute directly.

die() {
  local msg="${1:?}" code="${2:-1}"
  printf '%s\n' "ERROR: $msg" >&2
  exit "$code"
}

detect_sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    SHA256_CMD="sha256sum"
  elif command -v shasum >/dev/null 2>&1; then
    SHA256_CMD="shasum -a 256"
  elif command -v openssl >/dev/null 2>&1; then
    SHA256_CMD="openssl dgst -sha256 -r"
  else
    die "No SHA-256 tool found (tried sha256sum, shasum, openssl)" 4
  fi
}

sha256_hex() {
  $SHA256_CMD | sed 's/[[:space:]].*//'
}

compute_content_hash() {
  local dir="${1:?}"
  (
    cd "$dir"
    find . -path ./.git -prune -o -type f -print | LC_ALL=C sort | while IFS= read -r f; do
      printf '%s  ' "$f"
      $SHA256_CMD < "$f" | sed 's/[[:space:]].*//'
    done | sha256_hex
  )
}

checkpoint_dir() {
  local root="${1:?}"
  local name
  name="$(basename "$root")"
  printf '%s' "${TMPDIR:-/tmp}/git-backups/${name}"
}

json_field() {
  local field="${1:?}"
  if command -v jq >/dev/null 2>&1; then
    jq -r ".${field}" 2>/dev/null
  else
    sed -n 's/.*"'"$field"'"[[:space:]]*:[[:space:]]*"\{0,1\}\([^",}]*\)"\{0,1\}[,}].*/\1/p' | head -1
  fi
}
