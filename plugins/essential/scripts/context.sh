#!/usr/bin/env bash
# Basic context retrieval for Claude Code
# Generates session header, working directory, custom context, and environment info
# Compatible with bash 3.2+

# Get working directory context
get_working_directory_context() {
  printf '%s\n' "**Working directory**: \`$(pwd)\`"
}

get_repo_root() {
  if git rev-parse --git-dir >/dev/null 2>&1; then
    git rev-parse --show-toplevel
  else
    pwd
  fi
}

get_file_identity() {
  local path="$1"
  if stat -f '%d:%i' "$path" >/dev/null 2>&1; then
    stat -f '%d:%i' "$path"
  elif stat -c '%d:%i' "$path" >/dev/null 2>&1; then
    stat -c '%d:%i' "$path"
  else
    (cd "$(dirname "$path")" && printf '%s/%s\n' "$(pwd -P)" "$(basename "$path")")
  fi
}

get_repo_root_documents_context() {
  local repo_root="$1"
  local context=""
  local path rel name identity
  local seen_identities=$'\n'

  # Small onboarding entrypoints remain useful and are not generated work
  # state. Do not enumerate arbitrary root Markdown.
  local onboarding_groups=("README.md readme.md" "AGENTS.md" "CONTRIBUTING.md contributing.md" "SECURITY.md security.md")
  local group
  for group in "${onboarding_groups[@]}"; do
    for name in $group; do
      if [[ -f "$repo_root/$name" ]]; then
        identity="$(get_file_identity "$repo_root/$name")"
        if [[ "$seen_identities" != *$'\n'"$identity"$'\n'* ]]; then
          context+="- $name"$'\n'
          seen_identities+="$identity"$'\n'
        fi
        break
      fi
    done
  done

  # Only the explicitly active work item, or a sole unambiguous item, exposes
  # its fast pointer and state. Multiple candidates require explicit selection.
  local work_dir
  local work_candidates=()
  if [[ -n "${ENGINEERING_WORK_ID:-}" ]] &&
     [[ "$ENGINEERING_WORK_ID" =~ ^[a-z0-9]+([a-z0-9-]*[a-z0-9])?$ ]] &&
     [[ -d "$repo_root/.engineering/work/$ENGINEERING_WORK_ID" ]]; then
    work_candidates+=("$repo_root/.engineering/work/$ENGINEERING_WORK_ID")
  elif [[ -z "${ENGINEERING_WORK_ID:-}" ]]; then
    while IFS= read -r work_dir; do
      [[ -z "$work_dir" ]] && continue
      work_candidates+=("$work_dir")
    done < <(find "$repo_root/.engineering/work" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | LC_ALL=C sort)
  fi

  if [[ "${#work_candidates[@]}" -eq 1 ]]; then
    work_dir="${work_candidates[0]}"
    for name in working.md state.md; do
      path="$work_dir/$name"
      if [[ -f "$path" ]]; then
        rel="${path#"$repo_root"/}"
        context+="- $rel"$'\n'
      fi
    done
  elif [[ "${#work_candidates[@]}" -gt 1 ]]; then
    context+="- Work selection required; set ENGINEERING_WORK_ID to one of:"$'\n'
    for work_dir in "${work_candidates[@]}"; do
      rel="${work_dir#"$repo_root"/}/"
      context+="  - $rel"$'\n'
    done
  elif [[ -n "${ENGINEERING_WORK_ID:-}" ]]; then
    context+="- Work selection unavailable; set a valid existing ENGINEERING_WORK_ID."$'\n'
  fi

  # Durable entrypoints only. Their own indexes provide progressive disclosure
  # into architecture, design, and specification detail.
  if [[ -f "$repo_root/docs/index.md" ]]; then
    context+="- docs/index.md"$'\n'
  fi
  if [[ -f "$repo_root/docs/architecture/overview.md" ]]; then
    context+="- docs/architecture/overview.md"$'\n'
  fi

  if [[ -f "$repo_root/docs/design/system.md" ]]; then
    context+="- docs/design/system.md"$'\n'
  fi

  # Capability indexes are the only spec files injected at bootstrap.
  local capability_dir
  while IFS= read -r capability_dir; do
    [[ -z "$capability_dir" ]] && continue
    path="$capability_dir/index.md"
    if [[ -f "$path" ]]; then
      rel="${path#"$repo_root"/}"
      context+="- $rel"$'\n'
    fi
  done < <(find "$repo_root/docs/specs" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | LC_ALL=C sort)

  if [[ -n "$context" ]]; then
    context="## Target Repo Documents"$'\n\n'"${context}"
  fi

  printf '%s' "$context"
}

# Get environment and session info
# Parameters: $1 = session_id
get_environment_context() {
  # Detect shell and version
  local shell_path="${SHELL:-/bin/bash}"
  local shell_name
  shell_name="$(basename "$shell_path")"
  local shell_version=""

  if [[ -x "$shell_path" ]]; then
    shell_version=$("$shell_path" --version 2>&1 | head -1 || echo "version unknown")
  else
    shell_version="version unknown"
  fi

  printf '**Environment**: %s %s\n**Shell**: %s — write %s-compatible scripts\n' \
    "$(uname -s)" "$(uname -m)" "$shell_version" "$shell_name"
}

# Get agent capability signal.
# Emitted here (essential's env) because essential is the only plugin that still
# injects an environment block after the env dedup; the coding/governance hooks
# that used to carry this signal now run without --with-plugin-context.
get_agent_capabilities_context() {
  if [[ "${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-}" == "1" ]]; then
    printf '## Agent Capabilities\n\n**Agent Teams**: enabled\n'
  fi
}

# One shared pointer to the constitution standards, replacing the per-plugin
# enumeration that used to dominate the boot context. Each plugin's reference
# catalogs its own standards; the full set lives under the directory below.
get_standards_pointer_context() {
  printf '%s\n' "Standards: each plugin's \`constitution/standards/\` (cataloged in its reference)."
}

# Get all basic context in one call
# Combines working directory, custom context, and environment info
get_plugin_context() {
  local context=""
  local repo_root
  local block

  repo_root=$(get_repo_root)
  context+="$(get_working_directory_context)"$'\n\n'
  context+="$(get_environment_context)"$'\n'
  block="$(get_repo_root_documents_context "$repo_root")"
  if [[ -n "$block" ]]; then
    context+="$block"$'\n\n'
  fi
  block="$(get_agent_capabilities_context)"
  if [[ -n "$block" ]]; then
    context+="$block"$'\n\n'
  fi
  context+="$(get_standards_pointer_context)"
  printf '%s' "$context"
}
