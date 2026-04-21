#!/usr/bin/env python3
"""Measure displayed character width of TOC lines in markdown documentation.

This tool enforces the non-negotiable 110-displayed-char limit on every TOC
line used by the `/coding:document` skill. Counting rules reflect how the
rendered markdown actually appears to readers.

Counting rules (authoritative):
  - `&emsp;`         -> 2 display chars (project spec).
  - `&nbsp;`         -> 1 display char.
  - `&ensp;`         -> 1 display char.
  - `[text](url)`    -> count `text` only; drop brackets, url and parens.
  - emoji / CJK wide -> 2 display chars (unicodedata east-asian W|F).
  - combining marks  -> 0 display chars (Mn | Me | Cf, covers VS16 / ZWJ).
  - other            -> 1 display char.

CLI:
  toc_width.py <file> [<file>...]    scan files, report TOC lines
  toc_width.py --line "<literal>"    measure a single literal line
  toc_width.py -                     read lines from stdin
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from typing import Iterable

# html entity replacements in display-width terms
HTML_ENTITY_WIDTHS = {
    "&emsp;": 2,
    "&nbsp;": 1,
    "&ensp;": 1,
}

# markdown inline link: [text](url) — non-greedy, single-line
MD_LINK_RE = re.compile(r"\[([^\]]*?)\]\(([^)]*?)\)")

# TOC row heuristic parts
TOC_BULLET_RE = re.compile(r"^\s*•")          # starts with a bullet (optional lead ws)
TOC_EMSP_RE = re.compile(r"&emsp;")           # uses the project separator
TOC_ANCHOR_LINK_RE = re.compile(r"\[[^\]]+\]\(#[^)]+\)")  # contains anchor link


def replace_entities(text: str) -> str:
    """Replace known HTML entities with placeholder chars preserving display width.

    We map `&emsp;` -> two U+E000 chars (Private Use Area), so later char-based
    width counting sees 2 display chars without being confused by other rules.
    """
    result = text
    # use a single-char PUA marker repeated to represent display width
    for entity, width in HTML_ENTITY_WIDTHS.items():
        result = result.replace(entity, "" * width)
    return result


def strip_link_urls(text: str) -> str:
    """Replace `[caption](url)` with just `caption`.

    This is what the reader actually sees.
    """
    return MD_LINK_RE.sub(lambda m: m.group(1), text)


def char_width(ch: str) -> int:
    """Return the display width of a single codepoint.

    Rules:
      - combining marks / variation selectors / format chars -> 0
      - east-asian wide / fullwidth -> 2
      - symbol-class codepoints above U+2000 (emoji / pictographs) -> 2,
        since unicodedata marks many emoji (e.g. 🗂, 🛡, 🧩, 🔌) as `N`arrow
        even though terminals and GitHub render them as 2 cells
      - everything else -> 1
    """
    if unicodedata.category(ch) in {"Mn", "Me", "Cf"}:
        return 0
    if unicodedata.east_asian_width(ch) in {"W", "F"}:
        return 2
    if ord(ch) >= 0x2000 and unicodedata.category(ch).startswith("S"):
        return 2
    return 1


def measure(line: str) -> int:
    """Return the display-width of a markdown TOC line."""
    # strip trailing newline but keep interior whitespace
    cleaned = line.rstrip("\n")
    # resolve links to their displayed caption first, then entities
    cleaned = strip_link_urls(cleaned)
    cleaned = replace_entities(cleaned)
    return sum(char_width(ch) for ch in cleaned)


def is_toc_line(line: str) -> bool:
    """Identify a TOC row by heuristic.

    Requires:
      (a) bullet-led (optional leading whitespace), and
      (b) contains &emsp; (project separator), and
      (c) contains at least two anchor-style markdown links (distinguishing a
          real TOC row from instructional prose that cites a single example).
    """
    if not TOC_BULLET_RE.search(line):
        return False
    if not TOC_EMSP_RE.search(line):
        return False
    if len(TOC_ANCHOR_LINK_RE.findall(line)) < 2:
        return False
    return True


def classify(width: int) -> str:
    """Return OK | TIGHT | OVER."""
    if width > 110:
        return "OVER"
    if width >= 101:
        return "TIGHT"
    return "OK"


def preview(line: str, n: int = 80) -> str:
    """Return first n chars of a line for reporting, tabs rendered as spaces."""
    squashed = line.rstrip("\n").replace("\t", " ")
    return squashed[:n]


def scan_file(path: Path) -> list[tuple[int, int, str, str]]:
    """Return list of (lineno, width, status, preview) for TOC rows in file.

    Lines inside HTML comments (<!-- ... -->) are skipped: template sample TOCs
    and instructional prose live there, never the real rendered TOC.
    """
    results: list[tuple[int, int, str, str]] = []
    in_comment = False
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            # track html comment state across lines; <!-- ... --> can span many
            cursor = 0
            stripped_line_parts: list[str] = []
            while cursor < len(line):
                if in_comment:
                    end = line.find("-->", cursor)
                    if end == -1:
                        cursor = len(line)
                    else:
                        in_comment = False
                        cursor = end + 3
                else:
                    start = line.find("<!--", cursor)
                    if start == -1:
                        stripped_line_parts.append(line[cursor:])
                        cursor = len(line)
                    else:
                        stripped_line_parts.append(line[cursor:start])
                        in_comment = True
                        cursor = start + 4
            visible = "".join(stripped_line_parts)
            if not is_toc_line(visible):
                continue
            width = measure(visible)
            results.append((lineno, width, classify(width), preview(visible)))
    return results


def report_file(path: Path, rows: Iterable[tuple[int, int, str, str]]) -> bool:
    """Print one line per TOC row. Return True if any row is OVER."""
    any_over = False
    for lineno, width, status, prev in rows:
        print(f"{path}:{lineno}\t{width}\t{status}\t{prev}")
        if status == "OVER":
            any_over = True
    return any_over


def cmd_line(literal: str) -> int:
    """Measure one literal line passed on the CLI."""
    width = measure(literal)
    status = classify(width)
    print(f"{width}\t{status}\t{preview(literal)}")
    return 0 if status != "OVER" else 1


def cmd_stdin() -> int:
    """Measure each line from stdin and print width tab status."""
    any_over = False
    for line in sys.stdin:
        width = measure(line)
        status = classify(width)
        print(f"{width}\t{status}\t{preview(line)}")
        if status == "OVER":
            any_over = True
    return 1 if any_over else 0


def cmd_files(paths: list[str]) -> int:
    """Scan each file, report TOC rows; exit 1 if any OVER."""
    any_over = False
    for raw in paths:
        path = Path(raw)
        if not path.is_file():
            print(f"skip (not a file): {path}", file=sys.stderr)
            continue
        rows = scan_file(path)
        if report_file(path, rows):
            any_over = True
    return 1 if any_over else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Measure display width of markdown TOC lines (110-char hard cap)."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--line",
        metavar="TEXT",
        help="measure a single literal line passed on the command line",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="markdown files to scan, or `-` to read lines from stdin",
    )
    args = parser.parse_args(argv)

    if args.line is not None:
        return cmd_line(args.line)

    if args.files == ["-"]:
        return cmd_stdin()

    if not args.files:
        parser.print_help()
        return 2

    return cmd_files(args.files)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
