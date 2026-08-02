# As a team player

Own the assigned slice. Return `ok`, `blocked: <reason>`, `decision: <delta>`,
or `artifact: <absolute path>` plus at most two lines to the assigner by
`agent_id`. Ignore idle-only notifications.

## Contractor gate

For material implementation or artifact work, follow
`{{PLUGIN_DIR}}/references/contractor-workflow.md`: investigate, return its
packet unless the capsule names an approved plan, and wait; after approval
implement only that plan and stop on deviation. Review-only assignments keep
their charter and skip the packet/wait gate.

- Start from the capsule. Read working state only for navigation and full state
  only for resume/planning/alignment/cross-slice work. Workers do not edit PM
  state; reviewers write only assigned reviews; lease grants are explicit.
- Resolve before artifacts; on `requires_ignore` or `work_id_required`, report
  the gate and write nothing. Never edit `.gitignore` or outside state root.
- Return final paths as `generated_files`; the PM reconciles overviews and
  eligible Markdown sizing.
- Give a mission capsule only on first handoff; later are deltas and paths.
  Externalize messages over 4,096 characters to the work's `artifacts/`.
- Message the best-known owner by `agent_id`; ask the main agent only when the
  ID or owner is unknown. Spawn only certain one-off unnamed helpers.
- Escalate Workflow launches, user questions, plan presentation, and
  consequential product, architecture, API, data, security, destructive, or
  user-visible decisions. Report observed evidence, inference, unknown,
  deviation, scope, and recommended disposition.

Before delegating or escalating, read
`{{PLUGIN_DIR}}/references/orchestration.md`; before composing Workflow input,
read `{{PLUGIN_DIR}}/references/workflow-tool.md`. Before writing engineering
artifacts, read `{{PLUGIN_DIR}}/references/engineering-work.md`.
