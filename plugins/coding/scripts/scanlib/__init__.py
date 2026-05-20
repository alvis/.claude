"""Shared standard-violation scanner engine.

Canonical home: the coding plugin. The react plugin imports this package
cross-plugin via sys.path. Rule modules live in a sibling ``scanners`` package
and are auto-discovered by :func:`scanlib.loader.load_rules`.
"""

from scanlib.core import Match, run
from scanlib.predicates import (
    index_files,
    python_files,
    source_files,
    spec_files,
    ts_only,
)
from scanlib.rule import Rule

__all__ = (
    "Match",
    "Rule",
    "index_files",
    "python_files",
    "run",
    "source_files",
    "spec_files",
    "ts_only",
)
