---
name: write-pr
description: 'Author a conventional-commit PR title and unified body from a jj or git change ref, emitting output for gh pr create. Use for PR descriptions, draft pull requests, stacked coding:commit PR bodies, and callers that need a unified title/body template from a commit.'
model: opus
allowed-tools: Bash(jj:*), Bash(gh:*), Bash(git:*), Read
argument-hint: "[<commit-ref>]"
---

# Write Pull Request

Compose a deterministic, regex-validated Conventional Commits PR title and a
unified PR body from one commit, emitted to stdout. Opening the PR is the
caller's job: it splits the output and pipes the body into
`gh pr create --draft --title "$TITLE" --body-file -`. Zone enforcement
(GIT-PR-SIZE-01..04) belongs to the reviewer, and the `--draft` flag
(GIT-PR-STACK-04/06) belongs to the caller — never to this author.

## Boundaries

- Use for: a PR title and body for the current jj working-copy change or any
  resolvable commit ref, including one invocation per stacked change from
  `coding:commit --create-pr`.
- Do not use for: opening the PR (the caller runs `gh pr create`), zone
  classification or review boilerplate (reviewer's job), or committing
  changes (`coding:commit`).
- Multi-template directories (`.github/PULL_REQUEST_TEMPLATE/*.md`) are
  intentionally ignored — selecting between them is a human choice and out of
  scope.

## Inputs

- **Required**: none — defaults to `@`, the current jj working-copy change.
- **Optional**: `<commit-ref>` — any jj revset (`@`, `@-`, a change id) or
  git ref (`HEAD`, `HEAD~1`, a SHA). Behavior is deterministic given the ref.
- **Prerequisites**: `jj` on PATH (falls back to `git` when `jj` is absent).
  `gh` is needed only by the caller; this skill never invokes it.

## Workflow

1. Resolve the commit ref: try `jj log -r <ref> --no-graph -T 'description'`
   first; fall back to `git log -1 --format=%B <ref>` when `jj` exits
   non-zero. Unknown ref: exit 2, print "no such revision" plus the failing
   ref. Neither `jj` nor `git` available: exit 3, "no commit source
   available".
2. Extract the subject (first non-empty line) and body (everything after the
   first blank line). Recognize commit trailers (`Refs:`, `Closes:`,
   `Fixes:`, `Breaking-Change:`, `Testing:`, `Manual-Test:`) for routing in
   step 5.
3. Validate the subject against the Conventional Commits regex — the
   canonical conventional-commits.org type allowlist with optional `(scope)`
   and `!` for breaking changes:

   ```
   ^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\([\w./-]+\))?!?: .+
   ```

   On mismatch, exit 2 with the failing token, the regex, and the offending
   subject. This skill is the single source of truth for the regex; it is
   mirrored in `coding:commit` (`references/conventional-commits.md`).
4. Resolve the template — first hit wins, paths relative to the repo root:

   1. `.github/PULL_REQUEST_TEMPLATE.md`
   2. `.github/pull_request_template.md`
   3. `docs/PULL_REQUEST_TEMPLATE.md`
   4. `docs/pull_request_template.md`
   5. `PULL_REQUEST_TEMPLATE.md`
   6. `pull_request_template.md`

   <IMPORTANT>A repo-local template is emitted verbatim — never fill
   placeholders in or otherwise mutate a foreign template; skip step 5
   entirely.</IMPORTANT> When none exist, fall back to the bundled default at
   [references/templates/pr.md](references/templates/pr.md) and continue.
   When the bundled default is also missing: exit 4, print the path that
   failed to resolve.
5. Fill the bundled default's placeholders from the commit body:
   - `{{summary_paragraph}}` — first body paragraph (≤3 sentences); fall back
     to the subject text after `: ` when the body is empty.
   - `{{context_body}}` — content under `## Context` / `Why:` /
     `Background:`, if present.
   - `{{implementation_body}}` — content under `## Implementation` / `What:`
     / `How:`, if present.
   - `{{breaking_changes_body}}` — `Breaking-Change:` trailers; "None." when
     absent.
   - `{{related_issues_body}}` — `Refs:` / `Closes:` / `Fixes:` trailers;
     "None." when absent.
   - `{{manual_testing_body}}` — `Testing:` / `Manual-Test:` trailers;
     "Covered by automated tests." when absent.
   - `{{additional_notes_body}}` — remaining unmapped body content; "None."
     when absent.

   Drop any optional section that resolves to "None." rather than leaving a
   stub — keep Summary and the Checklist only.
6. Emit the title line, a single blank line, then the Markdown body to
   stdout. Recommended caller one-liner:

   ```bash
   write-pr | { read -r TITLE; read -r _; gh pr create --draft --title "$TITLE" --body-file -; }
   ```

7. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker remains
   (for example a non-conventional subject that needs a reword by
   `coding:commit`), then report the blocker with its exit code instead of
   looping.

## Verification

- The title matches the Conventional Commits regex.
- stdout is exactly the title, one blank line, and the body — nothing else.
- A repo template was emitted byte-for-byte verbatim; a bundled default has
  no `{{placeholder}}` left unfilled and no dropped-section stubs.
- Idempotence: the same commit ref plus the same resolved template produces
  byte-identical output — no timestamps, random IDs, or diff stats.

## Completion

Report the resolved commit ref, the template used (repo path or bundled
default), the emitted title, sections dropped as empty, and the exit code:
`0` success, `2` unknown ref or non-conventional subject, `3` no commit
source available, `4` bundled default template missing. For `coding:commit
--create-pr` callers: this skill remains the single source of truth for the
default template file, the resolution order, and the title regex; the caller
consumes the `title\n\nbody` stream and runs `gh pr create` itself.
