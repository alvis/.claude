#!/usr/bin/env python3.13
"""advisory React-Props pre-pass scanner — thin shim over the shared scanlib engine.

Rules are auto-discovered from the sibling `scanners/` package: drop one `.py`
file exporting a `Rule` (as `RULE`) into `scanners/` and it is picked up with no
dispatcher edits. The shared engine lives in the coding plugin's `scanlib/`
package; this shim adds that directory to `sys.path` and imports it cross-plugin.

If the coding plugin is absent the scanner degrades gracefully (exit 0) — it is
advisory and must never block.
"""

import sys
from pathlib import Path

here = Path(__file__).resolve().parent  # plugins/react/scripts
coding = here.parent.parent / "coding" / "scripts"
sys.path.insert(0, str(coding))  # shared scanlib source
sys.path.insert(0, str(here))  # THIS plugin's scanners must win path resolution

try:
    from scanlib.core import run
except ModuleNotFoundError:
    print("warn: shared scanlib not found (coding plugin missing) — skipping", file=sys.stderr)
    raise SystemExit(0)  # advisory: never block

if __name__ == "__main__":
    raise SystemExit(run())
