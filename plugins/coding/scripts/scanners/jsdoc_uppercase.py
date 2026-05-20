"""DOC-FORM-03 candidate: uppercase first letter inside /** ... */ prose."""

import re
from pathlib import Path

from scanlib.core import Match
from scanlib.jsdoc import description_after_tag, jsdoc_prose_lines
from scanlib.predicates import source_files
from scanlib.rule import Rule

ACRONYM_OR_PASCAL = re.compile(r"^([A-Z][A-Z0-9_]+|[A-Z][a-z]+[A-Z]\w*)\b")
EXAMPLE_CODE_HINT = re.compile(r"[`(){};=]")  # crude — looks like code, not prose


def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    for lineno, text, tag in jsdoc_prose_lines(lines):
        # Skip @example code-like lines
        if tag == "example" and EXAMPLE_CODE_HINT.search(text) and not text.startswith("@"):
            continue
        # @param is owned by DOC-FORM-04, not DOC-FORM-03
        if tag == "param" or text.startswith("@param"):
            continue
        check_text = description_after_tag(text) if text.startswith("@") else text
        if not check_text:
            continue
        first = check_text[:1]
        if not first.isalpha():
            continue
        if not first.isupper():
            continue
        if ACRONYM_OR_PASCAL.match(check_text):
            continue
        # PascalCase / acronym already filtered; flag plain Capitalized-word-then-lowercase
        if re.match(r"^[A-Z][a-z]", check_text):
            matches.append(Match(path, lineno, lines[lineno - 1].rstrip("\n")))


RULE = Rule(
    id="jsdoc-uppercase",
    label="JSDoc: uppercase first letter",
    scan=scan,
    order=0,
    applies_to=source_files,
    rule_refs=("DOC-FORM-03",),
)
