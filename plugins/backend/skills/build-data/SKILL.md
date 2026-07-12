---
name: build-data
description: "Build complete data orchestrators from spec to commit, including schema setup, operations, controllers, and quality gates. Use when creating new data domains, adding operations to existing orchestrators, or implementing Prisma schemas from Notion."
model: opus
context: fork
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: "<domain-name> <operations...> [--extend] [--notion-url=...]"
---

# Build Data

Owns the complete data orchestrator lifecycle for `@theriety/data-{domain}`
packages — from specification through Prisma schema, operations, controller
integration, testing, quality gates, review, and commit.
`backend:build-service` owns service and manifest packages;
`backend:audit-data` owns reviews of existing data layers.

## Boundaries

- Use for: creating a new data orchestrator package from scratch; adding
  operations to an existing orchestrator; implementing Prisma schemas from
  Notion entity definitions; implementing data operations from Notion
  specifications; integrating operations into data controllers.
- Do not use for: service or manifest packages (`backend:build-service`), or
  auditing an existing data layer (`backend:audit-data`).

## Inputs

- **Required**: domain name in kebab-case (maps to `@theriety/data-{domain}`,
  e.g. `product`, `vault`); operations list where every name starts with a
  valid verb (`get`, `list`, `set`, `drop`, `resolve`, `attach`, `detach`,
  `initiate`); entities list (e.g. `offering`, `suite`, `tariff`).
- **Optional**: `--extend` to force extend mode; `--notion-url` for a Notion
  page with entity and operation specifications; selector pattern override —
  `simple` (single `selectors.ts`) or `complex` (co-located `entities/*.ts`).
- **Prerequisites**: `@theriety/data` and `@theriety/core` packages available
  in the workspace.

## Workflow

1. **Discover the spec.** Parse the domain name, operations (validate verb
   prefixes), entities, and selector pattern. Detect mode with
   `ls <repository-root>/data/{domain}/` — the directory exists in extend
   mode, otherwise new mode. Verify `@theriety/data` and `@theriety/core`
   exist; stop and ask the user when packages are missing or a verb is
   invalid. Default the selector pattern from entity count: `simple` for up
   to 3 entities, `complex` above that. In extend mode read the existing
   factory, operations barrel, and `package.json`. When `--notion-url` is
   given, fetch entity definitions and operation specifications from Notion.
   Produce a file manifest of everything to create or modify.
2. **Implement the Prisma schema.** Dispatch one comprehensive schema
   subagent with the prompt contract in
   [references/schema-implementation.md](references/schema-implementation.md);
   it translates every entity into documented Prisma models and runs
   `npx prisma generate`. Proceed only when generation and build pass.
3. **Scaffold the project** (new mode only). Run `coding:setup-project` with
   the `@theriety/data-{domain}` package structure: `package.json` with
   imports map (`#prisma`, `#types`, `#operations/*`, `#*`), vitest configs
   (unit + integration), `prisma/`, `src/` with `operations/`, `types/`, and
   `entities/` or `selectors.ts`, and `spec/` with `orchestrator.ts`,
   `fixture.ts`, `operations/`. Model on `<repository-root>/data/product/`
   (simple) or `<repository-root>/data/vault/` (complex).
4. **Scaffold the orchestrator surface.** Draft once with
   `coding:draft-code`: typed operation signatures with canonical
   implementation markers, selectors, exports, and factory/controller wiring
   — no operation bodies; step 5 is their sole implementation stage. Draft
   signatures to the verb contracts (reference implementations per verb live
   in `<repository-root>/data/`):
   - **get**: `findUnique` + `MissingDataError`
   - **list**: `findMany` with filter/cursor/sort
   - **set**: upsert with `CreateInput | UpdateInput`
   - **drop**: status-based soft/hard delete
   - **resolve**: priority-based fallback matching
   - **attach/detach**: junction record management
   - **initiate**: idempotent upsert with nested relations

   Record the operation inventory for step 5.
5. **Implement operations.** Dispatch operation subagents with the prompt
   contract in
   [references/operation-implementation.md](references/operation-implementation.md)
   — up to 3 batches in parallel, execution reports under 1000 tokens, per
   the bounds in plugins/governance/constitution/references/delegation.md.
   Each operation gets its implementation plus its completed integration-test
   markers.
6. **Integrate the controller.** Dispatch one controller subagent using the
   controller pattern in
   [references/operation-implementation.md](references/operation-implementation.md):
   delegating methods for all new operations in alphabetical order.
7. **Quality gate.** Run `coding:fix`, then `coding:lint`, then
   `coding:refactor`, then verify with
   `pnpm typecheck && pnpm lint && pnpm test`.
8. **Review.** Run `coding:review-code`. Review issues loop back to step 7.
9. **Commit or hand over.** When verification passed and review approved, run
   `coding:commit`; when issues remain or the user prefers manual review, run
   `coding:handover`.
10. Run the verification below; when a check fails, fix the cause and re-run
    that check. Repeat until every check passes or a concrete blocker
    remains, then report the blocker instead of looping.

## Verification

- `npx prisma generate` succeeds and every entity has a documented model with
  its relationships, constraints, and indexes.
- `pnpm typecheck && pnpm lint && pnpm test` pass in the data package.
- Every requested operation is implemented, integration-tested, and exposed
  as a controller method.
- `coding:review-code` approved the change set.

## Completion

Report the mode (new or extend), package path and name, entities, selector
pattern, operations implemented, unit and integration test counts,
typecheck/lint/test results, review outcome, whether the work was committed
or handed over, and any unresolved issues.
