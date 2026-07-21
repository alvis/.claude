#!/usr/bin/env bash
# Deprecated compatibility entrypoint. Despite its historical name, this must
# never stamp transport-owned Notion revision metadata.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "deprecated: stamp-last-edited.sh is read-only; use validate-transport-metadata.sh" >&2
exec bash "$script_dir/validate-transport-metadata.sh" "$@"
