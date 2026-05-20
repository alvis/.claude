"""File-gate predicates for rules — replace per-rule glob and suffix guards."""

from pathlib import Path

# the coding monolith iterated 6 suffixes; the react monolith only 4. the
# shared engine keeps all 6 to preserve coding byte-identity — react rules gate
# on `ts_only`/`index_files`, so the extra `.mjs`/`.cjs` files never match there.
SOURCE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
TS_SUFFIXES = {".ts", ".tsx"}
SPEC_SUFFIXES = (
    ".spec.ts",
    ".spec.tsx",
    ".spec.js",
    ".spec.jsx",
    ".int.spec.ts",
    ".int.spec.tsx",
    ".e2e.spec.ts",
    ".e2e.spec.tsx",
)
INDEX_NAMES = {"index.ts", "index.tsx"}


def is_spec_file(path: Path, /) -> bool:
    """Return whether ``path`` is a spec file by its compound suffix."""
    name = path.name
    for suffix in SPEC_SUFFIXES:
        if name.endswith(suffix):
            return True
    return False


def source_files(path: Path, /) -> bool:
    """Match any TypeScript or JavaScript source file."""
    return path.suffix.lower() in SOURCE_SUFFIXES


def spec_files(path: Path, /) -> bool:
    """Match only spec files (``*.spec.*``, ``*.int.spec.*``, ``*.e2e.spec.*``)."""
    return is_spec_file(path)


def ts_only(path: Path, /) -> bool:
    """Match only ``.ts`` / ``.tsx`` files — used by React Props rules."""
    return path.suffix.lower() in TS_SUFFIXES


def index_files(path: Path, /) -> bool:
    """Match only barrel files named ``index.ts`` / ``index.tsx``."""
    return path.name in INDEX_NAMES
