#!/usr/bin/env python3.13
"""advisory mechanical pre-pass scanner — thin shim over the shared scanlib engine.

Rules are auto-discovered from the sibling `scanners/` package: drop one `.py`
file exporting a `Rule` (as `RULE`) into `scanners/` and it is picked up with no
dispatcher edits. The engine, CLI, and output format live in `scanlib/`.

The script always exits 0 — it is advisory, not a gate.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scanlib.core import run

if __name__ == "__main__":
    raise SystemExit(run())
