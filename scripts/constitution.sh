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

# Function to search for markdown files in a specific path
search_md_files() {
  local search_path="$1"
  local subdir="$2"
  # Replace slashes with underscores for valid temp file path
  local safe_subdir="${subdir//\//_}"
  local temp_file="/tmp/claude_search_$$_${safe_subdir}.txt"

  # Clear temp file
  > "$temp_file"

  # Search only in the provided path
  if [[ -d "${search_path}/${subdir}" ]]; then
    find "${search_path}/${subdir}" -type f -name "*.md" 2>/dev/null >> "$temp_file" || true
  fi

  # Format output
  if [[ -f "$temp_file" && -s "$temp_file" ]]; then
    sort -u "$temp_file" | while IFS= read -r file; do
      if [[ -n "$file" ]]; then
        echo "  - $file"
      fi
    done
    rm -f "$temp_file"
  fi
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

  # Search for workflows
  local workflows_found=$(search_md_files "$search_path" "constitution/workflows")

  # Search for standards
  local standards_found=$(search_md_files "$search_path" "constitution/standards")

  # Search for templates
  local templates_found=$(search_md_files "$search_path" "constitution/templates")

  context+="## ${label} Constitution\n\n"

  if [[ -n "$workflows_found" ]]; then
    context+="**Workflows**:\n$workflows_found\n"
  fi

  if [[ -n "$standards_found" ]]; then
    context+="**Standards**:\n$standards_found\n"
  fi

  if [[ -n "$templates_found" ]]; then
    context+="**Templates**:\n$templates_found\n"
  fi

  echo -n "$context"
}
