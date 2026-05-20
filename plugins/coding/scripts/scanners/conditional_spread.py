"""FUNC-SIGN-06 candidate: `...(cond ? { k: v } : {})` conditional object spread."""

import re
from pathlib import Path

from scanlib.core import Match
from scanlib.predicates import source_files
from scanlib.rule import Rule

# matches `...(<expr> ? {…} : {})` and the inverted `...(<expr> ? {} : {…})`
# across line breaks — flags both sides of the ternary independently.
CONDITIONAL_SPREAD = re.compile(
    r"\.\.\.\s*\(\s*[^?()]+\?\s*"
    r"(?:\{[^{}]*\}\s*:\s*\{\s*\}|\{\s*\}\s*:\s*\{[^{}]*\})"
    r"\s*\)",
    re.DOTALL,
)


def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    text = "\n".join(lines)
    for hit in CONDITIONAL_SPREAD.finditer(text):
        # convert byte offset to 1-based line number by counting preceding newlines
        lineno = text.count("\n", 0, hit.start()) + 1
        matches.append(Match(path, lineno, lines[lineno - 1].rstrip("\n")))


RULE = Rule(
    id="conditional-spread",
    label="Conditional object spread (`...(cond ? {…} : {})`)",
    scan=scan,
    order=50,
    applies_to=source_files,
    rule_refs=("FUNC-SIGN-06",),
)
