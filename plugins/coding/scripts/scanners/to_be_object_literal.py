"""TST-DATA-06 candidate: `.toBe({...})` / `.toBe([...])` against object/array literal."""

import re
from pathlib import Path

from scanlib.core import Match
from scanlib.predicates import spec_files
from scanlib.rule import Rule

# matches `.toBe(` immediately followed (after optional whitespace and
# newlines) by an opening `{` or `[` — the literal-shaped operand is what
# distinguishes a structural-value compare from a legitimate primitive or
# identity assertion. multi-line literals are caught via re.DOTALL so the
# opening brace/bracket may sit on a continuation line.
TO_BE_OBJECT_LITERAL = re.compile(r"\.toBe\(\s*[\{\[]", re.DOTALL)


def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    text = "\n".join(lines)
    for hit in TO_BE_OBJECT_LITERAL.finditer(text):
        # convert byte offset to 1-based line number by counting preceding newlines
        lineno = text.count("\n", 0, hit.start()) + 1
        matches.append(Match(path, lineno, lines[lineno - 1].rstrip("\n")))


RULE = Rule(
    id="to-be-object-literal",
    label="`.toBe(...)` against object/array literal (TST-DATA-06)",
    scan=scan,
    order=125,
    applies_to=spec_files,
    rule_refs=("TST-DATA-06",),
)
