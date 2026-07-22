# Handover completion

Return:

```yaml
handover: complete
source_tree: <kind (git-worktree|jj-workspace) and label of the current source tree>
workspace_root: <absolute .engineering/works path in the current source tree>
overview_path: <absolute .engineering/overview.md path in the default source tree>
external_anchor: <URL or response_only>
streams_carried: <n>
streams_index_only: <n>
streams:
  - work_id: <id>
    lifecycle: <initialized|active|blocked|complete|retiring>
    carried: <true|false>
    source_anchor: <remote revision, attachment locator, inline patch label, or none>
    current_task_id: <full executable task ID or none>
    next_owner: <exact continuation owner or ->
    next_action: <exact continuation action or ->
    continuation_intent: <capability-level work type, or none for index-only>
    rehydratable: <true|false>
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

Every stream in the current source tree's `works/` appears once in `streams`;
carried streams (selected continuable streams with a reachable anchor) carry
`carried: true`, and `complete`/`retiring`, unselected, and anchor-degraded
streams carry `carried: false`. `overview_path` is the default source tree's
global cross-tree index, updated with only this source tree's rows.
Then provide the complete fenced Markdown receipt defined in
[document-templates.md](document-templates.md) for publication or copy/paste,
followed by the immediate next action per carried stream. Distinguish external
publication success from a response-only receipt. Never claim ignored state was
transferred; the receipt transfers state only by carrying each work file's raw
contents.

For `external_anchor: response_only`, the fenced receipt must carry the raw
contents of every `### Work state` file, the complete patch when the source
anchor is an inline `git format-patch`, and every inline specification. A payload
label, a local pathname, an elision, a summary, or "available on request" is not
content and makes the response non-rehydratable. Redact secrets from every
carried block; if redaction leaves one stream's required section incomplete,
degrade that stream to an index-only row instead of blocking the whole receipt.

A response-only receipt permits only text source anchors: a destination-reachable
remote revision, or an inline `git format-patch` patch. A `git bundle` is binary
and must never be inlined as base64 or raw bytes — publish it to an external
attachment and record only its locator, ref, and base commit in that stream's
`### Source anchor`. If a stream's sole carrier is a bundle and the receipt is
response-only, that stream cannot be carried: relocate the bundle to an external
attachment and reference it, or degrade the stream to an index-only row.

When a continuable stream has no verified portable source anchor, mark its entry
`carried: false`, `rehydratable: false` with its exact local-only changes and
the available safe choices: pause to create a reachable revision (commit and,
when authorized, open a pull request), or obtain user approval for a patch or
external bundle attachment carrier. Also degrade a stream whose required
work-state file or continuation specification is incomplete, ambiguous, or
unredactable. Such degradation is per stream and never aborts the run:
persistence (on-disk state refresh and the default tree's `overview.md` upsert)
always completes first, so every degraded stream remains resumable on the same
machine from its state files. `handover: complete` therefore reports the
successful local pause even when every stream is `carried: false`; the
`carried`/`rehydratable` flags carry the cross-machine verdict. Reserve a
top-level `handover: blocked` for a failure that prevents persistence itself — an
unresolvable workspace, an unreadable contract, or an unwritable `overview.md` —
not for a missing source anchor.
