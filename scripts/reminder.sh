#!/usr/bin/env bash
# Shared token usage tracking and reminder utilities for Claude Code hooks

# Check token usage and generate reminder context for boundary crossings
#
# Parameters:
#   $1: session_id - The current session ID
#   $2: transcript_path - Path to the transcript JSONL file
#
# Returns:
#   Reminder context string (congratulations messages for each 25k boundary crossed)
#   Empty string if no boundaries crossed or invalid inputs
#
# Side effects:
#   Updates /tmp/claude-<session_id>.json with current token count
#   Preserves existing metadata in the session file
#
# Usage:
#   REMINDER_CONTEXT=$(check_and_remind_token_usage "$SESSION_ID" "$TRANSCRIPT_PATH")
#
check_and_remind_token_usage() {
  local session_id="$1"
  local transcript_path="$2"
  local context=""

  # Validate inputs
  if [[ -z "$transcript_path" || ! -f "$transcript_path" ]]; then
    echo -n "$context"
    return 0
  fi

  # Extract the last line of the transcript (contains usage data)
  local last_line
  last_line=$(tail -n 1 "$transcript_path")

  # Parse token usage from the usage field in the last line
  # The usage field should contain: input_tokens, cache_creation_input_tokens, cache_read_input_tokens
  # Try .message.usage first (standard Claude transcript format), then .usage as fallback
  local current_input_tokens current_cache_creation_tokens current_cache_read_tokens
  current_input_tokens=$(echo "$last_line" | jq -r '.message.usage.input_tokens // .usage.input_tokens // 0')
  current_cache_creation_tokens=$(echo "$last_line" | jq -r '.message.usage.cache_creation_input_tokens // .usage.cache_creation_input_tokens // 0')
  current_cache_read_tokens=$(echo "$last_line" | jq -r '.message.usage.cache_read_input_tokens // .usage.cache_read_input_tokens // 0')

  # Calculate total current tokens
  local current_total
  current_total=$((current_input_tokens + current_cache_creation_tokens + current_cache_read_tokens))

  # Path to session metadata file
  local metadata_file="/tmp/claude-${session_id}.json"

  # Read previous token count (default to 0 if file doesn't exist)
  local previous_total=0
  if [[ -f "$metadata_file" ]]; then
    previous_total=$(jq -r '.lastContextInjectionTokens // 0' "$metadata_file" 2>/dev/null || echo 0)
  fi

  # Check if we've crossed a 25k boundary
  local previous_boundary current_boundary
  previous_boundary=$((previous_total / 25000))
  current_boundary=$((current_total / 25000))

  if [[ $current_boundary -gt $previous_boundary ]]; then
    # Calculate how many boundaries we've crossed
    local boundaries_crossed
    boundaries_crossed=$((current_boundary - previous_boundary))

    # Create congratulations message for each boundary
    for ((i = 0; i < boundaries_crossed; i++)); do
      context+=$'== CONSTITUTION REMINDER ==\n\n'
    done
  fi

  # Update metadata file with current token count
  # Preserve existing metadata while updating token count
  local updated_metadata
  if [[ -f "$metadata_file" ]]; then
    # Merge new token count with existing metadata
    updated_metadata=$(jq --arg tokens "$current_total" '.lastContextInjectionTokens = ($tokens | tonumber)' "$metadata_file")
  else
    # Create new metadata file
    updated_metadata="{\"lastContextInjectionTokens\": $current_total}"
  fi

  # Write updated metadata atomically
  echo "$updated_metadata" | jq . > "$metadata_file.tmp"
  mv "$metadata_file.tmp" "$metadata_file"

  # Return the context string
  echo -n "$context"
}
