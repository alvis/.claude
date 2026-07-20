---
name: sync-spec
description: Materialize a required Notion specification into an active engineering work directory or complete approved specification changes through the default-workspace mirror. Use before specification planning, implementation, or review and when closing a work item. Delegate transport and conflicts to sync-notion.
model: opus
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, TodoWrite, Skill
argument-hint: "<notion-url-or-id> --work-id=<id> [--mode=materialize|complete]"
---

# Sync Spec

Orchestrate specification materialization and completion without owning Notion
transport. `specification:sync-notion` owns pull, push, pairing, conflicts, and
post-sync integrity. `specification:mdc` owns authored `.mdc` content changes.

## Boundaries

- `materialize` refreshes the authoritative mirror under the explicitly
  resolved default workspace, then materializes only the requested page tree
  under the active workspace's `.engineering/work/<work-id>/spec/`.
- `complete` reconciles approved work-spec changes into the default mirror,
  delegates outbound sync, performs a verification pull, regenerates versioned
  `docs/specs/<capability>/*.md`, and reports discoverable dependent work that
  requires revalidation.
- Never derive, normalize, or rename an MDC filename. Paths are owned by
  `notion-sync` and are taken verbatim from the transport report.
- Never use a legacy root specification bundle, copy the entire default mirror
  into a worktree, or push/merge by calling `notion-sync` directly.

## Inputs

- **Required**: Notion URL or page id and `--work-id=<id>`.
- **Optional**: `--mode=materialize|complete` (default `materialize`),
  `--capability=<lowercase-slug>` for durable derivation.
- **Prerequisites**: the absolute Essential engineering-work contract path
  supplied by injected context; a workspace resolved by that contract;
  `notion-sync` and `NOTION_TOKEN`.

## Workflow

1. Before creating or materially rewriting a project artifact, read the
   absolute `engineering-work.md` path injected by Essential. If unavailable,
   stop artifact writes and report the missing contract. Resolve:
   - `default_workspace_root` explicitly; never infer it from the current
     worktree when Git or jj reports a different default workspace;
   - `active_workspace_root` and canonical `work_id`;
   - `mirror_root = <default>/.engineering/notion`;
   - `work_spec_root = <active>/.engineering/work/<work-id>/spec`.
   Verify `.engineering/` is ignored by the repository VCS and neither target
   is tracked; refuse before writing if that boundary is not true.
   For an existing work item, read `working.md`, then `state.md`, then only the
   specification/sync paths they reference.
2. Normalize the Notion id only for identity comparison. Require a 32-hex id
   after dash removal. Do not use the id to construct a filename.
3. In `materialize` mode:
   - invoke `Skill(sync-notion)` in `notion-to-local` mode with the Notion ref,
     `mirror_root`, and recursive following;
   - select the returned root and required descendants by frontmatter `ref:`
     and returned relationship data, not filename shape;
   - build an incoming manifest containing every selected relative path,
     stable `ref:`, source revision, and SHA-256 content hash. If
     `work_spec_root` already exists, load its last materialization manifest
     from the work receipt and hash the current tree before staging anything;
   - refuse with `materialization_conflict` when the prior manifest is absent,
     a recorded file is missing or changed, an unrecorded file exists, a
     stable identity moved unexpectedly, or the current aggregate manifest
     hash differs. Preserve the existing tree byte-for-byte and report the
     existing/incoming manifest diff for explicit reconciliation. Never treat
     a dirty work copy as disposable and never route this work-local conflict
     through Notion transport conflict handling;
   - when the current tree is absent or exactly matches its recorded manifest,
     stage only the selected set in a sibling temporary directory, preserving
     returned relative paths. Verify the staged manifest, move an existing
     clean tree to a sibling rollback path, atomically rename the staged tree
     into `work_spec_root`, and restore the rollback tree if promotion fails.
     Remove the rollback only after the promoted manifest verifies;
   - record the root ref, paths, source revision, per-file source hashes, and
     aggregate materialization-manifest hash in the work state/receipt. The PM
     reconciles `state.md`; this skill returns the required update rather than
     editing PM-owned indexes itself.
4. In `complete` mode:
   - require approved changes and a clean review disposition in the work state;
   - compare work copies with matching mirror files by `ref:`. Apply authored
     content changes to mirror MDC only through `Skill(mdc)`; transport metadata
     remains owned by `sync-notion`/`notion-sync`;
   - invoke `Skill(sync-notion)` in `local-to-notion` or `two-way-merge` mode as
     required by the comparison. Never reproduce its conflict protocol;
   - invoke `Skill(sync-notion)` in `notion-to-local` mode into a verification
     directory and require matching identity and clean expected diff before
     replacing the mirror;
   - regenerate the affected versioned specification under
     `docs/specs/<capability>/`. Use lowercase human-owned filenames and
     `index.md`; do not reuse or derive notion-sync paths. Preserve stable
     Notion ids, source revision, source hash, derivation timestamp, and a
     durable task/PR/Notion receipt anchor in derived frontmatter. Keep the
     ignored local receipt path only in `state.md`;
   - enumerate locally registered Git worktrees and jj workspaces explicitly.
     For locally readable open work whose recorded source id matches and hash
     changed, return a `needs_revalidation` notice with workspace/work-id/state
     paths for its PM; do not edit PM-owned state. Return durable external
     task/PR/Notion anchors and unknown or remote dependents separately. Never
     claim an ignored remote work directory was discovered or updated.
5. Return explicit final paths generated or materially rewritten as
   `generated_files`. Do not run `wc -c`; the PM performs the one final
   batch size pass after all artifact writers finish. `.mdc` is size-exempt.

<IMPORTANT>
The default-workspace mirror is ignored local transport state. It must exist
only under the resolved default workspace and must never be committed, copied
through Git/jj, or treated as a durable handoff. A linked worktree or secondary
jj workspace receives only its work-local selected specification.
</IMPORTANT>

## Verification

- The root specification is non-empty and its frontmatter `ref:` matches the
  requested Notion id; filenames play no role in identity.
- Every materialized path came from the verified transport report and belongs
  to the requested root tree.
- An existing work specification was replaced only when its current manifest
  exactly matched the recorded last-materialized manifest. A missing or
  diverged manifest produced `materialization_conflict` without changing the
  existing tree.
- Mirror and work-spec roots are ignored/untracked in their owning workspaces.
- Completion has a verified outbound sync, verification pull, refreshed
  default mirror, durable receipt anchor, explicit locally registered workspace
  enumeration, and separate unknown/remote revalidation notices.
- No direct `.mdc` content write bypassed `specification:mdc`, and no transport
  or conflict operation bypassed `specification:sync-notion`.

## Completion

<report>

```yaml
skill: sync-spec
status: completed|partial|refused
mode: materialize|complete
work_id: '<id>'
outputs:
  default_mirror: '<absolute default-workspace path or null>'
  work_spec_root: '<absolute active-workspace path>'
  notion_root: {id: '<32hex>', path: '<notion-sync-owned path>'}
  materialization: {status: unchanged|replaced|materialization_conflict, manifest_hash: '', existing_preserved: true|false, conflict_diff: []}
  materialized_files: [{path: '', notion_id: '', source_revision: '', source_hash: ''}]
  derived_specs: [{path: '', source_ids: [], source_revision: '', source_hash: '', receipt_anchor: ''}]
  revalidation:
    local_registered: [{workspace_root: '', work_id: '', state_path: '', status: needs_revalidation, state_updated: false}]
    external_receipt_anchors: []
    unknown_or_remote_dependents: []
generated_files: []
issues: []
```

</report>
