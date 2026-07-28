#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIRECTORY="$(cd "$(dirname "$0")" && pwd)"
exec uv run --python 3.13 "$SCRIPT_DIRECTORY/install_agents.py" "$@"
