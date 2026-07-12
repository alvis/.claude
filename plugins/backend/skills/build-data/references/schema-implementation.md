# Schema Implementation — Prisma Subagent Dispatch

Consulted by workflow step 2 (Implement the Prisma schema). One comprehensive
subagent implements all entity models for the domain.

## Dispatch prompt

<IMPORTANT>
The subagent performs the task itself; it must not delegate the work to
another subagent.
</IMPORTANT>

**Read the following assigned standards** and follow them recursively (when
standard A references standard B, read B too):

- plugin:coding:standard:documentation/write
- plugin:coding:standard:naming/write
- plugin:coding:standard:typescript/write
- standard:data-entity

**Assignment**: implement the Prisma schema for domain `{domain}` with
entities `{entity list}`.

**Steps**:

1. When a Notion URL is provided: fetch entity definitions from Notion
   (locate the Data Controllers database, find the controller page, extract
   the entity specs)
2. Validate the project structure (`prisma/` folder, `package.json`)
3. Translate each entity into Prisma schema model syntax
4. Write individual schema files with JSDoc documentation for every field
5. Ensure proper relationships, constraints, and indexes
6. Run `npx prisma generate` to create TypeScript types
7. Run `npm run build` to verify no breaking changes
8. Fix any compilation errors

**Report** (under 1000 tokens):

<report>

```yaml
status: success|failure|partial
summary: 'Schema implementation results'
modifications: ['entity1.prisma', ...]
outputs:
  entity_count: N
  entity_list: ['Entity1', ...]
  prisma_generation: success|failed
issues: []
```

</report>

## Review and decision

- Run a read-only schema validation review; a review subagent must not modify
  files.
- Proceed when the schemas are valid and `npx prisma generate` succeeded; on
  compilation errors, fix and re-dispatch (bound retries to 2, then report the
  remaining issues instead of looping).
