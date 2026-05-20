"""DOC-FORM-03 candidate: trailing period inside /** ... */ prose."""

import re
from pathlib import Path

from scanlib.core import Match
from scanlib.jsdoc import description_after_tag, jsdoc_prose_lines
from scanlib.predicates import source_files
from scanlib.rule import Rule

EXAMPLE_CODE_HINT = re.compile(r"[`(){};=]")  # crude — looks like code, not prose


def strip_trailing_punct(text: str, /) -> str:
    return text.rstrip()


def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    for lineno, text, tag in jsdoc_prose_lines(lines):
        if tag == "example" and EXAMPLE_CODE_HINT.search(text):
            continue
        check_text = description_after_tag(text) if text.startswith("@") else text
        if not check_text:
            continue
        stripped = strip_trailing_punct(check_text)
        if stripped.endswith("."):
            # ignore "..." ellipsis and "e.g." style abbreviations
            if stripped.endswith("...") or stripped.endswith("e.g.") or stripped.endswith("i.e."):
                continue
            matches.append(Match(path, lineno, lines[lineno - 1].rstrip("\n")))


RULE = Rule(
    id="jsdoc-fullstop",
    label="JSDoc: trailing period",
    scan=scan,
    order=10,
    applies_to=source_files,
    rule_refs=("DOC-FORM-03",),
)
