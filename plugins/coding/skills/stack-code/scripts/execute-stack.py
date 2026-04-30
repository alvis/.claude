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

import restack
from lib import (
    confirm,
    emit_json,
    force_with_lease_push,
    gh,
    is_bookmark_merged,
    jj,
    jj_last_op_id,
    repo_root,
    squash_into_change,
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


def _resolve_change_id(bookmark: str, *, dry_run: bool) -> str:
    """Return the current short change_id for `bookmark` (state may be stale)."""
    res = jj(
        "log", "-r", bookmark, "--no-graph", "-T", "self.change_id().short()",
        dry_run=dry_run,
    )
    return res.stdout.strip() or "DRYRUNCHID"


def _resolve_at_change_id(*, dry_run: bool) -> str:
    """Return the current short change_id for `@` (the working-copy commit)."""
    res = jj(
        "log", "-r", "@", "--no-graph", "-T", "self.change_id().short()",
        dry_run=dry_run,
    )
    return res.stdout.strip() or "DRYRUNCHID"


def _jj_diff_paths(*, dry_run: bool) -> list[str]:
    """Return the list of paths in the current working-copy diff (empty in dry-run).

    Drives the per-bookmark idempotence guard: if a bookmark's proposal `files`
    do not intersect with these paths, the bookmark has no working-copy changes
    and the per-PR mutation is skipped (re-running with a clean working copy is
    a no-op, per the documented contract).
    """
    if dry_run:
        print("[DRY-RUN] would inspect: jj diff --name-only", file=sys.stderr)
        return []
    res = jj("diff", "--name-only")
    if res.returncode != 0:
        # Conservative fallback: empty list means the loop will skip every
        # existing bookmark, which is the safe direction (no spurious mutation).
        return []
    return [ln.strip() for ln in res.stdout.splitlines() if ln.strip()]


def _existing_pr_index(state: dict[str, Any], bookmark: str) -> int:
    """Index of `bookmark` in state['prs'], or -1 if absent."""
    for i, p in enumerate(state.get("prs", [])):
        if p.get("bookmark") == bookmark:
            return i
    return -1


def _follow_up_commit(
    bookmark: str,
    change_id: str,
    message: str,
    bm_changed_files: list[str],
    orphan_id: str,
    *,
    dry_run: bool,
) -> str:
    """`--fix-up` OFF path: append a new commit on top of the bookmark and move it forward.

    Mirrors sub-flow E in references/workflow-correct.md. Returns the new tip's change_id.

    `orphan_id` is the change that holds the user's working-copy edits BEFORE
    `jj new` was issued. After `jj new <change_id>`, jj snapshots the prior `@`
    into that orphan and creates a fresh empty `@` as the bookmark's child; the
    edits would otherwise be stranded on the orphan. We squash the bookmark's
    relevant files from the orphan into the new `@` so the follow-up commit
    actually carries the intended change. The orphan is left in place — it may
    still hold edits for OTHER bookmarks the loop will process in subsequent
    iterations.
    """
    if not bm_changed_files:
        # Defensive: caller is expected to skip in this case, but guard anyway
        # so a no-op never produces an empty follow-up commit.
        raise SystemExit(
            f"_follow_up_commit invoked for {bookmark!r} with no changed files"
        )
    # 1. start a new (empty) change descending from the bookmark's current tip.
    res = jj("new", change_id, dry_run=dry_run)
    if res.returncode != 0 and not dry_run:
        raise SystemExit(f"jj new {change_id} failed: {res.stderr.strip()}")
    # 2. carry the bookmark-relevant edits from the orphan into the new @.
    squash_args = ["squash", "--from", orphan_id, "--into", "@", "--", *bm_changed_files]
    res = jj(*squash_args, dry_run=dry_run)
    if res.returncode != 0 and not dry_run:
        raise SystemExit(
            f"jj squash --from {orphan_id} --into @ failed: {res.stderr.strip()}"
        )
    # 3. describe with conventional-commits message
    res = jj("describe", "-m", message.strip(), dry_run=dry_run)
    if res.returncode != 0 and not dry_run:
        raise SystemExit(f"jj describe failed: {res.stderr.strip()}")
    # 4. move bookmark forward to the new tip (@). After `jj new <change_id>`,
    # `@` is the freshly-created commit; `@-` would still point at the prior tip.
    res = jj("bookmark", "set", bookmark, "-r", "@", dry_run=dry_run)
    if res.returncode != 0 and not dry_run:
        raise SystemExit(f"jj bookmark set {bookmark} -r @ failed: {res.stderr.strip()}")
    # 5. fast-forward push (force-with-lease helper centralises future hardening)
    force_with_lease_push(bookmark, dry_run=dry_run)
    # 6. resolve the new tip's change_id for state persistence
    return _resolve_change_id(bookmark, dry_run=dry_run)


def execute(
    proposal: dict[str, Any],
    *,
    dry_run: bool,
    root: Path,
    fix_up: bool = False,
) -> tuple[dict[str, Any], list[str]]:
    """Materialise a stack from a proposal.

    Returns `(state, touched_unmerged_bookmarks)`. The orchestrator uses the
    second value to decide whether to invoke the mandatory post-rewrite/
    post-follow-up restack (per references/workflow-correct.md closing invariant).
    """
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
    touched_unmerged: list[str] = []

    # Idempotence contract (per references/workflow-correct.md):
    #   re-running with the same state and a clean working copy must be a no-op.
    # Compute the working-copy diff filenames ONCE up front and use them to gate
    # every per-PR mutation against the bookmark's proposal `files`.
    wc_files: set[str] = set(_jj_diff_paths(dry_run=dry_run))
    # Capture the orphan change_id (the working-copy commit that holds the
    # edits) BEFORE the loop fires `jj new` for the first time. The same orphan
    # is reused across iterations because each `jj new <bookmark>` only moves
    # `@` — the orphan persists as a regular commit until explicitly abandoned.
    # Only relevant when we'll take the follow-up path; the fix-up path squashes
    # from `@` directly so the orphan doesn't matter there.
    orphan_id: str = ""
    if not fix_up and wc_files:
        orphan_id = _resolve_at_change_id(dry_run=dry_run)

    for pr in proposal["prs"]:
        bookmark = str(pr["bookmark"])
        files = list(pr["files"])
        title = _compose_title(pr)
        # commit message subject = title verbatim; body = summary paragraph.
        # The title is already validated; we just append the body as the commit body.
        body_text = str(pr.get("summary", ""))
        msg = f"{title}\n\n{body_text}".rstrip() + "\n"

        existing_idx = _existing_pr_index(state, bookmark)
        if existing_idx >= 0:
            # Re-run path: bookmark already exists in state.
            # Idempotence guard: only mutate when the working copy actually
            # touches files that this bookmark owns. Skipping here also keeps
            # the bookmark out of `touched_unmerged_bookmarks` so restack is
            # not invoked unnecessarily.
            bm_changed_files = [f for f in files if f in wc_files]
            if not bm_changed_files:
                print(
                    f"no working-copy changes for {bookmark}; skipping",
                    file=sys.stderr,
                )
                prev_bookmark = bookmark
                continue
            if fix_up:
                # Sub-flow A/B: rewrite the existing owning change. Refuse on MERGED (sub-flow C / GIT-PR-STACK-03).
                if is_bookmark_merged(bookmark, dry_run=dry_run):
                    raise SystemExit(
                        f"refusing to --fix-up MERGED bookmark {bookmark!r} "
                        f"(GIT-PR-STACK-03); see references/workflow-correct.md "
                        f"sub-flow C (corrective PR) instead."
                    )
                # State may be stale — re-derive change_id from the bookmark itself.
                fresh_cid = _resolve_change_id(bookmark, dry_run=dry_run)
                state["prs"][existing_idx]["change_id"] = fresh_cid
                # Squash only the intersection — never the proposal's full file
                # list — so files the user did not touch are not silently moved.
                squash_into_change(fresh_cid, files=bm_changed_files, dry_run=dry_run)
                force_with_lease_push(bookmark, dry_run=dry_run)
                touched_unmerged.append(bookmark)
            else:
                # Sub-flow E: follow-up commit on top of the existing bookmark.
                tip_cid = _resolve_change_id(bookmark, dry_run=dry_run)
                new_tip = _follow_up_commit(
                    bookmark, tip_cid, msg, bm_changed_files, orphan_id,
                    dry_run=dry_run,
                )
                state["prs"][existing_idx]["change_id"] = new_tip
                touched_unmerged.append(bookmark)
            prev_bookmark = bookmark
            continue

        # New-bookmark path: unchanged from the original behaviour.
        change = _split_into_change(files, dry_run=dry_run, message=msg)
        _describe(change, msg, dry_run=dry_run)
        _bookmark(bookmark, change, dry_run=dry_run)
        _push(bookmark, dry_run=dry_run)

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

        gh_url = _open_pr(body_path, prev_bookmark, bookmark, title, dry_run=dry_run)

        entry: dict[str, Any] = {
            "n": pr["n"],
            "scope": pr.get("scope", ""),
            "bookmark": bookmark,
            "change_id": change,
            "gh_url": gh_url,
            "title": title,
            "status": "draft",
        }
        state["prs"] = [p for p in state["prs"] if p.get("n") != pr["n"]]
        state["prs"].append(entry)
        prev_bookmark = bookmark

    state["last_op_id"] = jj_last_op_id(dry_run=dry_run)
    state_save(slug, state, root=root)
    return state, touched_unmerged


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="execute a proposed stack")
    ap.add_argument("--proposal", required=True, type=Path, help="proposal JSON path; '-' for stdin")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true", help="skip confirmation (eval-only)")
    ap.add_argument(
        "--fix-up",
        action="store_true",
        default=False,
        help=(
            "on a re-run for an existing bookmark, squash working-copy edits into the "
            "bookmark's existing owning change (per GIT-PR-STACK-02) and force-with-lease "
            "push. Refuses to rewrite already-merged bookmarks (GIT-PR-STACK-03)."
        ),
    )
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

    state, touched_unmerged = execute(
        proposal, dry_run=args.dry_run, root=repo_root(), fix_up=args.fix_up,
    )

    # Mandatory post-rewrite/post-follow-up restack (references/workflow-correct.md
    # closing invariant): runs unconditionally when at least one unmerged bookmark
    # was touched. restack.run() is itself idempotent.
    restacked_downstream: list[str] = []
    if touched_unmerged:
        summary = restack.run(slug=str(state["slug"]), dry_run=args.dry_run)
        raw_restacked = summary.get("restacked_bookmarks", [])
        if isinstance(raw_restacked, list):
            restacked_downstream = [str(b) for b in raw_restacked]

    emit_json({
        "slug": state["slug"],
        "prs": [p["bookmark"] for p in state["prs"]],
        "last_op_id": state.get("last_op_id", ""),
        "fix_up": args.fix_up,
        "restacked_downstream_bookmarks": restacked_downstream,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main())
