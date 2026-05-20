"""RC-STRUCT-02 candidate: `interface XxxProps` declarations (prefer `type`)."""

import re
from pathlib import Path

from scanlib.core import Match
from scanlib.predicates import ts_only
from scanlib.rule import Rule

# RC-STRUCT-02 — `interface FooProps`
INTERFACE_PROPS = re.compile(
    r"^\s*(?:export\s+)?interface\s+(?P<name>\w+Props)\b",
    re.MULTILINE,
)


def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    text = "\n".join(lines)
    for hit in INTERFACE_PROPS.finditer(text):
        lineno = text.count("\n", 0, hit.start()) + 1
        matches.append(Match(path, lineno, lines[lineno - 1].rstrip("\n")))


RULE = Rule(
    id="props-interface",
    label="Props declared as `interface` (RC-STRUCT-02 — prefer `type`)",
    scan=scan,
    order=0,
    applies_to=ts_only,
    rule_refs=("RC-STRUCT-02",),
)
