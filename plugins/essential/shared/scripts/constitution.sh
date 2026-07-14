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

  # For plugins, check for and embed CLAUDE.md if it exists. The header names the
  # plugin (its directory basename) so that relative `references/...` pointers in
  # the embedded CLAUDE.md are unambiguous once several plugins' blocks are
  # concatenated together.
  local claude_md_path="${search_path}/CLAUDE.md"
  if [[ "$path_type" == "plugin" && -f "$claude_md_path" ]]; then
    context+="### ${search_path##*/} plugin\n\n"
    context+="$(cat "$claude_md_path")\n\n"
  fi

  # Standards are intentionally NOT enumerated here. Listing every standard for
  # every plugin dominated the injected boot context; each plugin's reference
  # now catalogs its own standards, and essential's env emits one shared pointer
  # to the standards directories (see get_standards_pointer_context). The full
  # set is read on demand from <plugin>/constitution/standards/.

  echo -n "$context"
}
