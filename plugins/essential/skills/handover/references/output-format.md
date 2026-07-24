# Handover completion

Return:

```yaml
handover: complete
source_tree: <kind (git-worktree|jj-workspace) and label of the current source tree>
workspace_root: <absolute .engineering/works path in the current source tree>
overview_path: <absolute .engineering/overview.md path in the default source tree>
external_anchor: <URL or response_only>
streams_indexed: <n>
streams_selected: <n>
streams:
  - work_id: <id>
    lifecycle: <initialized|active|blocked|complete|retiring>
    transfer_path: <absolute .engineering/works/<work-id> directory holding this stream>
    source_anchor: <remote revision, artifacts-relative patch/bundle, or none>
    current_task_id: <full executable task ID or none>
    next_owner: <exact continuation owner or ->
    next_action: <exact continuation action or ->
    continuation_intent: <capability-level work type, or none for index-only>
    transferable: <true|false>
    files_classified:
      completed: <n>
      in_progress: <n>
      planned: <n>
      blocked: <n>
    decisions:
      finalized: <n>
      deferred: <n>
      researched: <n>
overviews_reconciled: [<relative paths>]
generated_files: [<absolute created/materially rewritten paths, including overview.md>]
```

Every stream in the current source tree's `works/` appears once in `streams`.
`transfer_path` is the directory that holds that stream — the thing a recipient
copies — and is present for every stream whose work directory exists, including
`complete` and `retiring` ones. `overview_path` is the default source tree's
global cross-tree index, updated with only this source tree's rows.
Then provide the complete fenced Markdown receipt defined in
[document-templates.md](document-templates.md) for publication or copy/paste,
followed by the immediate next action per selected stream. Distinguish external
publication success from a response-only receipt.

The receipt indexes state; it never carries it. Do not inline a work file's
contents, a specification body, artifact bytes, or a patch — name the work
directory instead. This holds identically for `external_anchor: response_only`:
a response-only receipt is the normal case, not a degraded one, because the
index is bounded by the number of streams rather than the size of the work.

**Never write the receipt, or any part of it, to a file.** There is no size at
which spilling to disk becomes correct — an index that somehow ran long is
shortened by dropping detail to pointers, never relocated to `/tmp`, a dotted
sibling such as `.local/`, the repository root, or `$HOME`. The state is already
persisted under `.engineering/`; a pointer to it loses nothing. The one file a
handover may generate is an approved `git format-patch` patch or `git bundle`,
and it belongs in `.engineering/works/<work-id>/artifacts/` so it travels with
the directory — never inlined into the receipt, whatever its format.

`transferable` is a statement about **code reachability only**. Mark a stream
`transferable: false` when it has no destination-reachable source anchor and no
approved patch/bundle carrier, and record its exact local-only changes plus the
safe choices: pause to create a reachable revision (commit and, when authorized,
open a pull request), or approve a patch or bundle under `artifacts/`. Its state
is transferable either way — copying the work directory always works — so this
never aborts the run, and persistence has already completed. Reserve a top-level
`handover: blocked` for a failure that prevents persistence itself — an
unresolvable workspace, an unreadable contract, or an unwritable `overview.md` —
not for a missing source anchor.
