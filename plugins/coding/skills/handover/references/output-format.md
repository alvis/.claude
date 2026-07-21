# Handover completion

Return:

```yaml
handover: complete
work_id: <id>
work_root: <absolute path>
state: <absolute state.md path>
working: <absolute working.md path>
external_anchor: <URL or response_only>
source_anchor: <remote revision, attachment locator, or inline payload label>
state_snapshot: <attachment locator or inline payload label>
current_task_id: <full executable task ID or none>
plan_source: state.md
plan_digest: <64-lowercase-hex>
plan_hash_kind: engineering-plan-definition-digest-v1
next_owner: <exact continuation owner>
next_action: <exact continuation action>
rehydratable: true
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
spec_sync:
  status: <exact sync-owner operational status or not_applicable>
  classification: <exact sync-owner relationship or not_applicable>
  next_action: <exact sync-owner next action or none>
generated_files: [<absolute created/materially rewritten paths>]
```

Then provide the complete fenced `engineering-work-handover/v3` receipt for
publication or copy/paste, followed by the immediate next action. Distinguish
external publication success from a response-only receipt. Name every carrier
as `external_locator` or `inline_content`, and report its verified checksum.
Never claim ignored state was transferred. For every Notion carrier, report
the logical profile, stable ref, captured revision, paired remote
`transport_manifest_hash`/`contract_digest`, exact sync-owner
`status`/`classification`/`next_action`, and optional contained
repository-relative suggested root. Report no B/L carrier only for `status:
success`, `classification: initial|unchanged|metadata_only|converged`,
`next_action: none`, with no authored/pending local work. Otherwise report the
checksum and inline/external carrier of the complete helper-produced
`specification-blr-transfer+json/v1` package, or block when B/L cannot be
constructed. Do not emit or redact-and-retain the origin's
absolute/workspace-specific transport root; omit it entirely because the
destination resolves its own root.

For `external_anchor: response_only`, the fenced receipt must embed the complete
decoded-or-encoded bytes (as declared) for the state snapshot, any patch or
bundle source anchor, every required linked work artifact, every `kind: inline`
specification, and every required Notion B/L transfer. The embedded transfer is the exact canonical JSON package
bytes (base64 when required by the containing YAML scalar), not a reconstructed
object. A payload label, local pathname, elision, summary, or
“available on request” is not content and makes the response non-rehydratable.
Check the exact embedded bytes again after rendering and report the checksum
verdict.

The state carrier is exactly `engineering-work-state+json/v1` emitted by
Essential's `validate-engineering-state pack` operation and accepted by its
`validate-snapshot` operation. Preserve its canonical JSON bytes; do not
convert it to YAML or reconstruct it from prose.

When no verified portable source anchor exists, do not render the completion
shape or a complete v3 receipt. Return `handover: blocked`,
`rehydratable: false`, the exact local-only changes, and the available safe
choices: route a save/publication through its Coding owners, or obtain user
approval for a patch/bundle carrier and attach/include its complete payload.
Also block when the state snapshot or any required narrative work artifact is
incomplete, ambiguous, unredactable, or available only through an
ignored/local-only path, or when a Notion state that
does not satisfy the exact no-B/L predicate lacks a complete portable B/L
package.
