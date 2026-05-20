"""Derive the standard rule-ID prefix whitelist from the constitution rules."""

from pathlib import Path

# fallback whitelist, used only when the rules glob yields nothing (e.g. the
# scanner runs outside the .claude repo). keep in sync with the live standards:
#   ls plugins/*/constitution/standards/*/rules/*.md
FALLBACK_PREFIXES = (
    "A11Y", "CSS", "DES", "DOC", "ERR", "FUNC", "GEN", "GIT", "LOG", "NAM",
    "PYT", "RC", "RH", "RPS", "SB", "TST", "TYP", "WT",
)


def _plugins_root() -> Path:
    """Return the `plugins/` directory containing this scanlib package."""
    # this file: plugins/coding/scripts/scanlib/prefixes.py -> parents[3] == plugins/
    return Path(__file__).resolve().parents[3]


def derive_rule_id_prefixes() -> tuple[str, ...]:
    """Return the sorted set of rule-ID prefixes found in the constitution.

    Globs `plugins/*/constitution/standards/*/rules/*.md`, takes each file
    stem's first hyphen segment uppercased (e.g. `doc-form-03` -> `DOC`).
    Falls back to the hardcoded whitelist when the glob is empty.
    """
    root = _plugins_root()
    prefixes: set[str] = set()
    for rule_file in root.glob("*/constitution/standards/*/rules/*.md"):
        prefixes.add(rule_file.stem.split("-")[0].upper())
    if not prefixes:
        return FALLBACK_PREFIXES
    return tuple(sorted(prefixes))
