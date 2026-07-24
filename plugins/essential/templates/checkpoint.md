# Checkpoint block template

One block per emission event, appended to the stream's external anchor (task,
PR, or Notion work item). Compact by design: identities and exact revisions,
not narrative. See `references/checkpoints.md` for when to emit.

```markdown
## Checkpoint: <event-type>

- Work: `<work-id>` · State revision: `<n>`
- At: `<ISO-8601>` · Actor: `<capability_id>`
- Subject: `<id>` @ `<content hash | commit SHA | base-id | render revision>`
- Consequence: <one line: what is now decided, approved, dispatched, or done>
- Invalidates: `<id@revision>, …` (omit when none)
- Evidence: <link or ref> (omit when none)
```

Event types: `decision-accepted`, `plan-approved`, `dispatch`, `irreversible`,
`artifact-approved`, `handover`, `retirement`. An `artifact-approved` block
must carry the full approval binding (reviewer, scope, exceptions) from
`references/checkpoints.md`.
