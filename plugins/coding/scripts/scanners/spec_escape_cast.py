"""TST-MOCK-09 candidate: `as unknown as` test-double casts in spec files."""

import re
from pathlib import Path

from scanlib.core import Match
from scanlib.predicates import is_spec_file
from scanlib.rule import Rule

# `escape_cast.py` deliberately skips spec files (TYP-TYPE-07 permits partial
# cast-chains in tests), but TST-MOCK-09 still forbids the `as unknown as`
# double-cast for test doubles: validate the shape with `satisfies Partial<T>`
# first. this companion rule covers spec files only — production is handled by
# `escape_cast.py` under TYP-CORE-03.
ESCAPE_CAST = re.compile(r"\bas\s+unknown\s+as\b")
# strips a trailing `//` line comment so a comment that merely *mentions* the
# pattern (e.g. `// avoid as unknown as`) is not flagged as a real cast.
LINE_COMMENT = re.compile(r"//.*$")


def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    # spec-only; the engine already gates via `applies_to`, but guard here too
    # so a stray non-spec invocation stays silent.
    if not is_spec_file(path):
        return
    for lineno, raw in enumerate(lines, start=1):
        code = LINE_COMMENT.sub("", raw)
        if ESCAPE_CAST.search(code):
            matches.append(Match(path, lineno, raw.rstrip("\n")))


RULE = Rule(
    id="spec-escape-cast",
    label="`as unknown as` test-double cast — validate with `satisfies Partial<T>` first (TST-MOCK-09)",
    scan=scan,
    order=91,
    applies_to=is_spec_file,
    rule_refs=("TST-MOCK-09",),
)
