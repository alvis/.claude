#!/usr/bin/env python3
"""Advisory React scanner using an explicitly supplied Coding scanlib.

Rules are auto-discovered from the sibling `scanners/` package: drop one `.py`
file exporting a `Rule` (as `RULE`) into `scanners/` and it is picked up with no
dispatcher edits. The caller supplies the installed Coding scanlib path.
"""

import argparse
import sys
from pathlib import Path

here = Path(__file__).resolve().parent  # plugins/react/scripts
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--scanlib", type=Path, required=True)
known, remaining = parser.parse_known_args()
sys.path.insert(0, str(known.scanlib.parent.resolve()))
sys.path.insert(0, str(here))  # THIS plugin's scanners must win path resolution
sys.argv = [sys.argv[0], *remaining]

from scanlib.core import run

if __name__ == "__main__":
    raise SystemExit(run())
