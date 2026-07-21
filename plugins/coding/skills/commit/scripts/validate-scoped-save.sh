#!/usr/bin/env bash
set -euo pipefail

# Stable allowed-tools entrypoint for the dependency-free scoped-save validator.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/validate_scoped_save.py" "$@"
