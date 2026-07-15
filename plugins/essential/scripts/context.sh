#!/usr/bin/env bash
# Basic context retrieval for Claude Code
# Generates session header, working directory, custom context, and environment info
# Compatible with bash 3.2+

# Get working directory context
get_working_directory_context() {
  local context=""
  context+="**Working directory**: \`$(pwd)\`\n\n"
  echo -n "$context"
}

get_repo_root() {
  if git rev-parse --git-dir >/dev/null 2>&1; then
    git rev-parse --show-toplevel
  else
    pwd
  fi
}

get_repo_root_documents_context() {
  local repo_root="$1"
  local context=""
  local docs=(
    "CONTEXT.md"
    "DESIGN.md"
    "PLAN.md"
    "NOTES.md"
    "REQUIREMENTS.md"
    "DATA.md"
    "UI.md"
    "REFERENCE.md"
  )
  local doc

  for doc in "${docs[@]}"; do
    if [[ -f "$repo_root/$doc" ]]; then
      context+="- $repo_root/$doc\n"
    fi
  done

  if [[ -n "$context" ]]; then
    context="## Target Repo Documents\n\n${context}\n"
  fi

  echo -n "$context"
}

# Get environment and session info
# Parameters: $1 = session_id
get_environment_context() {
  local context=""

  # Detect shell and version
  local shell_path="${SHELL:-/bin/bash}"
  local shell_name=$(basename "$shell_path")
  local shell_version=""

  if [[ -x "$shell_path" ]]; then
    shell_version=$("$shell_path" --version 2>&1 | head -1 || echo "version unknown")
  else
    shell_version="version unknown"
  fi

  context+="**Environment**: $(uname -s) $(uname -m)\n"
  context+="**Shell**: $shell_version — write $shell_name-compatible scripts\n"

  echo -n "$context"
}

# Get agent capability signal.
# Emitted here (essential's env) because essential is the only plugin that still
# injects an environment block after the env dedup; the coding/governance hooks
# that used to carry this signal now run without --with-plugin-context.
get_agent_capabilities_context() {
  if [[ "${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-}" == "1" ]]; then
    echo -n "## Agent Capabilities\n\n**Agent Teams**: enabled\n"
  fi
}

# One shared pointer to the constitution standards, replacing the per-plugin
# enumeration that used to dominate the boot context. Each plugin's reference
# catalogs its own standards; the full set lives under the directory below.
get_standards_pointer_context() {
  echo -n "Standards: each plugin's \`constitution/standards/\` (cataloged in its reference).\n"
}

# Get all basic context in one call
# Combines working directory, custom context, and environment info
get_plugin_context() {
  local context=""
  local repo_root

  repo_root=$(get_repo_root)
  context+=$(get_working_directory_context)
  context+=$(get_environment_context)
  context+=$(get_repo_root_documents_context "$repo_root")
  context+=$(get_agent_capabilities_context)
  context+=$(get_standards_pointer_context)
  echo -n "$context"
}
