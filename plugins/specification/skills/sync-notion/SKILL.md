---
name: sync-notion
description: Synchronize paired local files and Notion pages in a declared direction, including recursive pulls, verified pushes, and explicit two-way conflict resolution. Own Notion transport and pairing; keep specification orchestration in sync-spec and authored MDC edits in mdc.
model: opus
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task, AskUserQuestion, Skill
argument-hint: "<local-to-notion|notion-to-local|two-way-merge> <file-or-ref> [counterpart...] [--out=<dir>]"
---

# Sync Notion

Own transport, pairing, conflict decisions, and post-sync integrity for
local–Notion pairs. Public modes are `local-to-notion`, `notion-to-local`, and
`two-way-merge`; CLI verbs are implementation details.

## Boundaries

- Use for explicit pull, push, or merge transport. `specification:sync-spec`
  orchestrates work materialization and completion; `specification:spec-code`
  owns specification content and durable derivation.
- For engineering specifications, the ignored canonical mirror is
  `<default-workspace>/.engineering/notion/` and work-local materialization is
  `<active-workspace>/.engineering/work/<work-id>/spec/`.
- `.mdc` denotes Notion-backed content. Preserve notion-sync-owned paths and
  never calculate filenames from titles or ids.
- `notion-sync` may create/replace transport files and update pairing metadata.
  Authored `.mdc` body changes must route through `specification:mdc`.
- Do not run the ordinary Markdown size gate for `.mdc`.

## Inputs

- **Required**: one public mode and at least one local path or Notion ref.
- **Optional**: explicit counterpart, `--out=<dir>`, `--database-id=<id>`.
- **Prerequisites**: `notion-sync`, `NOTION_TOKEN`, and for project artifact
  writes the absolute Essential `engineering-work.md` path injected in context.

## Workflow

1. Before creating or materially rewriting a project artifact, read the
   absolute `engineering-work.md` path injected by Essential. If unavailable,
   stop artifact writes and report the missing contract. Resolve default and
   active workspace roots from that contract; never guess that the current
   worktree is the default workspace.
   For an engineering work pair, read `working.md`, then `state.md`, then only
   the referenced sync/spec paths. Before writing an engineering mirror or work
   spec, verify `.engineering/` is ignored and the target is untracked.
2. Resolve every pair as `{local_path, notion_ref, state}`. Prefer frontmatter
   `ref:`, then an explicit ref, then `notion-sync search -j`. Load
   [references/database-resolution.md](references/database-resolution.md) only
   for search/database resolution. Refuse ambiguous identity or a target path
   outside the declared output root.
3. Perform at most one recursive pull per requested root using the CLI's
   recursive flags. Preserve returned relative paths, refs, parents,
   relationships, and revision evidence verbatim. For specification mirrors,
   refuse `.md` transport output: Notion-owned files must be `.mdc`.
4. Execute exactly one public mode using
   [references/sync-mode-execution.md](references/sync-mode-execution.md):
   - `local-to-notion`: diff, review, push, then verify;
   - `notion-to-local`: pull to staging, verify identity/completeness, then
     replace the declared output set;
   - `two-way-merge`: load
     [references/two-way-merge.md](references/two-way-merge.md), resolve every
     conflict explicitly, apply authored content through `Skill(mdc)`, push,
     then verify.
5. Run the integrity gate per pair with a JSON diff or independent verification
   pull. Require correct identity, intact `ref:`/`parent:` metadata, recursive
   coverage, and no unexpected body drift. When local is authoritative, retry
   push + verification at most three complete cycles. A zero command exit does
   not override failed integrity.
6. On a data-loss signal, stop before later pairs. Report the failing pair and
   corrected copy-paste-ready content, then ask whether to re-verify, skip
   (`partial`), or abort. Never silently continue.
7. Return explicit final paths generated or materially rewritten as
   `generated_files`. Do not run `wc -c`; the PM owns the one final Markdown
   batch pass after all writers complete.

<IMPORTANT>
Only `sync-spec` may request specification completion across the work copy,
default mirror, remote Notion page, and durable derived docs. This skill
transports declared pairs and reports evidence; it does not promote docs,
reconcile PM-owned indexes, or mark dependent work for revalidation.
</IMPORTANT>

## Verification

- Each pair has a clean expected post-sync diff, correct page identity, intact
  metadata, and complete requested recursive coverage.
- Every merge conflict records a decision; skipped conflicts make the run
  `partial`.
- Specification mirror paths are returned by notion-sync, not derived, and the
  default mirror was written only in the resolved default workspace.
- `generated_files` names every final path created or materially rewritten.

## Completion

<report>

```yaml
status: success|partial|failure|refused
mode: local-to-notion|notion-to-local|two-way-merge
pairs:
  - local_path: ''
    notion_ref: ''
    action: created|updated|pulled|merged|skipped
    conflicts: {found: 0, resolved: 0, skipped: 0}
    post_sync_diff: clean|unexpected|not_run
    metadata_verified: true|false
generated_files: []
commands: []
unresolved: []
```

</report>
