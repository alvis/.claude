---
name: write-pr
description: 'Author conventional-commit PR titles and unified PR bodies from a `jj`/`git` change ref, emit to stdout for the caller to pipe into `gh pr create`. Triggers when: "write a PR description", "draft a pull request", "open a PR for this", "generate PR body". Also use when: stack-code needs a PR body for a stacked change, or any caller needs a conventional-title + unified-template body from a commit. Examples: "write a PR for this implementation", "draft a PR body for change @-", "open a draft PR for the current jj change".'
model: opus
allowed-tools: Bash(jj:*), Bash(gh:*), Bash(git:*), Read
argument-hint: [<commit-ref>]
---

# Write Pull Request

Compose a conventional-commit PR title and a unified PR body for a single commit (working-copy `jj` change by default, or any `<commit-ref>` resolvable by `jj log` / `git log`). Output the title + body to stdout; the caller pipes the body into `gh pr create --draft --title "$TITLE" --body-file -`.

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Produce a single, consistent PR title (Conventional Commits) plus a single unified PR body (one Markdown template at `references/templates/pr.md`) from one commit's subject + body trailers. No type taxonomy, no zone classifier, no Python scripts.

**When to use**:
- A human asks for a PR title + body for the current `jj` change or a referenced commit.
- The sibling `coding:stack-code` skill needs the unified template content per stacked PR (it inlines the same logic in `execute-stack.py`).
- Any caller wants a deterministic, conventional-commit-validated title and a placeholder-filled body before opening a PR.

**Prerequisites**:
- `jj` CLI on PATH for change extraction (falls back to `git` when `jj` is absent).
- `gh` CLI only required by the *caller* if they choose to open the PR via `gh pr create`. This skill itself does not invoke `gh`.

### Your Role

You are a **PR Author** who reads one commit, validates its subject against the Conventional Commits regex, and fills `references/templates/pr.md` with the commit's narrative content. You do not classify zones, do not append review boilerplate, and do not merge with repo-local PR templates — zone enforcement lives in `GIT-PR-SIZE-01..04` (reviewer's job, not the author's).

## 2. SKILL OVERVIEW

### Inputs

#### Required Inputs

- **Commit reference** (positional, optional): Any `jj` revset (e.g. `@`, `@-`, a change id) or `git` ref (e.g. `HEAD`, `HEAD~1`, a SHA). Defaults to `@` (current `jj` working-copy change) when omitted.

#### Optional Inputs

- None. Behaviour is deterministic given the commit ref.

#### Expected Outputs

- **stdout** — exactly two blocks separated by a single blank line:
  1. The conventional-commit **title** (one line, regex-validated).
  2. The unified **body** Markdown (template at `references/templates/pr.md` with placeholders filled).

The caller is responsible for splitting the two and piping the body into `gh pr create`. Recommended one-liner:

```bash
write-pr | { read -r TITLE; read -r _; gh pr create --draft --title "$TITLE" --body-file -; }
```

#### Data Flow Summary

The skill resolves the supplied (or default `@`) commit ref via `jj`/`git`, validates the subject against the Conventional Commits regex, then fills the unified `references/templates/pr.md` placeholders from commit body trailers. The result is a single deterministic stdout stream: title line, blank line, then the filled Markdown body — ready for the caller to pipe into `gh pr create`.

### Conventional Commits Title

Title MUST match:

```
^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\([\w./-]+\))?!?: .+
```

Allowlisted types: `build | chore | ci | docs | feat | fix | perf | refactor | revert | style | test` (the canonical conventional-commits.org set). Optional `(scope)` and `!` for breaking changes.

If the commit subject does not match, exit non-zero with a clear error: which token failed, the regex, and the offending subject.

### Contract with Caller (`stack-code`)

`stack-code` does NOT shell out to this skill. It reads `references/templates/pr.md` directly via its own `execute-stack.py` and applies the same regex (via `lib.validate_conventional_subject`). This skill remains the single source of truth for the *template file* and the *title regex*; no Python is needed here.

### Dependencies

- `jj` (preferred) or `git` for commit extraction.
- No third-party tools. No Python. The skill is content-only.

### Visual Overview

```plaintext
[START]
   |
   v
[Step 1: Resolve commit ref]            -> default @, else jj log -r <ref> | git log -1 <ref>
   |
   v
[Step 2: Extract subject + body]        -> first line = subject; rest = body trailers
   |
   v
[Step 3: Validate subject regex]        -> conventional-commits allowlist
   |
   v
[Step 4: Read template]                 -> references/templates/pr.md
   |
   v
[Step 5: Fill placeholders from body]   -> summary, context, implementation, etc.
   |
   v
[Step 6: Emit title + blank line + body to stdout]
   |
   v
[END]
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. **Resolve the commit ref**. If a positional arg is given, use it; else default to `@`. Try `jj log -r <ref> --no-graph -T 'description'` first; fall back to `git log -1 --format=%B <ref>` when `jj` exits non-zero.
2. **Extract subject + body**. The subject is the first non-empty line. The body is everything after the first blank line. Recognise commit trailers (e.g. `Refs: #123`, `Breaking-Change: <text>`) and route them to the matching template sections.
3. **Validate the subject** against the Conventional Commits regex (above). On mismatch, exit 2 with a message naming the failing token and the regex.
4. **Read the template** at `references/templates/pr.md`. Use `Read` tool on the absolute path resolved relative to this skill directory.
5. **Fill placeholders** from the commit body:
   - `{{summary_paragraph}}` — first body paragraph (≤3 sentences); fall back to the subject's text after `: ` if the body is empty.
   - `{{context_body}}` — content under a `## Context` / `Why:` / `Background:` heading, if present.
   - `{{implementation_body}}` — content under `## Implementation` / `What:` / `How:`, if present.
   - `{{breaking_changes_body}}` — `Breaking-Change:` trailers; "None." when absent.
   - `{{related_issues_body}}` — `Refs:` / `Closes:` / `Fixes:` trailers; "None." when absent.
   - `{{manual_testing_body}}` — `Testing:` / `Manual-Test:` trailers; "Covered by automated tests." when absent.
   - `{{additional_notes_body}}` — anything left in the commit body that didn't map elsewhere; "None." when absent.

   Drop any optional section whose body resolves to "None." rather than leaving a stub — keep Summary and the Checklist only.
6. **Emit** the title line, a blank line, then the filled Markdown body to stdout.

### Standards Referenced

- `plugins/coding/constitution/standards/git/rules/GIT-PR-SIZE-01..04` — zone thresholds. Informational only here: zone enforcement is the reviewer's job, not the PR author's. This skill does NOT classify zones nor append review-guide boilerplate.
- `plugins/coding/constitution/standards/git/rules/GIT-PR-STACK-04` — drafts are non-negotiable when stacked. The caller passes `--draft` to `gh pr create`; this skill does not own that flag.
- `plugins/coding/constitution/standards/git/rules/GIT-PR-STACK-06` — stacked PRs open as drafts; same caller responsibility.
- The Conventional Commits subject convention (allowlist + regex) is enforced verbatim here and mirrored in `coding:stack-code` (`lib.validate_conventional_subject`). Both skills point at the same regex.

### Error Handling

| Condition                                  | Behaviour                                                     |
|--------------------------------------------|---------------------------------------------------------------|
| Unknown commit ref                         | Exit 2; print "no such revision" + the failing ref.           |
| Subject violates conventional regex        | Exit 2; print the regex, the offending subject, and the failing token. |
| Missing `jj` AND `git`                     | Exit 3; message "no commit source available".                 |
| Template file missing                      | Exit 4; print the absolute path that failed to resolve.       |

### Idempotence

Same commit ref + same template file = byte-identical stdout. No timestamps, no random IDs, no diff stats.

## Examples

```bash
# Default — write a PR for the current jj change, pipe to gh
write-pr | { read -r TITLE; read -r _; gh pr create --draft --title "$TITLE" --body-file -; }

# Inspect title + body without opening a PR
write-pr @-

# A specific git SHA in a non-jj repo
write-pr abc1234

# Reject a non-conventional subject loudly (exit 2)
write-pr deadbeef   # commit subject "WIP fix stuff" -> regex error
```

### Skill Completion

**Report the skill output as specified**:

```yaml
skill: write-pr
status: completed|failed
outputs:
  commit_ref: '<resolved jj/git ref>'
  title: '<conventional-commit title>'
  body: '<filled Markdown body>'
  exit_code: 0|2|3|4
issues: [...]
summary: |
  PR title + body emitted to stdout for commit <ref>.
  [Title regex pass/fail; placeholders filled; sections dropped where empty.]
```
