# Backend workflow

Read this before schema, data-model, pipeline, service, API, or ML/AI work. Use the owning skill, then follow the standards named for that action.

## Actions

| Action | Instruction |
| --- | --- |
| Build or extend a schema, data model, controller, or pipeline | `backend:build-data` |
| Audit data schemas, operations, migrations, or pipelines | `backend:audit-data` |
| Build or extend a service or API | `backend:build-service` |
| Audit a service against its specification | `backend:audit-service` |
| Materialize or synchronize an implementation specification | `specification:sync-spec` |
| Write, test, review, save, or publish code | Read `coding:references/WORKFLOW.md`, then use its action owner |
| Create or materially rewrite project artifacts | Follow the injected `essential:references/engineering-work.md` contract |

Before work delegation, read `backend:references/ROUTING.md`.

## Standards

Read every file in a listed standards directory, following its cross-references.

| Applies to | Standards |
| --- | --- |
| Entity and schema work | `backend:constitution/standards/data-entity.md` |
| Data operations, controllers, and repositories | `backend:constitution/standards/data-operation.md` |
| TypeScript backend code | `coding:constitution/standards/universal/`, `coding:constitution/standards/function/`, `coding:constitution/standards/typescript/`, `coding:constitution/standards/naming/`, `coding:constitution/standards/testing/`, and `coding:constitution/standards/documentation/` |
| Errors, logging, and operational behavior | `coding:constitution/standards/observability/` |
| Python ML/AI code | `coding:constitution/standards/universal/`, `coding:constitution/standards/function/`, `coding:constitution/standards/python/`, `coding:constitution/standards/testing/`, and `coding:constitution/standards/observability/` |
| Review | `coding:constitution/standards/code-review.md` plus the implementation standards above |
| Files and project setup | `coding:constitution/standards/file-structure.md` |
| Commits, branches, and pull requests | `coding:constitution/standards/git/` |
