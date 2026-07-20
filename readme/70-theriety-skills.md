# theriety skills (depends on: coding, specification, essential)

[Back to marketplace overview](../README.md#plugins-and-skills)

Domain-specific service and data orchestrator lifecycle management for Theriety — build and audit services and data layers

This catalog is generated from the plugin manifest and each skill's `SKILL.md` frontmatter. Run `python3 scripts/generate_readme.py` after changing either source.

- `theriety:audit-data` — Audit a data orchestrator against its work-local authoritative specification and the canonical review taxonomy, then remediate explicitly approved gaps. Use for schema, operation, controller, testing, and data-layer quality review; keep service audits in audit-service.
- `theriety:audit-service` — Audit a backend service against its work-local authoritative specification and canonical review areas, with optional approved remediation. Use for implementation, operation completeness, documentation, semantic, security, testing, and quality audits.
- `theriety:build-data` — Build or extend a data orchestrator from an approved work-local specification through schema, operations, controller integration, tests, canonical review, and handoff. Use for new data domains, operations, or Prisma schemas; keep audits in audit-data.
- `theriety:build-service` — Build or extend a backend service from an approved work-local specification through manifests, implementation, tests, canonical review, and handoff. Use for new services, operations, integrations, webhooks, or manifest schemas; keep audits in audit-service.
