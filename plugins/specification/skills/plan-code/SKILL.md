---
name: plan-code
description: Build an implementation-ready plan from an approved specification inside an active engineering work item. Use to resolve the decision surface, define atomic implementation slices, and prepare verification without creating independent root planning or change artifacts.
model: opus
context: fork
allowed-tools: Read, Glob, Grep, Bash, Write, Task, TodoWrite, AskUserQuestion, ExitPlanMode
argument-hint: "--work-id=<id> [--spec=<path>] [--change=<description>]"
---

# Plan Code

Turn an approved work specification into a decision-complete implementation
blueprint stored with the active work item. `specification:spec-code` owns the
contract; `specification:implement-code` and Coding skills execute it.

## Boundaries

- Do not create independent root planning, proposal, or change artifacts.
- The complete work context and plan are summarized in `state.md`; detailed
  implementation slices live under `state/`. Proposals, changes, decisions,
  and design reasoning use the corresponding work-local child folders.
- `working.md` is a temporary current-focus summary, not the plan. Only the PM
  writes it and reconciles the four overview indexes.
- Do not implement source code, mutate history, or change authoritative MDC.

## Inputs

- **Required**: `--work-id=<id>` and an approved specification reachable from
  `.engineering/work/<work-id>/spec/` or a `sync-spec` materialization report.
- **Optional**: explicit spec path, focused change, discovery evidence, and
  current repository standards/architecture.

## Workflow

1. Before creating or materially rewriting a project artifact, read the
   absolute `engineering-work.md` path injected by Essential. If unavailable,
   stop artifact writes and report the missing contract. Resolve the active
   work root; read `working.md`, then `state.md`, then the materialization
   receipt and only the relevant spec sources.
2. Treat any legacy root design/draft/plan/proposed/change files as read-only
   migration inputs. Do not overwrite or delete them. Report ambiguous mapping
   for PM disposition.
3. Build the decision surface before implementation detail: data/migrations,
   public interfaces, user-visible flows, dependencies, security/privacy,
   integration boundaries, and acceptance criteria. Classify each as resolved,
   accepted reversible assumption with recheck trigger, deferred with owner and
   deadline, or blocking. Route discovery/decision work to the owning skills.
4. Ask only material unresolved questions. Once none block execution, write
   detailed lowercase artifacts as needed:
   - `decisions/<slug>.md` for a choice and consequences;
   - `proposals/<slug>.md` for an unapproved change;
   - `changes/<slug>.md` for an approved implementation/plan change;
   - `design/<slug>.md` for temporary task-specific technical design;
   - `state/implementation-plan.md` for ordered slices, dependencies,
     interfaces, tests, acceptance evidence, assumptions, and pivot signals.
   Ordinary work children always use an unnumbered semantic slug. Reserve
   `<nn>-<topic-slug>.md` for split output only; durable ADRs alone use
   `docs/architecture/decisions/<nnnn>-<decision-slug>.md`.
5. Make each implementation slice atomic and independently verifiable. Name
   its source targets, contract/acceptance references, implementation intent,
   test additions, repository gates, dependency order, and conventional commit
   intent. Include code only where an exact interface or migration shape is
   needed to prevent implementer choice; do not duplicate whole source files.
6. Dispatch one read-only reviewer with the authoritative spec, plan detail,
   decisions, and repository standards. It verifies complete acceptance/test
   mapping, architecture consistency, schema/API fidelity, executable order,
   and absence of hidden decisions. Resolve findings and review once more.
7. Return the complete `state.md` reconciliation payload and the four overview
   rows/status deltas to the PM. Do not directly edit PM-owned `state.md`,
   `working.md`, `proposals.md`, `changes.md`, `decisions.md`, or `design.md`.
8. Return explicit final paths generated or materially rewritten as
`generated_files`. Do not run file sizing; after every writer finishes, the PM
checks only eligible work Markdown inside the target `.engineering/`.

## Verification

- Every acceptance criterion maps to at least one implementation slice and one
  verification action.
- Every slice appears once, has dependency-safe order, and introduces no
  unresolved material decision.
- Temporary detail is work-local, legacy root files are untouched, and PM-owned
  indexes have explicit reconciliation data.
- The read-only quality gate passed and `generated_files` is complete.

## Completion

Report work id, authoritative spec/receipt, decisions and proposals created,
slice count and execution order, quality-gate result, legacy migration issues,
PM reconciliation payload, and `generated_files`. A refusal names the missing
spec, work state, repository, or blocking decision.
