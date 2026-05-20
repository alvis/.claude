"""RC-STRUCT-05 candidate: barrel re-exports component but not its `<Name>Props`."""

import re
from pathlib import Path

from scanlib.core import Match
from scanlib.predicates import index_files
from scanlib.rule import Rule

from scanners._blocks import parse_named_specifiers

# Sibling-file Props symbol detector for RC-STRUCT-05.
SIBLING_PROPS_DECL = re.compile(
    r"^\s*export\s+(?:type|interface)\s+(?P<name>\w+Props)\b",
    re.MULTILINE,
)

# Barrel re-export forms.
# Whole-namespace wildcard: `export * from './foo'` — satisfies the rule unconditionally.
REEXPORT_STAR = re.compile(
    r"""^\s*export\s*\*\s*from\s*['"](?P<src>\.\.?/[^'"]+)['"]""",
    re.MULTILINE,
)
# Named: `export { Foo, type FooProps } from './foo'` — possibly multi-line.
REEXPORT_NAMED = re.compile(
    r"""^\s*export\s+(?:type\s+)?\{(?P<names>[^}]+)\}\s*from\s*['"](?P<src>\.\.?/[^'"]+)['"]""",
    re.MULTILINE | re.DOTALL,
)


def scan(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    text = "\n".join(lines)

    # Collect wildcard sources — those satisfy the rule by definition.
    wildcards: set[str] = {m.group("src") for m in REEXPORT_STAR.finditer(text)}

    # Walk named re-exports, looking at their sibling source file.
    for re_match in REEXPORT_NAMED.finditer(text):
        src = re_match.group("src")
        if src in wildcards:
            continue
        names = parse_named_specifiers(re_match.group("names"))

        # resolve sibling: try .tsx, .ts, .jsx, .js
        sibling: Path | None = None
        base = (path.parent / src).resolve()
        for ext in (".tsx", ".ts", ".jsx", ".js"):
            candidate = base.with_suffix(ext)
            if candidate.is_file():
                sibling = candidate
                break
        if sibling is None:
            continue

        try:
            sibling_text = sibling.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        sibling_props = {m.group("name") for m in SIBLING_PROPS_DECL.finditer(sibling_text)}
        if not sibling_props:
            continue

        missing = sorted(sibling_props - set(names))
        if not missing:
            continue

        lineno = text.count("\n", 0, re_match.start()) + 1
        # decorate the line with what's missing, for human review
        line_text = lines[lineno - 1].rstrip("\n") + f"   # missing: {', '.join(missing)}"
        matches.append(Match(path, lineno, line_text))


RULE = Rule(
    id="barrel-missing-props-reexport",
    label="Barrel re-exports component but not `<Name>Props` (RC-STRUCT-05)",
    scan=scan,
    order=30,
    applies_to=index_files,
    rule_refs=("RC-STRUCT-05",),
)
