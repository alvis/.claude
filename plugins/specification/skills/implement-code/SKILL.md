---
name: implement-code
description: Execute approved specification tickets end to end by resolving ticket intent, materializing the authoritative spec bundle, coordinating implementation and tests, and reviewing alignment. Use after plan-code approval or to resume an explicitly scoped implementation. Keep contract authoring in spec-code and generic coding in the coding plugin.
model: opus
context: fork
agent: general-purpose
allowed-tools: Task, Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion
argument-hint: "<ticket or spec selector> [--spec-path=<path>] [--use-cache] [--resume] [--parallel]"
---

# Implement specification

Orchestrate one approved specification ticket from contract to reviewed code. This skill owns ticket resolution, spec materialization, execution/resume routing, deviation decisions, and alignment review; delegated coding skills own production edits.

## Inputs and boundaries

- Required ticket, spec selector, or explicit local spec path.
- Optional `--spec-path`, `--use-cache`, `--resume`, and capability-gated `--parallel`.
- An approved contract and a commit plan are prerequisites. Missing or contradictory intent is a blocker, not permission to guess.
- Never edit production code directly when a coding child owns the implementation. Never suppress general/security review because specification alignment fails.

## Workflow

1. Resolve the ticket and load local `DRAFT.md`/`PLAN.md` plus the authoritative Notion tree. With `--use-cache`, accept the cache only when the bundle contains Markdown and the ticket's root-id file is non-empty; otherwise record a cache miss and refresh through `sync-spec`.
2. Build a compact spec pointer containing ticket identity, acceptance criteria, affected areas, deviations, and verification commands. Preserve it across all child invocations.
3. Prepare or validate project structure, then invoke `coding:write-code` (or its resume path) with the pointer, plan, scope, and required tests. Use parallel execution only when files and dependencies are demonstrably independent; collect each child report.
4. Run focused tests and lint/type checks through coding skills. Record failures as implementation issues and route diagnosis to `coding:fix`; do not broaden scope to unapproved features.
5. Invoke `specification:review-implementation` over the resulting diff. That review must run the general/security/code-quality checks from `coding:review-code` even when alignment has major findings. Resolve each deviation explicitly and repeat only the affected check.
6. Return implementation status, spec bundle path, child artifacts, tests, deviations and decisions, review verdict, and remaining blockers. Commit only through `coding:commit` when the user requested a commit.

## Resume and completion

`--resume` loads existing handover/plan artifacts, verifies the pointer and working tree, and continues at the first incomplete contract step. Completion requires acceptance criteria evidence, passing relevant checks, a reviewed diff, and no unresolved blocking deviation.
