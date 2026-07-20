---
name: create-screen-design
description: Create a new responsive screen-design contract from notion-derived work context, keep temporary exploration in the active work item, sync approved content through MDC/Notion owners, and promote durable design docs. Route existing screens to update-screen-design.
model: opus
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Skill, AskUserQuestion
argument-hint: "<product> <screen descriptions...> --work-id=<id> [--constraints=...] [--platforms=...]"
---

# Create Screen Design

Create new screen design without conflating ignored Notion transport,
task-specific design exploration, and durable versioned design knowledge.

## Boundaries

- Use for new UX contracts, layouts, responsive behavior, interaction states,
  accessibility, and handoff notes. Existing pages route to
  `update-screen-design`; implementation/rendered review stays with Web owners.
- Temporary detail lives in
  `.engineering/work/<work-id>/design/<slug>.md`; `design.md` is the
  PM-owned overview. Do not create an independent design artifact elsewhere.
- Notion-backed `.mdc` paths are owned by notion-sync and authored only through
  `specification:mdc`; do not choose/derive filenames or size-gate MDC.
- Durable feature/screen design promotes to `docs/design/<slug>.md`; only truly
  system-wide tokens/components/states/motion/accessibility update
  `docs/design/system.md` or its children.

## Inputs

- **Required**: product, screen descriptions, and `--work-id=<id>`.
- **Optional**: constraints and platforms (default web + mobile).
- **Prerequisites**: resolvable product/context, Notion credentials/tooling,
  and an active engineering work item.

The canonical template, parent database, and collection remain:

- template `4555730e74b44592b77dd8a97620d3f2`
- parent `110161382ea64eefa46a4907574d4530`
- collection `c7bc479b-71db-41b1-b5ab-a07c641816b5`

## Workflow

1. Before creating or materially rewriting a project artifact, read the
   absolute `engineering-work.md` path injected by Essential. If unavailable,
   stop artifact writes and report the missing contract. Resolve work/default
   roots; read `working.md`, then `state.md`, then referenced spec/design paths.
2. Materialize required product/spec context through
   `specification:sync-spec`. Pull the template/context transport into the
   default-workspace mirror through `specification:sync-notion`, preserving its
   returned `.mdc` paths and refs. Search for collisions; existing screens route
   to update.
3. Map each requested screen to product relation, source refs, constraints, and
   platform coverage. Create a lowercase work-local design child with purpose,
   audience/task, hierarchy/navigation, responsive behavior, loading/empty/
   error states, accessibility, distinct alternatives/rationale, decisions,
   implementation notes, and provenance.
4. Present alternatives and obtain approval. Return the child row/status to the
   PM for `design.md`/`state.md` reconciliation; do not edit those overview
   files directly.
5. For approved screens, ask `specification:sync-notion` to create the page
   under the canonical parent using the live template/relations. Route authored
   MDC body content through `specification:mdc`; use the path/ref returned by
   transport and never hand-write MDC. Verify the persisted ref and remote
   identity before attempting another screen.
6. Promote stable non-system design to `docs/design/<screen-slug>.md` with
   Notion ids, source revision/hash, approved decision links, and supersession
   metadata. Route any system-wide rules to `docs/design/system.md` without
   duplicating them in the screen doc. Update `docs/index.md`/design links when
   needed.
7. Verify each remote page through `sync-notion` diff/verification pull and the
   durable derivation against the verified source. Stop on uncertain creation
   to avoid duplicates.
8. Return explicit final paths generated or materially rewritten as
`generated_files`, plus PM reconciliation. Do not run file sizing; after all
writers finish, the PM checks only eligible work Markdown inside the target
`.engineering/`.

## Verification

- Each screen has one unambiguous remote ref with canonical parent/product
  relations and complete responsive/state/accessibility coverage.
- Work design remains temporary and lower-case; durable promotion is approved,
  versioned, linked, and provenance-backed.
- No MDC path was invented or hand-edited; no worker edited PM-owned files.
- `generated_files` includes every work/durable/transport path changed.

## Completion

Return status, canonical ids, work/spec sources, per-screen temporary design,
remote ref/verification, durable promotion/system-rule routing, PM
reconciliation, unattempted recovery, and `generated_files`.
