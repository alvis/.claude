# Handover completion

Return:

```yaml
handover: complete
source_tree: <kind (git-worktree|jj-workspace) and label of the checkout this session ran in>
state_root: <absolute default source tree root that carries .engineering/>
workspace_root: <absolute state_root/.engineering/works path>
overview_path: <absolute state_root/.engineering/overview.md path>
streams_indexed: <n>
streams_selected: <n>
streams:
  - work_id: <id>
    lifecycle: <initialized|active|blocked|reviewing|completed|retiring>
    work_dir: <absolute .engineering/works/<work-id> directory holding this stream>
    current_task_id: <full executable task ID or none>
    next_owner: <exact continuation owner or ->
    next_action: <exact continuation action or ->
    continuation_intent: <capability-level work type, or none for index-only>
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

Every stream in `state_root/.engineering/works/` appears once in `streams`.
`work_dir` is present for every stream whose work directory exists, including
`reviewing`, `completed`, and `retiring` ones. `overview_path` is the global
index beside them, updated with only the refreshed streams' rows.
Then state the immediate next action per selected stream.

Reserve a top-level `handover: blocked` for a failure that prevents persistence
itself — an unresolvable workspace, an unreadable contract, or an unwritable
`overview.md`.
