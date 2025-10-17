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

# Get custom project context from .claude-context file
get_custom_context() {
  local context=""

  if [[ -f ".claude-context" ]]; then
    context+="### Custom Project Context\n\n"
    context+="$(cat .claude-context)\n\n"
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

  context+="\n**Environment**: $(uname -s) $(uname -m)\n"
  context+="**Shell**: $shell_name ($shell_version)\n"
  context+="**⚠️ Compatibility Note**: When writing shell scripts, ensure compatibility with $shell_name $shell_version\n"

  echo -n "$context"
}

# Get all basic context in one call
# Combines working directory, custom context, and environment info
get_plugin_context() {
  local context=""
  context+=$(get_working_directory_context)
  context+=$(get_custom_context)
  context+=$(get_environment_context)
  echo -n "$context"
}
