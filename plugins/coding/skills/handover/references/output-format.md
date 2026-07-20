# Handover completion

Return:

```yaml
handover: complete
work_id: <id>
work_root: <absolute path>
state: <absolute state.md path>
working: <absolute working.md path>
external_anchor: <URL or response_only>
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
sync_state: <verified|pending|conflict>
generated_files: [<absolute created/materially rewritten paths>]
```

Then provide the complete fenced `engineering-work-handover/v1` receipt for
publication or copy/paste, followed by the immediate next action. Distinguish
external publication success from a response-only receipt. Never claim ignored
state was transferred.
