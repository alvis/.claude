"""Repo-wide pytest guard — fail loudly when the interpreter is too old.

Repo sources use Python 3.10+-only syntax such as ``dataclass(slots=True)``;
on an older interpreter, collection dies with SyntaxErrors that read like real
test failures, so refuse to start and name the fix instead.
"""

import sys

MINIMUM = (3, 10)

if sys.version_info < MINIMUM:
    raise SystemExit(
        f"this suite needs Python {MINIMUM[0]}.{MINIMUM[1]}+ but pytest is running "
        f"on {sys.version.split()[0]}; retry with `uvx --python 3.13 pytest`"
    )
