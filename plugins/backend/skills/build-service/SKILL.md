---
name: build-service
description: "Build complete backend services from spec to commit, including operation declaration, implementation, and quality gates. Use when creating new services, adding operations to existing services, or declaring manifest schemas."
model: opus
context: fork
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: "<service-name> <operations...> [--extend] [--notion-url=...]"
---

# Build Service

Owns the complete backend service lifecycle for `@theriety/service-{name}`
packages — from specification through manifest declaration, scaffolding,
implementation, testing, quality gates, review, and commit. `backend:build-data`
owns data orchestrators; `backend:audit-service` owns reviews of existing
services.

## Boundaries

- Use for: creating a new service package from scratch; adding operations,
  integrations, or webhooks to an existing service; declaring operation
  manifests with schema definitions; implementing a service defined in a
  DESIGN.md or Notion specification.
- Do not use for: building data packages (`backend:build-data`), scaffolding
  without implementation (`coding:draft-code`), fixing only failing tests
  (`coding:fix`), or auditing an existing service (`backend:audit-service`).

## Inputs

- **Required**: service name in kebab-case (maps to
  `@theriety/service-{name}`); operations list with brief descriptions.
- **Optional**: data domain (default: auto-detect the `@theriety/data-{domain}`
  package); external integrations (e.g. Stripe, SendGrid); peer
  `@theriety/service-*` services this one calls; webhook handlers; guards
  (authorization scopes and rules for `ensure()` calls); `--extend` to force
  extend mode; `--notion-url` for a Notion page with operation specifications.
- **Prerequisites**: the `@theriety/data-{domain}` package the service depends
  on exists; extend mode requires an existing `@theriety/service-{name}`
  package.

## Workflow

1. **Discover the spec.** Parse the service name, operations, domain,
   integrations, peers, webhooks, and guards. Detect mode with
   `ls <repository-root>/services/{name}/` — the directory exists in extend
   mode, otherwise new mode. Verify `<repository-root>/packages/manifest-{name}/`
   and `<repository-root>/packages/data-{domain}/`: a manifest missing in new
   mode is created in step 2; a missing data package stops the skill — ask the
   user. When `--notion-url` is given, fetch the operation specifications from
   Notion. In extend mode read `services/{name}/src/index.ts` (existing
   operations) and `services/{name}/package.json` (existing dependencies).
   Produce a file manifest of everything to create or modify, and ask for
   clarification instead of guessing when requirements are ambiguous.
2. **Declare operation manifests.** Skip when every requested operation already
   has a manifest. Check whether `manifests/{name}/` exists; when a new
   manifest package is needed, follow the project structure in
   [references/manifest-declaration.md](references/manifest-declaration.md).
   Dispatch one manifest subagent per operation using the prompt contract in
   that reference — at most 3 concurrent, execution reports under 1000 tokens,
   per the bounds in plugins/governance/constitution/references/delegation.md.
   Proceed only when every schema compiles; re-dispatch failed operations
   instead of continuing.
3. **Scaffold the project** (new mode only). Run `coding:setup-project` with
   the `@theriety/service-{name}` package structure.
4. **Draft, implement, test.** Run three sub-skills sequentially, each with its
   phase context from
   [references/implementation-patterns.md](references/implementation-patterns.md):
   `coding:draft-code` (skeleton with TODO placeholders), then
   `coding:complete-code` (fill implementations), then `coding:complete-test`
   (unit + integration tests). Within each sub-skill, batches may run in
   parallel.
5. **Quality gate.** Run `coding:fix` (at most 3 fix cycles, then escalate to
   the user), then `coding:lint`, then `coding:refactor`, then verify with
   `pnpm typecheck && pnpm lint && pnpm test`.
6. **Review.** Run `coding:review-code` covering correctness, patterns,
   security, and test coverage. Review issues loop back to step 5.
7. **Commit or hand over.** When verification passed and review approved, run
   `coding:commit`; when issues remain or the user prefers manual review, run
   `coding:handover`.
8. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker remains,
   then report the blocker instead of looping.

## Verification

- `pnpm typecheck && pnpm lint && pnpm test` pass in the service package (and
  in the manifest package when one was created).
- Every requested operation is declared in the manifest, registered in
  `source/index.ts`, and implemented with unit (`spec/**/*.spec.ts`) and
  integration (`spec/**/*.spec.int.ts`) tests.
- `coding:review-code` approved the change set.

## Completion

Report the mode (new or extend), package and manifest paths, operations
declared and implemented, integrations and webhooks implemented, unit and
integration test counts, typecheck/lint/test results, review outcome, whether
the work was committed or handed over, and any unresolved issues.
