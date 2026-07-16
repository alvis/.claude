# Agent Memory Template

Use this schema for every project-scoped agent memory at
`.claude/agent-memory/<agent-name>/MEMORY.md`. The owning agent creates the file lazily and curates it; do not
seed empty memory files in a target repository.

## Rules

- Store only durable, repository-specific knowledge that will improve a future task for this role.
- Repository source, authoritative specifications, and current runtime evidence always override memory.
- Give every entry evidence, a `Last verified` date, and a `Recheck` trigger or expiry.
- When evidence contradicts an active entry, replace the active claim and move the superseded claim to
  `archive/YYYY-MM.md` with the reason it changed.
- Keep the primary file at or below 150 lines and 20KB. Before either threshold, consolidate duplicates, move
  detailed material to `topics/<slug>.md`, and archive obsolete history.
- Never store secrets, credentials, personal data, raw task logs, transient status, or unresolved sensitive
  exploit details.

## Current Facts

### <fact>

- Evidence: `<path, command, specification, issue, or result>`
- Last verified: `YYYY-MM-DD`
- Recheck: `<event that invalidates this fact, or expiry date>`
- Applies to: `<scope>`
- Fact: <concise current claim>

## Reusable Lessons

### <lesson>

- Evidence: `<path, command, experiment, or result>`
- Last verified: `YYYY-MM-DD`
- Recheck: `<trigger or expiry>`
- Lesson: <what to repeat or avoid, and why>

## Watchpoints

### <risk or drift signal>

- Evidence: `<path, issue, failure signature, or result>`
- Last verified: `YYYY-MM-DD`
- Recheck: `<trigger or expiry>`
- Watch for: <condition and the action it should trigger>

## Topic Index

- [`topics/<slug>.md`](topics/<slug>.md) — <durable detail moved out of the primary file>

## Archive Index

- [`archive/YYYY-MM.md`](archive/YYYY-MM.md) — <superseded claims and why they changed>
