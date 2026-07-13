#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIRECTORY="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIRECTORY/install_agents.py" "$@"
