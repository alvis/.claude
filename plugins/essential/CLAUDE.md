# Working as a team

Delegate on signal, not reflex: keep bounded conversational work inline;
delegate when a specialist owns the outcome, independent work can run in
parallel, noisy output would consume context, or independent review is
required — then review and synthesize what returns. Only the main agent
names teammates; capture returned `agent_id`s and address every direct
message by ID. Keep every dispatch and direct message below 4,096
characters; externalize longer detail to a task-owned artifact and send the
path. Distinguish user intent, observed facts, inferences, accepted
reversible assumptions, and unresolved questions; stop stale work when
evidence changes the plan, escalate consequential decisions, and never
invent runtime measurements.

Before delegating, orchestrating, or recording review, read
`{{PLUGIN_DIR}}/references/orchestration.md` — routing, message discipline,
naming, nesting, and review responsibility live there, with team-lifecycle
and model/effort selection in its per-moment references.

Before creating or materially rewriting a lifecycle-managed engineering
artifact, read `{{PLUGIN_DIR}}/references/engineering-work.md`; if
unavailable, do not write it. Run its resolver without inventing a work ID.
On `work_id_required`, the PM asks the user and workers report the
ambiguity. On `requires_ignore`, workers stop; the PM alone adds
`.engineering/` to the active workspace `.gitignore`, records it in
`generated_files`, and reruns.
