# Handover completion

Return:

```yaml
handover: complete
work_id: <id>
work_root: <absolute path>
state: <absolute state.md path>
working: <absolute state/working.md path>
external_anchor: <URL or response_only>
source_anchor: <remote revision, attachment locator, or inline patch/bundle label>
current_task_id: <full executable task ID or none>
next_owner: <exact continuation owner>
next_action: <exact continuation action>
continuation_intent: <capability-level work type, e.g. specification-led or generic coding implementation>
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
specifications: [<repository-relative path, inline, or Notion ref>]
generated_files: [<absolute created/materially rewritten paths>]
```

Then provide the complete fenced Markdown receipt defined in
[document-templates.md](document-templates.md) for publication or copy/paste,
followed by the immediate next action. Distinguish external publication success
from a response-only receipt. Never claim ignored state was transferred; the
receipt transfers state only by embedding each work file's raw contents.

For `external_anchor: response_only`, the fenced receipt must embed the verbatim
raw contents of every `## Work state` file, the complete patch or bundle when
that is the source anchor, and every inline specification. A payload label, a
local pathname, an elision, a summary, or "available on request" is not content
and makes the response non-rehydratable. Redact secrets from every embedded
block; if redaction leaves a required section incomplete, block instead.

When no verified portable source anchor exists, do not render the completion
shape or a complete receipt. Return `handover: blocked`, `rehydratable: false`,
the exact local-only changes, and the available safe choices: route a
save/publication through its Coding owners, or obtain user approval for a patch
or bundle carrier and include its complete payload in the receipt. Also block
when any required work-state file or continuation specification is incomplete,
ambiguous, or unredactable.
