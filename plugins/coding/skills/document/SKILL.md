---
name: document
description: Create or update source-backed package usage documentation and durable architecture documentation. Use after meaningful code changes, when docs are missing or stale, or when a package needs an architecture overview under docs/architecture; route specifications and Notion content to specification skills.
model: opus
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
argument-hint: "[--project=<path>] [--architecture|--no-architecture] [--readme-only] [--force-plan] [notes]"
---

# Document package

Produce accurate package documentation from code. This skill owns package
`readme.md` content and durable `docs/architecture/*.md` artifacts; it does not
author product specifications, Notion pages, or implementation changes.

## Boundaries

- Use for: creating or refreshing a package `readme.md`, adding source-backed durable
  architecture documentation, and realigning documentation after code changes.
- Do not use for: product specifications or Notion documentation (specification skills), implementation changes, or documenting a package other than the resolved selector.
- Never invent API behavior: every claim must trace to package metadata, exports, entry points, scripts, configuration, or relevant source/tests.
- Reject a missing project root, unreadable source, or a request to document a different package without changing the selector.

## Inputs

- **Required**: none — the project resolves from the working directory. Resolution order: explicit `--project`, nearest workspace/package manifest containing the target, then repository root. In a monorepo, document only the selected package unless the selector is the workspace root.
- **Optional**: `--architecture` is on by default; `--no-architecture` and `--readme-only` disable it. `--force-plan` asks for an outline even when a local template or sibling README is authoritative. Free-form notes may clarify audience or positioning but cannot override code evidence.
- **Prerequisites**: readable package metadata, exports, entry points, scripts, configuration, and relevant source/tests.

## Engineering-work gate

Before creating or materially rewriting a project artifact, read the absolute
`engineering-work.md` path injected by Essential. If unavailable, stop artifact
writes and report the missing contract. Resolve or mint the work ID/root by the
contract. When delegated, read `working.md`, then `state.md` and only its
relevant source/spec/design links; never write PM-owned `working.md` or work
overview files.

## Workflow

Load [references/authoring-rules.md](references/authoring-rules.md) for the
concrete drafting rules (section order, TOC discipline, Support Matrix, folder
notation, banned behaviors), the ARCHITECTURE tree/diagram/split rules, the
independent-review audit checklist, and the retry/rollback criteria.

1. Resolve the package/workspace and its anchors. Precedence is local explicit
   template/checklist, existing `readme.md` and `docs/architecture/` structure,
   repository documentation rules, then closest same-archetype sibling. Use
   this skill's bundled templates and one matching example only when repository
   anchors do not decide the shape. A bundled template/example entrypoint may
   be a split manifest; when it is, load every linked child in manifest order
   before drafting.
2. When `--force-plan` is set, or neither a repository anchor nor a bundled template decides the document shape, propose a section outline with a one-line rationale per section and wait for user approval before drafting.
3. Build an evidence map before drafting: manifest metadata, public exports, entry points, scripts, environment/configuration, tested examples, error behavior, dependency direction, and important source modules. Classify the package archetype (library, CLI, service, data/IaC, stateless app, or monorepo) and map each intended claim to a file or executable command.
4. Keep artifact ownership separate. `readme.md` explains audience, installation,
   quick start, public usage/API, configuration, and links. A durable
   `docs/architecture/<architecture-slug>.md` explains boundaries, components,
   runtime/data flow, dependency direction, extension points, and operational
   constraints; do not duplicate usage tutorials. Compute links relative to
   the package `readme.md` rather than assuming the documents are siblings.
   New files use lowercase names. If only a legacy uppercase README exists, do
   not create a duplicate: report the compatibility migration and rename it
   with all links atomically only when repository evidence makes that safe.
5. Draft from the evidence map. Use real imports, commands, paths, inputs, outputs, and failure cases that were verified against code/tests. Never invent a convenience API. Preserve the existing voice and integrate updates into the owning sections.
6. Generate a table of contents only when the document benefits from one. Use `${CLAUDE_SKILL_DIR}/scripts/toc_width.py` for width calculations; never use a checkout-specific absolute path.
7. Create or update `docs/architecture/<architecture-slug>.md` when explicitly
   requested or when the package has multiple public/runtime entry points,
   cross-process or persistent data flow, meaningful dependency layering, or
   at least three cooperating components whose relationship is not clear from
   `readme.md`. Use Essential's `derive-engineering-name` helper and repository capability,
   not a task title. Reconcile `docs/architecture/overview.md` and
   `docs/index.md`; individual architectural choices remain ADRs under
   `docs/architecture/decisions/`.
8. Run the verification below; when a check fails, fix the cause and re-run that check. Repeat until every check passes or a concrete blocker remains, then report the blocker instead of looping. Decide review outcomes per the criteria in references/authoring-rules.md (proceed, targeted retry with at most two attempts per issue, or rollback).

## Verification

- Every documented export, command, environment variable, path, link, and dependency exists in the evidence map and matches the source.
- Documentation/build/test examples were executed where safe, and each ran as documented.
- An independent read-only review (delegated) found no unsupported claims,
  wrong archetype, README/architecture overlap, unusable examples, stale text,
  or broken durable-index links.
- Any generated table of contents was produced with `toc_width.py`, not by hand.

## Completion

Report project path and archetype, anchors/templates/examples used, evidence-map
coverage, architecture create/skip decision, commands/examples verified,
independent-review verdict, stale claims removed, and unresolved gaps. Return
every created or materially rewritten final path as `generated_files`. Do not
measure or split `docs/**` or project README files: durable documentation has no
mechanical size limit. The PM size-checks only eligible work Markdown inside
the target `.engineering/` after all artifact writers finish.
