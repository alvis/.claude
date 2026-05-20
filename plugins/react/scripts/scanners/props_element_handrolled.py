"""RC-STRUCT-04 candidate: hand-rolled HTML attribute surface in a Props block."""

import re
from pathlib import Path

from scanlib.core import Match
from scanlib.predicates import ts_only
from scanlib.rule import Rule

from scanners._blocks import props_blocks

# Well-known HTML attribute names that, in aggregate (>=2), suggest the author
# is hand-rolling an element-attribute surface instead of extending
# `ComponentPropsWithoutRef<'tag'>`.
HTML_ATTRS = (
    "onClick", "onChange", "href", "target", "disabled", "type", "name",
    "placeholder", "role", "id", "className", "style",
)
# Match one HTML attribute key in a TS-style property line:
#   `onClick: ...`, `onClick?: ...`, `'aria-label'?: ...`, `"aria-foo": ...`
HTML_ATTR_LINE = re.compile(
    r"""(?mx)
    ^\s*
    (?:['"]?)
    (?P<attr>
        (?:""" + "|".join(re.escape(a) for a in HTML_ATTRS) + r""")
      | aria-[a-z][a-z0-9-]*
    )
    (?:['"]?)
    \??\s*:
    """,
)

# `ComponentPropsWithoutRef` / `ComponentPropsWithRef` / `ComponentProps`
# / `HTMLAttributes` imported anywhere in the file (named or namespaced React.X).
ELEMENT_PROPS_IMPORTED = re.compile(
    r"\b(?:ComponentPropsWithoutRef|ComponentPropsWithRef|ComponentProps|HTMLAttributes)\b",
)


def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    text = "\n".join(lines)
    if ELEMENT_PROPS_IMPORTED.search(text):
        return
    for start, end in props_blocks(text):
        block = text[start:end]
        hits = list(HTML_ATTR_LINE.finditer(block))
        # require >= 2 DISTINCT attribute keys
        distinct = {h.group("attr") for h in hits}
        if len(distinct) < 2:
            continue
        # flag the first occurrence (block opener line) — keeps output tidy
        abs_pos = start + hits[0].start()
        lineno = text.count("\n", 0, abs_pos) + 1
        matches.append(Match(path, lineno, lines[lineno - 1].rstrip("\n")))


RULE = Rule(
    id="props-element-handrolled",
    label="Hand-rolled HTML attributes in Props (RC-STRUCT-04 — extend `ComponentPropsWithoutRef`)",
    scan=scan,
    order=20,
    applies_to=ts_only,
    rule_refs=("RC-STRUCT-04",),
)
