"""TST-CORE-09 candidate: manual mock.calls[N] indexing in spec files."""

import re
from pathlib import Path

from scanlib.core import Match
from scanlib.predicates import spec_files
from scanlib.rule import Rule

# manual indexing into a mock's recorded calls, e.g. `fn.mock.calls[0]![0]` —
# the structural-assertion rules (TST-CORE-09 / TST-DATA-02) want
# `toHaveBeenCalledWith(expect.objectContaining({...}))` or
# `expect(fn.mock.calls).toEqual([...])` instead. `.mock.results[N]` is the
# sibling form for recorded return values; flag both.
MOCK_INDEX = re.compile(r"\.mock\.(?:calls|results)\[\s*\d+\s*\]")
# strips a trailing `//` line comment so a comment that merely *mentions* the
# pattern is not flagged as a real access.
LINE_COMMENT = re.compile(r"//.*$")


def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    for lineno, raw in enumerate(lines, start=1):
        code = LINE_COMMENT.sub("", raw)
        if MOCK_INDEX.search(code):
            matches.append(Match(path, lineno, raw.rstrip("\n")))


RULE = Rule(
    id="mock-calls-index",
    label="Manual mock.calls[N] indexing — prefer toHaveBeenCalledWith/objectContaining (TST-CORE-09)",
    scan=scan,
    order=126,
    applies_to=spec_files,
    rule_refs=("TST-CORE-09", "TST-DATA-02"),
)
