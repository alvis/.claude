---
name: document
description: Create or update a package README and optional ARCHITECTURE.md from the actual implementation. Use after meaningful code changes, when docs are missing or stale, or when a package needs a source-backed structure overview. Preserve existing project voice and route specification documentation to specification skills.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
argument-hint: "[--project=<path>] [--architecture|--no-architecture] [--readme-only] [--force-plan] [notes]"
---

# Document package

Produce accurate package documentation from code. This skill owns README and optional ARCHITECTURE.md artifacts; it does not author product specifications, Notion pages, or implementation changes.

## Inputs and boundaries

- Project defaults to the nearest package root with `package.json`; accept an explicit path.
- `--architecture` is on by default; `--no-architecture` and `--readme-only` disable it.
- `--force-plan` asks for an outline even when a local template or sibling README is authoritative.
- Optional notes may clarify audience or positioning but cannot override code evidence.
- Read package metadata, exports, entry points, scripts, configuration, and relevant source/tests. Never invent API behavior.

Reject a missing project root, unreadable source, or request to document a different package without changing the selector.

## Workflow

1. Resolve the package and locate its README template, checklist, sibling package examples, exports, CLI entry points, scripts, environment requirements, and architecture signals. Prefer repository scripts for discovery and validation.
2. Plan only when no template or sibling README exists (or `--force-plan` is set). Otherwise follow the authoritative structure: overview, install, quick start, usage, API/commands, configuration, architecture, and verification as applicable.
3. Draft claims against observed files. Include executable commands, real paths, public exports, failure behavior, and a short architecture map. Omit sections with no evidence; move deep examples to references when available.
4. Write README.md and, when enabled, ARCHITECTURE.md. Preserve valid existing content, fold changes into its owning section, and remove stale claims rather than appending an update log.
5. Cross-check every path, command, export, and dependency against the source. Run the package's documentation/build/test checks when configured and report limitations.

## Completion

Report project path, files written, source evidence reviewed, commands verified, stale claims removed, and unresolved documentation gaps. Keep the output source-backed and concise; do not claim product or design decisions.
