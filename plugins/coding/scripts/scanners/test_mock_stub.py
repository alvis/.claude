"""TST candidate: mock/stub-named identifiers inside spec files."""

import re
from pathlib import Path

from scanlib.core import Match
from scanlib.predicates import spec_files
from scanlib.rule import Rule

MOCK_STUB_PATTERN = re.compile(
    r"\b(?:(?!(?:setup|use)[A-Z])[A-Za-z]\w*(?:Stub|Mock)"
    r"|(?:mock|mocked|stub|stubbed|stubed)[A-Z]\w*)\b"
)


def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    for lineno, raw in enumerate(lines, start=1):
        if MOCK_STUB_PATTERN.search(raw):
            matches.append(Match(path, lineno, raw.rstrip("\n")))


RULE = Rule(
    id="test-mock-stub",
    label="Mock/stub identifiers in spec files",
    scan=scan,
    order=30,
    applies_to=spec_files,
    rule_refs=("TST-STRU-01",),
)
