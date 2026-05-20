"""React-only helpers — Props-block discovery and named-specifier parsing.

The leading underscore makes the rule loader skip this module: it exports no
``Rule``, only shared helpers consumed by the four React Props rules.
"""

import re
from collections.abc import Iterator

# Header for any Props block (either `interface XProps {` or `type XProps = {`).
# We capture the opening brace position so we can balance-brace-walk to find the
# end of the block.
PROPS_BLOCK_HEAD = re.compile(
    r"(?:^|\n)\s*(?:export\s+)?"
    r"(?:interface\s+(?P<iname>\w+Props)\b[^\n{]*\{"
    r"|type\s+(?P<tname>\w+Props)\b[^\n=]*=\s*\{)",
)


def find_block_end(text: str, open_brace_pos: int, /) -> int:
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


def props_blocks(text: str, /) -> Iterator[tuple[int, int]]:
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
        end_pos = find_block_end(text, open_pos)
        yield open_pos, end_pos


def parse_named_specifiers(group: str, /) -> list[str]:
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
