#!/usr/bin/env python3
"""Materialise a stack from a proposal JSON.

For each PR in the proposal:
  1. `jj split` selecting the cluster's files (non-interactive)
  2. `jj describe -m <conventional-msg>`
  3. `jj bookmark set <slug>/NN-<scope>`
  4. `jj git push --bookmark <bookmark>`
  5. read `../write-pr/references/templates/pr.md`, fill placeholders, write to tmpfile
  6. `gh pr create --draft --title "<conventional-title>" --body-file <tmpfile> --base <prev_or_main>`

`--dry-run` prints the entire plan without firing subprocess (still required to
be approved before running for real, per skill contract).

Title and body are produced inline here — no shell-out to `coding:write-pr`.
The template file is the single source of truth (path resolved relative to this
script). Subjects are validated with `lib.validate_conventional_subject`; a
non-conventional subject aborts the run with a non-zero exit code.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from lib import (
    confirm,
    emit_json,
    gh,
    jj,
    jj_last_op_id,
    repo_root,
    state_load,
    state_save,
    validate_conventional_subject,
)


# Single source of truth for the unified PR body template.
TEMPLATE_PATH = (
    Path(__file__).resolve().parents[2] / "write-pr" / "references" / "templates" / "pr.md"
)


# Required placeholders always render. Optional placeholders whose value is
# empty/whitespace cause their entire `## ... <body>` section to be dropped,
# per pr.md schema. Schema-of-record lives in pr.md's leading HTML comment.
_REQUIRED_PLACEHOLDERS: tuple[str, ...] = ("summary_paragraph",)
_OPTIONAL_PLACEHOLDERS: tuple[str, ...] = (
    "context_body",
    "implementation_body",
    "breaking_changes_body",
    "related_issues_body",
    "manual_testing_body",
    "additional_notes_body",
)


def _fill_template(template: str, values: dict[str, str]) -> str:
    """Substitute `{{key}}` placeholders; drop empty optional sections.

    For each optional placeholder whose value is empty/whitespace, remove the
    enclosing `## ... <placeholder>` block (header line through the placeholder
    line, inclusive of trailing blank line) so the rendered body never carries
    stub headers.
    """
    out = template
    for key in _OPTIONAL_PLACEHOLDERS:
        token = "{{" + key + "}}"
        value = values.get(key, "")
        if value.strip():
            out = out.replace(token, value)
            continue
        # Drop the whole section: the `## ` header line preceding the token,
        # any blank lines between, the token line, and one trailing blank line.
        pattern = "## "
        idx = out.find(token)
        if idx == -1:
            continue
        header_start = out.rfind("\n## ", 0, idx)
        if header_start == -1:
            continue
        section_end = out.find("\n", idx) + 1
        # Consume one trailing blank line if present.
        if section_end < len(out) and out[section_end] == "\n":
            section_end += 1
        out = out[: header_start + 1] + out[section_end:]
    for key in _REQUIRED_PLACEHOLDERS:
        token = "{{" + key + "}}"
        out = out.replace(token, values.get(key, ""))
    return out


def _compose_body(pr: dict[str, Any], *, slug: str) -> str:
    """Build the unified PR body for one proposal entry."""
    if not TEMPLATE_PATH.is_file():
        raise SystemExit(f"PR template missing at {TEMPLATE_PATH}")
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    files = list(pr.get("files", []))
    file_lines = "\n".join(f"- `{f}`" for f in files) or "- (no file list available)"
    values: dict[str, str] = {
        "summary_paragraph": str(pr.get("summary", "")) or f"Changes under {slug}.",
        "context_body": f"Part of stack `{slug}` (PR #{pr.get('n', '??'):02d}).",
        "implementation_body": f"Files in this slice:\n\n{file_lines}",
    }
    return _fill_template(template, values)


def _compose_title(pr: dict[str, Any]) -> str:
    """Build a Conventional Commits title for one proposal entry.

    The proposal may carry an explicit `title` (e.g. set by user edits); when
    absent we synthesise `chore(<scope>): <summary>`. Either way we validate.
    """
    explicit = str(pr.get("title", "")).strip()
    if explicit:
        validate_conventional_subject(explicit)
        return explicit
    scope = str(pr.get("scope", "")).strip()
    summary = str(pr.get("summary", "")).strip() or "stacked change"
    title = f"chore({scope}): {summary}" if scope else f"chore: {summary}"
    validate_conventional_subject(title)
    return title


def _split_into_change(files: list[str], *, dry_run: bool, message: str) -> str:
    """`jj split` the listed paths off the working copy. Returns the new change_id."""
    # pass --message so jj does not open $EDITOR (micro segfaults in non-TTY harness)
    args = ["split", "--quiet", "--message", message.strip(), "--"]
    args.extend(files)
    res = jj(*args, dry_run=dry_run)
    if res.returncode != 0 and not dry_run:
        raise SystemExit(f"jj split failed: {res.stderr}")
    cid = jj("log", "-r", "@-", "--no-graph", "-T", "change_id.short()", dry_run=dry_run)
    return cid.stdout.strip() or "DRYRUNCHID"


def _describe(change: str, message: str, *, dry_run: bool) -> None:
    res = jj("describe", "-r", change, "-m", message.strip(), dry_run=dry_run)
    if res.returncode != 0 and not dry_run:
        raise SystemExit(f"jj describe failed: {res.stderr.strip()}")


def _bookmark(name: str, change: str, *, dry_run: bool) -> None:
    res = jj("bookmark", "set", name, "-r", change, dry_run=dry_run)
    if res.returncode != 0 and not dry_run:
        raise SystemExit(f"jj bookmark set failed: {res.stderr.strip()}")


def _push(name: str, *, dry_run: bool) -> None:
    res = jj("git", "push", "--bookmark", name, dry_run=dry_run)
    if res.returncode != 0 and not dry_run:
        raise SystemExit(f"jj git push failed: {res.stderr.strip()}")


def _open_pr(body_file: Path, base: str, head: str, title: str, *, dry_run: bool) -> str:
    res = gh(
        "pr",
        "create",
        "--draft",
        "--body-file",
        str(body_file),
        "--base",
        base,
        "--head",
        head,
        "--title",
        title,
        dry_run=dry_run,
    )
    if res.returncode != 0 and not dry_run:
        raise SystemExit(f"gh pr create failed: {res.stderr.strip()}")
    return res.stdout.strip()


def _print_plan(proposal: dict[str, Any]) -> None:
    print("\nPlanned stack:", file=sys.stderr)
    for pr in proposal.get("prs", []):
        print(
            f"  #{pr['n']:02d} [{pr.get('scope', ''):<20}] {pr['bookmark']}  "
            f"({len(pr['files'])} files, {pr['loc']} LOC)",
            file=sys.stderr,
        )


def execute(proposal: dict[str, Any], *, dry_run: bool, root: Path) -> dict[str, Any]:
    slug: str = proposal["slug"]
    base: str = proposal.get("base", "main@origin")
    state = state_load(slug, root=root) or {
        "slug": slug,
        "mode": "split",
        "created_at": int(time.time()),
        "base": base,
        "prs": [],
    }
    # strip jj revset suffix (e.g. "main@origin" -> "main") for `gh pr create --base`
    prev_bookmark = base.split("@", 1)[0]
    for pr in proposal["prs"]:
        files = list(pr["files"])
        title = _compose_title(pr)
        # commit message subject = title verbatim; body = summary paragraph.
        # The title is already validated; we just append the body as the commit body.
        body_text = str(pr.get("summary", ""))
        msg = f"{title}\n\n{body_text}".rstrip() + "\n"
        change = _split_into_change(files, dry_run=dry_run, message=msg)
        _describe(change, msg, dry_run=dry_run)
        _bookmark(pr["bookmark"], change, dry_run=dry_run)
        _push(pr["bookmark"], dry_run=dry_run)

        body = _compose_body(pr, slug=slug)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=f"-pr-{pr['n']:02d}.md", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(body)
            body_path = Path(tf.name)

        if dry_run:
            print(
                f"[DRY-RUN] composed PR body ({len(body)} bytes) -> {body_path}",
                file=sys.stderr,
            )

        gh_url = _open_pr(body_path, prev_bookmark, pr["bookmark"], title, dry_run=dry_run)

        entry = {
            "n": pr["n"],
            "scope": pr.get("scope", ""),
            "bookmark": pr["bookmark"],
            "change_id": change,
            "gh_url": gh_url,
            "title": title,
            "status": "draft",
        }
        state["prs"] = [p for p in state["prs"] if p.get("n") != pr["n"]]
        state["prs"].append(entry)
        prev_bookmark = pr["bookmark"]

    state["last_op_id"] = jj_last_op_id(dry_run=dry_run)
    state_save(slug, state, root=root)
    return state


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="execute a proposed stack")
    ap.add_argument("--proposal", required=True, type=Path, help="proposal JSON path; '-' for stdin")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true", help="skip confirmation (eval-only)")
    args = ap.parse_args(argv)

    raw = sys.stdin.read() if str(args.proposal) == "-" else Path(args.proposal).read_text(encoding="utf-8")
    proposal = json.loads(raw)
    _print_plan(proposal)

    # Validate every PR's title up-front so a violation aborts before any mutation.
    for pr in proposal.get("prs", []):
        _compose_title(pr)

    if not args.dry_run:
        if not (args.yes or os.environ.get("STACK_CODE_AUTO_APPROVE") == "1" or confirm("Execute this stack for real?")):
            print("aborted by user", file=sys.stderr)
            return 1

    state = execute(proposal, dry_run=args.dry_run, root=repo_root())
    emit_json({"slug": state["slug"], "prs": [p["bookmark"] for p in state["prs"]], "last_op_id": state.get("last_op_id", "")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
