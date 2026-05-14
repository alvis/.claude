#!/usr/bin/env python3.13
"""advisory mechanical pre-pass scanner for React Props review-worthy patterns.

Categories (all opt-in via --category, default `all`):
  props-interface              RC-STRUCT-02: `interface XxxProps` declarations (prefer `type`)
  props-children-inline        RC-STRUCT-03: inline `children: ReactNode` inside a Props block
                               (candidate for `PropsWithChildren<...>`)
  props-element-handrolled     RC-STRUCT-04: hand-rolled HTML attribute surface inside a Props block
                               without importing `ComponentPropsWithoutRef`/`ComponentPropsWithRef`/
                               `ComponentProps`/`HTMLAttributes` — likely should extend element props
  barrel-missing-props-reexport RC-STRUCT-05: barrel re-exports the component but not its `<Name>Props`

Output is plain text grouped by category then file, with --before/--after
context lines per match. The script always exits 0 — it is advisory, not a gate.
"""

import argparse
import re
import sys
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast, get_args

type Scanner = Callable[..., None]

type Category = Literal[
    "props-interface",
    "props-children-inline",
    "props-element-handrolled",
    "barrel-missing-props-reexport",
]
CATEGORIES: tuple[Category, ...] = get_args(Category.__value__)
CATEGORY_LABELS: dict[Category, str] = {
    "props-interface": "Props declared as `interface` (RC-STRUCT-02 — prefer `type`)",
    "props-children-inline": "Inline `children: ReactNode` in Props (RC-STRUCT-03 — use `PropsWithChildren`)",
    "props-element-handrolled": "Hand-rolled HTML attributes in Props (RC-STRUCT-04 — extend `ComponentPropsWithoutRef`)",
    "barrel-missing-props-reexport": "Barrel re-exports component but not `<Name>Props` (RC-STRUCT-05)",
}

SOURCE_GLOBS = ("*.ts", "*.tsx", "*.js", "*.jsx")
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "coverage",
             "__pycache__", ".turbo", ".cache", "out"}

# RC-STRUCT-02 — `interface FooProps`
INTERFACE_PROPS = re.compile(
    r"^\s*(?:export\s+)?interface\s+(?P<name>\w+Props)\b",
    re.MULTILINE,
)

# Header for any Props block (either `interface XProps {` or `type XProps = {`).
# We capture the opening brace position so we can balance-brace-walk to find the
# end of the block.
PROPS_BLOCK_HEAD = re.compile(
    r"(?:^|\n)\s*(?:export\s+)?"
    r"(?:interface\s+(?P<iname>\w+Props)\b[^\n{]*\{"
    r"|type\s+(?P<tname>\w+Props)\b[^\n=]*=\s*\{)",
)

# Children inline pattern: `children?: ReactNode` or `children: React.ReactNode`.
CHILDREN_INLINE = re.compile(
    r"\bchildren\??\s*:\s*(?:React\.)?ReactNode\b",
)

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


@dataclass(frozen=True, slots=True)
class Match:
    path: Path
    lineno: int
    line: str


def iter_files(root: Path, /) -> Iterator[Path]:
    if root.is_file():
        yield root
        return
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in {".ts", ".tsx", ".js", ".jsx"}:
            continue
        yield path


def _find_block_end(text: str, open_brace_pos: int) -> int:
    """given the index of the `{` opening a Props block, return the index just
    past the matching `}`. balances braces with no awareness of strings/comments
    — good enough for advisory scanning."""
    depth = 0
    i = open_brace_pos
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def _props_blocks(text: str) -> Iterator[tuple[int, int]]:
    """yield (start, end) char-offsets for every `XProps` block (type or interface)."""
    for head in PROPS_BLOCK_HEAD.finditer(text):
        # locate the `{` that ends the head — for `interface ... {` it is in
        # the matched span; for `type ... = {` likewise. Find the LAST `{`
        # within the matched span to be safe.
        span = head.group(0)
        brace_offset = span.rfind("{")
        if brace_offset == -1:
            continue
        open_pos = head.start() + brace_offset
        end_pos = _find_block_end(text, open_pos)
        yield open_pos, end_pos


def scan_props_interface(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    if path.suffix.lower() not in {".ts", ".tsx"}:
        return
    text = "\n".join(lines)
    for hit in INTERFACE_PROPS.finditer(text):
        lineno = text.count("\n", 0, hit.start()) + 1
        matches.append(Match(path, lineno, lines[lineno - 1].rstrip("\n")))


def scan_props_children_inline(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    if path.suffix.lower() not in {".ts", ".tsx"}:
        return
    text = "\n".join(lines)
    for start, end in _props_blocks(text):
        block = text[start:end]
        for hit in CHILDREN_INLINE.finditer(block):
            abs_pos = start + hit.start()
            lineno = text.count("\n", 0, abs_pos) + 1
            matches.append(Match(path, lineno, lines[lineno - 1].rstrip("\n")))


def scan_props_element_handrolled(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    if path.suffix.lower() not in {".ts", ".tsx"}:
        return
    text = "\n".join(lines)
    if ELEMENT_PROPS_IMPORTED.search(text):
        return
    for start, end in _props_blocks(text):
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


def _parse_named_specifiers(group: str) -> list[str]:
    """parse the inner names of `export { A, type B, C as D }` into a flat
    list of EXPORTED identifiers (the LHS — i.e. `A`, `B`, `D`)."""
    out: list[str] = []
    for raw in group.split(","):
        token = raw.strip()
        if not token:
            continue
        # strip leading `type ` keyword if present
        if token.startswith("type "):
            token = token[len("type "):].strip()
        # `Foo as Bar` -> exported name is `Foo` (the source-side identifier
        # determines what the barrel emits; for our match we care that
        # `<Name>Props` symbol appears at all on either side — be liberal).
        if " as " in token:
            left, right = (s.strip() for s in token.split(" as ", 1))
            out.append(left)
            out.append(right)
        else:
            out.append(token)
    return out


def scan_barrel_missing_props_reexport(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    if path.name not in {"index.ts", "index.tsx"}:
        return
    text = "\n".join(lines)

    # Collect wildcard sources — those satisfy the rule by definition.
    wildcards: set[str] = {m.group("src") for m in REEXPORT_STAR.finditer(text)}

    # Walk named re-exports, looking at their sibling source file.
    for re_match in REEXPORT_NAMED.finditer(text):
        src = re_match.group("src")
        if src in wildcards:
            continue
        names = _parse_named_specifiers(re_match.group("names"))

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


SCANNERS: dict[Category, Scanner] = {
    "props-interface": scan_props_interface,
    "props-children-inline": scan_props_children_inline,
    "props-element-handrolled": scan_props_element_handrolled,
    "barrel-missing-props-reexport": scan_barrel_missing_props_reexport,
}


def render(category: Category, *, matches: list[Match], lines_by_path: dict[Path, list[str]],
           before: int, after: int) -> str:
    out: list[str] = []
    out.append(f"=== {CATEGORY_LABELS[category]} ===")
    out.append("")
    if not matches:
        out.append("(no matches)")
        out.append("")
        return "\n".join(out)
    by_file: dict[Path, list[Match]] = {}
    for m in matches:
        by_file.setdefault(m.path, []).append(m)
    for path, items in by_file.items():
        for idx, m in enumerate(items):
            out.append(f"{path}:{m.lineno}  {m.line.strip()}")
            file_lines = lines_by_path[path]
            start = max(1, m.lineno - before)
            end = min(len(file_lines), m.lineno + after)
            for ln in range(start, end + 1):
                marker = ">" if ln == m.lineno else " "
                out.append(f"  {marker} {ln:>4}: {file_lines[ln - 1].rstrip()}")
            if idx + 1 < len(items):
                out.append("")
                out.append("  --- next match ---")
                out.append("")
        out.append("")
    return "\n".join(out)


def parse_args(argv: list[str], /) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", default=["."], help="files or directories to scan (default: cwd)")
    parser.add_argument("--category", choices=("all",) + CATEGORIES, default="all",
                        help="which scanner(s) to run (default: all)")
    parser.add_argument("--before", type=int, default=5, help="context lines before each match (default 5)")
    parser.add_argument("--after", type=int, default=10, help="context lines after each match (default 10)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    selected: tuple[Category, ...] = (
        CATEGORIES if args.category == "all" else (cast(Category, args.category),)
    )

    results: dict[Category, list[Match]] = {c: [] for c in selected}
    lines_by_path: dict[Path, list[str]] = {}

    for raw_path in args.paths:
        root = Path(raw_path)
        if not root.exists():
            print(f"warn: path not found: {root}", file=sys.stderr)
            continue
        for file_path in iter_files(root):
            text: str | None = None
            for category in selected:
                scanner = SCANNERS[category]
                if text is None:
                    try:
                        text = file_path.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        text = ""
                    lines_by_path[file_path] = text.splitlines()
                scanner(path=file_path, lines=lines_by_path[file_path], matches=results[category])

    out_chunks: list[str] = []
    summary: list[str] = []
    for category in selected:
        matches = results[category]
        out_chunks.append(render(
            category,
            matches=matches,
            lines_by_path=lines_by_path,
            before=args.before,
            after=args.after,
        ))
        files = {m.path for m in matches}
        summary.append(f"  {category}: {len(matches)} matches in {len(files)} files")

    print("\n".join(out_chunks))
    print("=== Summary ===")
    print("\n".join(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
