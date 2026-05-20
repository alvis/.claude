"""GEN candidate: `let` declarations — every match is worth a review."""

import re
from pathlib import Path

from scanlib.core import Match
from scanlib.predicates import source_files
from scanlib.rule import Rule

LET_PATTERN = re.compile(r"^\s*let\s+\w")
LET_ALLOW_COMMENT = re.compile(r"//.*eslint-disable.*prefer-const", re.IGNORECASE)


def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    for lineno, raw in enumerate(lines, start=1):
        if not LET_PATTERN.match(raw):
            continue
        if LET_ALLOW_COMMENT.search(raw):
            continue
        matches.append(Match(path, lineno, raw.rstrip("\n")))


RULE = Rule(
    id="let",
    label="`let` declarations",
    scan=scan,
    order=40,
    applies_to=source_files,
    honor_no_tests=True,
)
