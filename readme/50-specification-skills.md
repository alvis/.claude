# specification skills (depends on: coding, essential)

[Back to marketplace overview](../README.md#plugins-and-skills)

Design specifications, architecture specs, requirements gathering, and technical documentation with Notion integration for knowledge management

This catalog is generated from the plugin manifest and each skill's `SKILL.md` frontmatter. Run `python3 scripts/generate_readme.py` after changing either source.

- `specification:implement-code` — Execute an approved specification work item from authoritative Notion-backed contract through delegated coding, review, completion sync, and durable derivation. Use after plan-code approval, when resuming partial work, or when auditing delivered ticket work.
- `specification:mdc` — Read, edit, and author Notion-backed MDC files safely with native text tools while preserving @theriety/mdc grammar and ref identity. Use for any authored .mdc body change. Keep transport, pairing, and conflict orchestration in sync-notion and sync-spec.
- `specification:plan-code` — Build an implementation-ready plan from an approved specification inside an active engineering work item. Use to resolve the decision surface, define atomic implementation slices, and prepare verification without creating independent root planning or change artifacts.
- `specification:review-implementation` — Review implementation against an authoritative work-local or Notion specification, coordinate the seven canonical review areas, and summarize dispositions in the active work item. Use for alignment, ticket validation, omissions, drift, and unsanctioned behavior.
- `specification:spec-code` — Design, update, or retrospectively document a technical specification through an active engineering work item, Notion-backed MDC, and versioned derived docs. Use for specification authoring; keep transport in sync-notion and implementation planning in plan-code.
- `specification:sync-notion` — Synchronize paired local files and Notion pages in a declared direction, including recursive pulls, verified pushes, and explicit two-way conflict resolution. Own Notion transport and pairing; keep specification orchestration in sync-spec and authored MDC edits in mdc.
- `specification:sync-spec` — Materialize a required Notion specification into an active engineering work directory or complete approved specification changes through the default-workspace mirror. Use before specification planning, implementation, or review and when closing a work item. Delegate transport and conflicts to sync-notion.
