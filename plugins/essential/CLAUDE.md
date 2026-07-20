# Working as a team

- Keep bounded conversational work inline. Delegate when a live specialist owns
  the outcome, independent work can run in parallel, noisy output would consume
  context, or independent review is required. Review and synthesize returns.
- Inspect the live roster before every spawn. Match the requested action and
  deliverable before subject nouns; never invent an unavailable role or an
  unrequested prerequisite stage.
- Only the main agent assigns configured teammate names. Capture returned
  `agent_id`s and address every direct message by ID. Nested agents may spawn
  only certainly one-off helpers and omit configured names.
- Give full context once: objective, constraints, acceptance criteria, and
  absolute artifact paths. Later messages contain only changed state, a
  decision, blocker, or requested result. Keep every dispatch and direct message
  below 4,096 characters; externalize longer detail to a task-owned artifact.
- Distinguish user intent, observed facts, inferences, accepted reversible
  assumptions, and unresolved questions. Stop stale work when evidence changes
  the plan and escalate consequential decisions.
- Follow a skill yourself and delegate only its bounded steps. Parallelize only
  independent work. Own what you spawn and independently review consequential
  changes. Never invent runtime measurements.

Before delegating, orchestrating, or recording review, read
`{{PLUGIN_DIR}}/references/orchestration.md`.

Before creating or materially rewriting project Markdown, read
`{{PLUGIN_DIR}}/references/engineering-work.md`; if unavailable, do not write
artifacts and report the missing contract. Before any work artifact, run its
workspace resolver. Workers stop on `requires_ignore`; the PM alone adds
`.engineering/` to the target `.gitignore`, records it in `generated_files`,
and reruns the resolver.
