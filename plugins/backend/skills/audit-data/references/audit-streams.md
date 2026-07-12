# Audit Streams — Dispatch Prompts and Report Structure

Consulted by workflow step 3 (Dispatch the audit streams) for the three
blind-dispatch prompts and by step 4 for the AUDIT.md structure.

## Contents

- [Shared dispatch contract](#shared-dispatch-contract)
- [Stream 1 — schema audit](#stream-1--schema-audit)
- [Stream 2 — operation audit](#stream-2--operation-audit)
- [Stream 3 — controller audit](#stream-3--controller-audit)
- [AUDIT.md structure](#auditmd-structure)

## Shared dispatch contract

<IMPORTANT>
Each dispatch prompt contains ONLY: the spec path, the implementation
path(s), the output template path, and the applicable standards paths. Never
include the parent narrative, intent, or expected conclusions.
</IMPORTANT>

Every stream prompt opens with:

> You are an independent auditor. Treat the implementation as unfamiliar.
> Compare it against the spec and the listed standards. Do not assume the
> implementation matches the spec. This is a read-only audit. Do not modify
> any file.

## Stream 1 — schema audit

- **Spec**: [absolute path to entity spec export or DESIGN.md section]
- **Implementation**: [absolute path(s) to prisma/ schema files]
- **Output Template**: [absolute path to AUDIT.md schema-findings template]
- **Applicable Standards**: backend constitution `standards/data-entity.md`

**Report** (under 1000 tokens):

<report>

```yaml
status: success|failure|partial
outputs:
  models_checked: N
  missing_models: ['Model1', ...]
  orphaned_models: ['Model2', ...]
  field_mismatches: ['Model.field: expected X got Y', ...]
  missing_relations: ['Model1 -> Model2', ...]
issues: []
```

</report>

## Stream 2 — operation audit

- **Spec**: [absolute path to operation spec export or DESIGN.md section]
- **Implementation**: [absolute path(s) to src/operations/ and
  src/operations/index.ts]
- **Output Template**: [absolute path to AUDIT.md operation-findings template]
- **Applicable Standards**: backend constitution `standards/data-operation.md`

**Report** (under 1000 tokens):

<report>

```yaml
status: success|failure|partial
outputs:
  operations_checked: N
  missing_operations: ['op1', ...]
  extra_operations: ['op2', ...]
  pattern_violations: ['op3: wrong verb pattern', ...]
  missing_tests: ['op4: no int test', ...]
issues: []
```

</report>

## Stream 3 — controller audit

- **Spec**: [absolute path to controller spec export or DESIGN.md section]
- **Implementation**: [absolute path to source/index.ts and
  src/operations/index.ts]
- **Output Template**: [absolute path to AUDIT.md controller-findings
  template]
- **Applicable Standards**: backend constitution `standards/data-operation.md`
  and `standards/data-entity.md`

**Report** (under 1000 tokens):

<report>

```yaml
status: success|failure|partial
outputs:
  methods_checked: N
  missing_methods: ['method1', ...]
  extra_methods: ['method2', ...]
  pattern_violations: ['method3: wrong delegation', ...]
issues: []
```

</report>

## AUDIT.md structure

```markdown
# Data Audit: @theriety/data-{domain}
Date: [YYYY-MM-DD]

## Summary
- Entities audited: [count]
- Operations audited: [count]
- Controller methods: [count]
- Total findings: [count]
- Overall: [PASS/NEEDS_ATTENTION/CRITICAL]

## Schema Findings
| # | Severity | Entity | Finding | Recommendation |
|---|----------|--------|---------|----------------|
| 1 | critical | Offering | Missing field: quota | Add quota field to Prisma model |

## Operation Findings
| # | Severity | Operation | Finding | Recommendation |
|---|----------|-----------|---------|----------------|
| 1 | critical | getOffering | Missing int test | Add spec/operations/getOffering.spec.int.ts |

## Controller Findings
| # | Severity | Method | Finding | Recommendation |
|---|----------|--------|---------|----------------|
| 1 | warning | setOffering | Wrong delegation | Use Parameters<typeof op>[1] pattern |

## Code Quality
- Review: [summary]
- Lint: [N warnings]
- Unused code: [list]

## Decisions Required
- [ ] Finding #1: [accept/reject/defer]
```
