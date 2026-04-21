#!/usr/bin/env bash
# Constitution context retrieval for Claude Code
# Searches for workflows and standards in a specified directory
# Compatible with bash 3.2+

# Determine path type based on the search path
# Returns: "plugin", "user", or "project"
get_path_type() {
  local search_path="$1"

  if [[ "$search_path" == *"/plugins/"* ]]; then
    echo "plugin"
  elif [[ "$search_path" == "$HOME/.claude"* ]]; then
    echo "user"
  else
    echo "project"
  fi
}

# Get first-level standard entries for a specific constitution path.
# Directories are rendered by name only, while top-level markdown files keep
# their .md extension.
get_first_level_standard_entries() {
  local search_path="$1"
  local standards_dir="${search_path}/constitution/standards"
  local temp_file="/tmp/claude_standards_$$_$(basename "$search_path").txt"

  if [[ ! -d "$standards_dir" ]]; then
    return
  fi

  > "$temp_file"

  find "$standards_dir" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null >> "$temp_file" || true
  find "$standards_dir" -mindepth 1 -maxdepth 1 -type f -name "*.md" -exec basename {} \; 2>/dev/null >> "$temp_file" || true

  if [[ -s "$temp_file" ]]; then
    sort -u "$temp_file" | while IFS= read -r entry; do
      if [[ -n "$entry" ]]; then
        echo "- $entry"
      fi
    done
  fi

  rm -f "$temp_file"
}

# Get constitution context (workflows and standards) from a specific path
# Parameters: $1 = search_path (e.g., /path/to/.claude or /path/to/plugins/coding)
get_constitution_context() {
  local search_path="$1"
  local context=""

  # Skip if path doesn't exist
  if [[ ! -d "$search_path" ]]; then
    return
  fi

  # Determine path type
  local path_type=$(get_path_type "$search_path")
  local label=""
  case "$path_type" in
    plugin)
      label="Plugin"
      ;;
    user)
      label="User"
      ;;
    project)
      label="Project"
      ;;
  esac

  # For plugins, check for and embed CLAUDE.md if it exists
  local claude_md_path="${search_path}/CLAUDE.md"
  if [[ "$path_type" == "plugin" && -f "$claude_md_path" ]]; then
    context+="### ${label} Instructions\n\n"
    context+="$(cat "$claude_md_path")\n\n"
  fi

  local standards_found=$(get_first_level_standard_entries "$search_path")

  if [[ -n "$standards_found" ]]; then
    context+="## ${label} Constitution\n\n"
    context+="Root Path: ${search_path}/constitution/standards/\n"
    context+="$standards_found\n"
  fi

  echo -n "$context"
}
