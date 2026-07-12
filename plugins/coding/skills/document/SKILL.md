---
name: document
description: Create or update a package README and optional ARCHITECTURE.md from the actual implementation. Use after meaningful code changes, when docs are missing or stale, or when a package needs a source-backed structure overview. Preserve existing project voice and route specification documentation to specification skills.
model: opus
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
argument-hint: "[--project=<path>] [--architecture|--no-architecture] [--readme-only] [--force-plan] [notes]"
---

# Document package

Produce accurate package documentation from code. This skill owns README and optional ARCHITECTURE.md artifacts; it does not author product specifications, Notion pages, or implementation changes.

## Inputs and boundaries

- Project resolution order: explicit `--project`, nearest workspace/package manifest containing the target, then repository root. In a monorepo, document only the selected package unless the selector is the workspace root.
- `--architecture` is on by default; `--no-architecture` and `--readme-only` disable it.
- `--force-plan` asks for an outline even when a local template or sibling README is authoritative.
- Optional notes may clarify audience or positioning but cannot override code evidence.
- Read package metadata, exports, entry points, scripts, configuration, and relevant source/tests. Never invent API behavior.

Reject a missing project root, unreadable source, or request to document a different package without changing the selector.

## Workflow

Load [references/authoring-rules.md](references/authoring-rules.md) for the
concrete drafting rules (section order, TOC discipline, Support Matrix, folder
notation, banned behaviors), the ARCHITECTURE tree/diagram/split rules, the
independent-review audit checklist, and the retry/rollback criteria.

1. Resolve the package/workspace and its anchors. Precedence is local explicit template/checklist, existing README/ARCHITECTURE structure, repository documentation rules, then closest same-archetype sibling. Use this skill's `references/README.template.md`, `ARCHITECTURE.template.md`, `package-types.md`, and one matching example only when repository anchors do not decide the shape.
2. Build an evidence map before drafting: manifest metadata, public exports, entry points, scripts, environment/configuration, tested examples, error behavior, dependency direction, and important source modules. Classify the package archetype (library, CLI, service, data/IaC, stateless app, or monorepo) and map each intended claim to a file or executable command.
3. Keep artifact ownership separate. README explains audience, installation, quick start, public usage/API, configuration, and links. ARCHITECTURE explains boundaries, components, runtime/data flow, dependency direction, extension points, and operational constraints; do not duplicate README tutorials.
4. Draft from the evidence map. Use real imports, commands, paths, inputs, outputs, and failure cases that were verified against code/tests. Never invent a convenience API. Preserve the existing voice and integrate updates into the owning sections.
5. Generate a table of contents only when the document benefits from one. Use `${CLAUDE_SKILL_DIR}/scripts/toc_width.py` for width calculations; never use a checkout-specific absolute path.
6. Create ARCHITECTURE.md when explicitly requested or when the package has multiple public/runtime entry points, cross-process or persistent data flow, meaningful dependency layering, or at least three cooperating components whose relationship is not clear from README. Otherwise omit it and state why.
7. Cross-check every claim, link, path, export, command, and dependency against evidence. Run documentation/build/test examples where safe. Delegate an independent read-only review for unsupported claims, wrong archetype, README/ARCH overlap, unusable examples, and stale text; apply corrections and rerun checks.

## Completion

Report project path and archetype, anchors/templates/examples used, evidence-map coverage, files written, architecture create/skip decision, commands/examples verified, independent-review verdict, stale claims removed, and unresolved gaps. Keep the output source-backed and concise; do not claim product or design decisions.
