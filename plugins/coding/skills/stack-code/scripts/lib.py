#!/usr/bin/env python3
"""Shared helpers for stack-code scripts.

NOTE: stdlib only. mypy --strict clean. Every subprocess goes through `run` so
`--dry-run` is honoured uniformly across the skill.

Bookmark naming is `<slug>/NN-<scope>` per `GIT-PR-STACK-01`. The PR-type
taxonomy is gone; bookmark scopes derive from the commit's conventional-commit
scope or the cluster's path prefix.

Title validation enforces the Conventional Commits allowlist:
    build | chore | ci | docs | feat | fix | perf | refactor | revert | style | test
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Literal, Sequence

Mode = Literal["create", "split"]

STATE_DIR_REL: Final[str] = ".jj/stack-code"

# Conventional Commits — canonical allowlist (conventional-commits.org).
CONVENTIONAL_TYPES: Final[tuple[str, ...]] = (
    "build",
    "chore",
    "ci",
    "docs",
    "feat",
    "fix",
    "perf",
    "refactor",
    "revert",
    "style",
    "test",
)

CONVENTIONAL_SUBJECT_RE: Final[re.Pattern[str]] = re.compile(
    r"^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)"
    r"(\([\w./-]+\))?!?: .+"
)


@dataclass(frozen=True)
class RunResult:
    returncode: int
    stdout: str
    stderr: str


def run(cmd: Sequence[str], *, dry_run: bool = False, cwd: Path | None = None) -> RunResult:
    """subprocess.run wrapper. In dry-run, prints the planned command and stubs success."""
    if dry_run:
        print(f"[DRY-RUN] would run: {' '.join(cmd)}", file=sys.stderr)
        return RunResult(returncode=0, stdout="[DRY-RUN]\n", stderr="")
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        return RunResult(returncode=127, stdout="", stderr=f"{exc}\n")
    return RunResult(returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


def jj(*args: str, dry_run: bool = False, cwd: Path | None = None) -> RunResult:
    return run(["jj", *args], dry_run=dry_run, cwd=cwd)


def gh(*args: str, dry_run: bool = False, cwd: Path | None = None) -> RunResult:
    return run(["gh", *args], dry_run=dry_run, cwd=cwd)


def has_executable(name: str) -> bool:
    for d in os.environ.get("PATH", "").split(os.pathsep):
        if d and (Path(d) / name).is_file() and os.access(Path(d) / name, os.X_OK):
            return True
    return False


def repo_root(cwd: Path | None = None) -> Path:
    res = run(["git", "rev-parse", "--show-toplevel"], cwd=cwd)
    if res.returncode == 0 and res.stdout.strip():
        return Path(res.stdout.strip())
    return Path(cwd or Path.cwd()).resolve()


def state_dir(root: Path | None = None) -> Path:
    base = root or repo_root()
    return base / STATE_DIR_REL


def state_path(slug: str, root: Path | None = None) -> Path:
    return state_dir(root) / f"{slug}.json"


def state_load(slug: str, *, root: Path | None = None) -> dict[str, Any]:
    p = state_path(slug, root)
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def state_save(slug: str, state: dict[str, Any], *, root: Path | None = None) -> Path:
    d = state_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    p = state_path(slug, root)
    p.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return p


_SLUG_RE: Final[re.Pattern[str]] = re.compile(r"[^a-z0-9]+")


def slug_derive(text: str) -> str:
    """Kebab-case slug, max 40 chars, no leading/trailing dashes."""
    s = _SLUG_RE.sub("-", text.lower()).strip("-")
    return s[:40].strip("-") or "stack"


_SCOPE_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9][a-z0-9._/-]*$")


def bookmark_name(slug: str, n: int, scope: str) -> str:
    """Format `<slug>/NN-<scope>` per GIT-PR-STACK-01.

    `scope` is the commit's conventional-commit scope (or a sanitised path
    prefix). It must be lower-case slug-safe; raises ValueError otherwise.
    """
    if not _SCOPE_RE.match(scope):
        raise ValueError(f"invalid bookmark scope {scope!r} (expect kebab-case)")
    return f"{slug}/{n:02d}-{scope}"


def validate_conventional_subject(subject: str) -> None:
    """Raise ValueError if `subject` does not match the conventional-commits allowlist.

    Mirrors the regex documented in `coding:write-pr` SKILL.md so both skills
    enforce identical rules.
    """
    if not CONVENTIONAL_SUBJECT_RE.match(subject.strip()):
        raise ValueError(
            "subject does not match conventional-commits regex\n"
            f"  regex:   {CONVENTIONAL_SUBJECT_RE.pattern}\n"
            f"  subject: {subject!r}\n"
            f"  allowed: {', '.join(CONVENTIONAL_TYPES)}"
        )


def cluster_by_path(paths: Sequence[str], *, depth: int = 2) -> dict[str, list[str]]:
    """Group paths by their top-N segment prefix. Files at root cluster under '.'."""
    out: dict[str, list[str]] = {}
    for p in paths:
        parts = p.split("/")
        key = "/".join(parts[: max(1, depth - 1)]) if len(parts) > 1 else "."
        out.setdefault(key, []).append(p)
    return out


def split_test_paths(paths: Sequence[str]) -> tuple[list[str], list[str]]:
    """Separate test files from implementation files (kept together per GIT-PR-SIZE-01 edge cases)."""
    tests: list[str] = []
    impl: list[str] = []
    for p in paths:
        if re.search(r"(\.spec|\.test|_test|/__tests__/)", p):
            tests.append(p)
        else:
            impl.append(p)
    return impl, tests


def jj_diff_stats(*, dry_run: bool = False) -> tuple[list[str], int]:
    """Return (changed_files, total_loc) using `jj diff --git`, falling back to `git diff HEAD`."""
    res = jj("diff", "--git", dry_run=dry_run)
    diff = res.stdout
    if res.returncode != 0 or not diff:
        res = run(["git", "diff", "HEAD"], dry_run=dry_run)
        diff = res.stdout
    files: list[str] = []
    loc = 0
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                files.append(parts[3].removeprefix("b/"))
        elif line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
            loc += 1
    return files, loc


def jj_diff_files(*, dry_run: bool = False) -> list[str]:
    """Return list of changed paths via `jj diff --name-only`, falling back to git."""
    res = jj("diff", "--name-only", dry_run=dry_run)
    if res.returncode != 0 or not res.stdout:
        res = run(["git", "diff", "HEAD", "--name-only"], dry_run=dry_run)
    return [ln.strip() for ln in res.stdout.splitlines() if ln.strip()]


def jj_last_op_id(*, dry_run: bool = False) -> str:
    """Capture the latest jj operation id for rollback (`jj op restore <id>`)."""
    res = jj("op", "log", "-n1", "--no-graph", "-T", "self.id().short()", dry_run=dry_run)
    return res.stdout.strip() or ""


def derive_scope_from_paths(paths: Sequence[str]) -> str:
    """Best-effort scope derivation from a cluster's paths.

    Returns the most common second path segment (or the first segment for
    single-segment paths), sanitised to a kebab-case slug. Falls back to
    "core" when nothing else is available.
    """
    counts: dict[str, int] = {}
    for p in paths:
        parts = [seg for seg in p.split("/") if seg]
        if not parts:
            continue
        candidate = parts[1] if len(parts) >= 2 else parts[0]
        candidate = re.sub(r"\.[^./]+$", "", candidate)  # strip extension
        candidate = slug_derive(candidate)
        if candidate:
            counts[candidate] = counts.get(candidate, 0) + 1
    if not counts:
        return "core"
    return max(counts.items(), key=lambda kv: (kv[1], kv[0]))[0]


def commit_message(conv_type: str, summary: str, *, scope: str | None = None, body: str = "") -> str:
    """Compose a Conventional Commits message.

    `conv_type` MUST be one of `CONVENTIONAL_TYPES`. Use `feat!` style breaking
    markers by passing the trailing `!` inside `summary`'s caller; this helper
    keeps the type clean.
    """
    if conv_type not in CONVENTIONAL_TYPES:
        raise ValueError(
            f"unknown conventional type {conv_type!r}; "
            f"allowed: {', '.join(CONVENTIONAL_TYPES)}"
        )
    head = f"{conv_type}({scope}): {summary}" if scope else f"{conv_type}: {summary}"
    validate_conventional_subject(head)
    return f"{head}\n\n{body}".rstrip() + "\n"


def confirm(prompt: str) -> bool:
    """User confirmation. STACK_CODE_AUTO_APPROVE=1 skips prompts (evals only)."""
    if os.environ.get("STACK_CODE_AUTO_APPROVE") == "1":
        print(f"[auto-approve] {prompt}", file=sys.stderr)
        return True
    if not sys.stdin.isatty():
        return False
    try:
        ans = input(f"{prompt} [y/N] ").strip().lower()
    except EOFError:
        return False
    return ans in {"y", "yes"}


def emit_json(obj: Any) -> None:
    """Print a JSON object to stdout for caller consumption."""
    json.dump(obj, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
