"""Shared JSDoc-prose helpers used by the jsdoc-* rules."""

import re
from collections.abc import Iterator

JSDOC_OPEN = re.compile(r"/\*\*")
JSDOC_CLOSE = re.compile(r"\*/")
JSDOC_PROSE_LINE = re.compile(r"^\s*\*\s+(?P<text>\S.*)$")
ONELINE_JSDOC = re.compile(r"/\*\*\s*(?P<text>[^*][^*]*?)\s*\*/")
TAG_LINE = re.compile(r"^@(?P<tag>\w+)\b\s*(?P<rest>.*)$")


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
