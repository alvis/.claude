"""TST candidate: beforeAll/afterAll/beforeEach/afterEach hooks in spec files."""

import re
from pathlib import Path

from scanlib.core import Match
from scanlib.predicates import spec_files
from scanlib.rule import Rule

HOOK_PATTERN = re.compile(r"\b(beforeAll|afterAll|beforeEach|afterEach)\s*\(")


def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    for lineno, raw in enumerate(lines, start=1):
        if HOOK_PATTERN.search(raw):
            matches.append(Match(path, lineno, raw.rstrip("\n")))


RULE = Rule(
    id="test-hooks",
    label="Lifecycle hooks (beforeAll/afterAll/beforeEach/afterEach)",
    scan=scan,
    order=20,
    applies_to=spec_files,
    rule_refs=("TST-STRU-01",),
)
