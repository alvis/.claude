#!/usr/bin/env python3.13
"""advisory mechanical pre-pass scanner for 5 review-worthy patterns.

Categories (all opt-in via --category, default `all`):
  jsdoc-uppercase     uppercase first letter inside /** ... */ prose lines
  jsdoc-fullstop      trailing period inside /** ... */ prose lines
  test-hooks          beforeAll/afterAll/beforeEach/afterEach in *.spec.* files
  test-mock-stub      mock/stub-named identifiers in *.spec.* files
  let                 `let` declarations (any file) — every match worth review
  conditional-spread  `...(cond ? { k: v } : {})` style conditional object spread
  dynamic-import-static  dynamic `import()` with a string-literal or non-interpolated-template path (TYP-IMPT-07)
                         covers both runtime `await import('./x')` and type-position `typeof import('./x')`.
                         skips matches inside `vi.mock(...)` / `vi.hoist(...)` callbacks.

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
    "jsdoc-uppercase",
    "jsdoc-fullstop",
    "test-hooks",
    "test-mock-stub",
    "let",
    "conditional-spread",
    "dynamic-import-static",
]
CATEGORIES: tuple[Category, ...] = get_args(Category.__value__)
CATEGORY_LABELS: dict[Category, str] = {
    "jsdoc-uppercase": "JSDoc: uppercase first letter",
    "jsdoc-fullstop": "JSDoc: trailing period",
    "test-hooks": "Lifecycle hooks (beforeAll/afterAll/beforeEach/afterEach)",
    "test-mock-stub": "Mock/stub identifiers in spec files",
    "let": "`let` declarations",
    "conditional-spread": "Conditional object spread (`...(cond ? {…} : {})`)",
    "dynamic-import-static": "Dynamic `import()` with static path (TYP-IMPT-07)",
}

SOURCE_GLOBS = ("*.ts", "*.tsx", "*.js", "*.jsx", "*.mjs", "*.cjs")
SPEC_GLOBS = ("*.spec.ts", "*.spec.tsx", "*.spec.js", "*.spec.jsx",
              "*.int.spec.ts", "*.int.spec.tsx", "*.e2e.spec.ts", "*.e2e.spec.tsx")
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "coverage",
             "__pycache__", ".turbo", ".cache", "out"}

JSDOC_OPEN = re.compile(r"/\*\*")
JSDOC_CLOSE = re.compile(r"\*/")
JSDOC_PROSE_LINE = re.compile(r"^\s*\*\s+(?P<text>\S.*)$")
ONELINE_JSDOC = re.compile(r"/\*\*\s*(?P<text>[^*][^*]*?)\s*\*/")
ACRONYM_OR_PASCAL = re.compile(r"^([A-Z][A-Z0-9_]+|[A-Z][a-z]+[A-Z]\w*)\b")
TAG_LINE = re.compile(r"^@(?P<tag>\w+)\b\s*(?P<rest>.*)$")
EXAMPLE_CODE_HINT = re.compile(r"[`(){};=]")  # crude — looks like code, not prose
HOOK_PATTERN = re.compile(r"\b(beforeAll|afterAll|beforeEach|afterEach)\s*\(")
MOCK_STUB_PATTERN = re.compile(
    r"\b(?:(?!(?:setup|use)[A-Z])[A-Za-z]\w*(?:Stub|Mock)"
    r"|(?:mock|mocked|stub|stubbed|stubed)[A-Z]\w*)\b"
)
LET_PATTERN = re.compile(r"^\s*let\s+\w")
LET_ALLOW_COMMENT = re.compile(r"//.*eslint-disable.*prefer-const", re.IGNORECASE)
# matches `...(<expr> ? {…} : {})` and the inverted `...(<expr> ? {} : {…})`
# across line breaks — flags both sides of the ternary independently.
CONDITIONAL_SPREAD = re.compile(
    r"\.\.\.\s*\(\s*[^?()]+\?\s*"
    r"(?:\{[^{}]*\}\s*:\s*\{\s*\}|\{\s*\}\s*:\s*\{[^{}]*\})"
    r"\s*\)",
    re.DOTALL,
)
# TYP-IMPT-07 — see plugins/coding/constitution/standards/typescript/rules/typ-impt-07.md
# matches `import(<literal>)` where the argument is a string literal or a backtick
# template literal WITHOUT `${...}`. Catches BOTH runtime (`await import('./x')`)
# and type-position (`typeof import('./x')`, `import('./x').Foo`) usages — the regex
# doesn't care about context; the vi.mock/vi.hoist exception is applied per match.
DYNAMIC_IMPORT_STATIC = re.compile(
    r"\bimport\s*\(\s*"
    r"(?:'[^'\n]*'|\"[^\"\n]*\"|`[^`$\n]*`)"
    r"\s*\)",
)
# header for the exempted scope — `vi.mock(` or `vi.hoist(` (optional whitespace
# allowed around `.`). The trailing `(` is included so `m.end()` lands just past it.
VI_MOCK_OR_HOIST_HEAD = re.compile(r"\bvi\s*\.\s*(?:mock|hoist)\s*\(")


@dataclass(frozen=True, slots=True)
class Match:
    path: Path
    lineno: int
    line: str


def is_spec_file(path: Path, /) -> bool:
    name = path.name
    for suffix in (".spec.ts", ".spec.tsx", ".spec.js", ".spec.jsx",
                   ".int.spec.ts", ".int.spec.tsx", ".e2e.spec.ts", ".e2e.spec.tsx"):
        if name.endswith(suffix):
            return True
    return False


def iter_files(root: Path, /) -> Iterator[Path]:
    if root.is_file():
        yield root
        return
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}:
            continue
        yield path


def strip_trailing_punct(text: str, /) -> str:
    return text.rstrip()


def jsdoc_prose_lines(lines: list[str], /) -> Iterator[tuple[int, str, str | None]]:
    """yield (lineno, prose-text, current-tag-or-none) for prose inside /** ... */."""
    in_block = False
    current_tag: str | None = None
    for idx, raw in enumerate(lines, start=1):
        # one-line /** ... */ on its own line
        oneline = ONELINE_JSDOC.search(raw)
        if oneline and not in_block:
            yield idx, oneline.group("text").strip(), None
            continue
        if not in_block:
            if JSDOC_OPEN.search(raw):
                in_block = True
                current_tag = None
                # opening line could carry text after /** before *
                tail = raw.split("/**", 1)[1]
                tail = tail.split("*/", 1)[0]
                stripped = tail.strip().lstrip("*").strip()
                if stripped:
                    yield idx, stripped, None
                if JSDOC_CLOSE.search(raw):
                    in_block = False
            continue
        # in_block True
        prose_match = JSDOC_PROSE_LINE.match(raw)
        if prose_match:
            text = prose_match.group("text").strip()
            tag_match = TAG_LINE.match(text)
            if tag_match:
                current_tag = tag_match.group("tag")
                rest = tag_match.group("rest").strip()
                yield idx, text, current_tag
                # rest is the description portion; reuse same line
            else:
                yield idx, text, current_tag
        if JSDOC_CLOSE.search(raw):
            in_block = False
            current_tag = None


def description_after_tag(text: str, /) -> str:
    """for `@param userId the unique id`, return `the unique id`. for `@returns ...`, drop `@returns`."""
    tag_match = TAG_LINE.match(text)
    if not tag_match:
        return text
    rest = tag_match.group("rest").strip()
    tag = tag_match.group("tag")
    # @param/@property: skip the param name token, take the rest as description
    if tag in {"param", "property", "arg", "argument"} and rest:
        parts = rest.split(None, 1)
        if len(parts) == 2:
            return parts[1].strip()
        return ""
    return rest


def scan_jsdoc_uppercase(*, path: Path, lines: list[str], matches: list[Match]) -> None:
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


def scan_jsdoc_fullstop(*, path: Path, lines: list[str], matches: list[Match]) -> None:
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


def scan_test_hooks(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    for lineno, raw in enumerate(lines, start=1):
        if HOOK_PATTERN.search(raw):
            matches.append(Match(path, lineno, raw.rstrip("\n")))


def scan_mock_stub(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    for lineno, raw in enumerate(lines, start=1):
        if MOCK_STUB_PATTERN.search(raw):
            matches.append(Match(path, lineno, raw.rstrip("\n")))


def scan_let(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    for lineno, raw in enumerate(lines, start=1):
        if not LET_PATTERN.match(raw):
            continue
        if LET_ALLOW_COMMENT.search(raw):
            continue
        matches.append(Match(path, lineno, raw.rstrip("\n")))


def scan_conditional_spread(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    text = "\n".join(lines)
    for hit in CONDITIONAL_SPREAD.finditer(text):
        # convert byte offset to 1-based line number by counting preceding newlines
        lineno = text.count("\n", 0, hit.start()) + 1
        matches.append(Match(path, lineno, lines[lineno - 1].rstrip("\n")))


def _inside_vi_mock_or_hoist(*, text: str, pos: int) -> bool:
    """true iff `pos` lies inside an unclosed `vi.mock(` / `vi.hoist(` call.

    walks through every `vi.mock(`/`vi.hoist(` opener that appears before `pos`,
    counting parens between the opener and `pos`. since the opener's own `(` is
    consumed by the regex match (and thus excluded from the segment), we are still
    inside iff opens >= closes in the segment.
    """
    for head in VI_MOCK_OR_HOIST_HEAD.finditer(text, 0, pos):
        segment = text[head.end():pos]
        if segment.count("(") >= segment.count(")"):
            return True
    return False


def scan_dynamic_import_static(*, path: Path, lines: list[str], matches: list[Match]) -> None:
    text = "\n".join(lines)
    for hit in DYNAMIC_IMPORT_STATIC.finditer(text):
        if _inside_vi_mock_or_hoist(text=text, pos=hit.start()):
            continue
        lineno = text.count("\n", 0, hit.start()) + 1
        matches.append(Match(path, lineno, lines[lineno - 1].rstrip("\n")))


SCANNERS: dict[Category, tuple[Scanner, tuple[str, ...], bool]] = {
    "jsdoc-uppercase": (scan_jsdoc_uppercase, SOURCE_GLOBS, False),
    "jsdoc-fullstop": (scan_jsdoc_fullstop, SOURCE_GLOBS, False),
    "test-hooks": (scan_test_hooks, SPEC_GLOBS, True),
    "test-mock-stub": (scan_mock_stub, SPEC_GLOBS, True),
    "let": (scan_let, SOURCE_GLOBS, False),
    "conditional-spread": (scan_conditional_spread, SOURCE_GLOBS, False),
    "dynamic-import-static": (scan_dynamic_import_static, SOURCE_GLOBS, False),
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
    parser.add_argument("--no-tests", action="store_true",
                        help="skip *.spec.* files for the `let` category (others unaffected)")
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
                scanner, _globs, spec_only = SCANNERS[category]
                if spec_only and not is_spec_file(file_path):
                    continue
                if category == "let" and args.no_tests and is_spec_file(file_path):
                    continue
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
