"""RC-STRUCT-03 candidate: inline `children: ReactNode` inside a Props block."""

import re
from pathlib import Path

from scanlib.core import Match
from scanlib.predicates import ts_only
from scanlib.rule import Rule

from scanners._blocks import props_blocks

# Children inline pattern: `children?: ReactNode` or `children: React.ReactNode`.
CHILDREN_INLINE = re.compile(
    r"\bchildren\??\s*:\s*(?:React\.)?ReactNode\b",
)


def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    text = "\n".join(lines)
    for start, end in props_blocks(text):
        block = text[start:end]
        for hit in CHILDREN_INLINE.finditer(block):
            abs_pos = start + hit.start()
            lineno = text.count("\n", 0, abs_pos) + 1
            matches.append(Match(path, lineno, lines[lineno - 1].rstrip("\n")))


RULE = Rule(
    id="props-children-inline",
    label="Inline `children: ReactNode` in Props (RC-STRUCT-03 — use `PropsWithChildren`)",
    scan=scan,
    order=10,
    applies_to=ts_only,
    rule_refs=("RC-STRUCT-03",),
)
