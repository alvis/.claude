# Handover completion

Return:

```yaml
handover: complete
source_tree: <kind (git-worktree|jj-workspace) and label of the current source tree>
workspace_root: <absolute .engineering/works path in the current source tree>
overview_path: <absolute .engineering/overview.md path in the default source tree>
external_anchor: <URL or response_only>
streams_embedded: <n>
streams_index_only: <n>
streams:
  - work_id: <id>
    lifecycle: <initialized|active|blocked|complete|retiring>
    embedded: <true|false>
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
continuable streams carry `embedded: true`, and `complete`/`retiring` streams
carry `embedded: false`. `overview_path` is the default source tree's global
cross-tree index, updated with only this source tree's entry.
Then provide the complete fenced Markdown receipt defined in
[document-templates.md](document-templates.md) for publication or copy/paste,
followed by the immediate next action per embedded stream. Distinguish external
publication success from a response-only receipt. Never claim ignored state was
transferred; the receipt transfers state only by embedding each work file's raw
contents.

For `external_anchor: response_only`, the fenced receipt must embed the raw
contents of every `### Work state` file, the complete patch when the source
anchor is an inline `git format-patch`, and every inline specification. A payload
label, a local pathname, an elision, a summary, or "available on request" is not
content and makes the response non-rehydratable. Redact secrets from every
embedded block; if redaction leaves one stream's required section incomplete,
degrade that stream to an index-only row instead of blocking the whole receipt.

A response-only receipt permits only text source anchors: a destination-reachable
remote revision, or an inline `git format-patch` patch. A `git bundle` is binary
and must never be inlined as base64 or raw bytes — publish it to an external
attachment and record only its locator, ref, and base commit in that stream's
`### Source anchor`. If a stream's sole carrier is a bundle and the receipt is
response-only, that stream cannot be embedded: relocate the bundle to an external
attachment and reference it, or degrade the stream to an index-only row.

When a continuable stream has no verified portable source anchor, mark its entry
`embedded: false`, `rehydratable: false` with its exact local-only changes and
the available safe choices: route a save/publication through its Coding owners,
or obtain user approval for a patch or external bundle attachment carrier. Also
degrade a stream whose required work-state file or continuation specification is
incomplete, ambiguous, or unredactable. When the filtered selection is a single
stream and that stream is blocked, do not render the completion shape or a
complete receipt: return `handover: blocked`, `rehydratable: false`, and the
exact local-only changes for that stream.
