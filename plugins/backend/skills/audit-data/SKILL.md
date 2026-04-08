---
name: audit-data
description: "Audit data orchestrators against specifications, generate discrepancy reports, and remediate approved changes. Use when reviewing data domain completeness, checking schema compliance, or performing data layer quality audits."
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: <domain-name> [--operation=...] [--entity=...] [--auto-fix]
---

# Audit Data

Audits data orchestrators against their Notion specifications, validates schema completeness, operation coverage, and controller alignment, generates discrepancy reports, and remediates approved changes by invoking `build-data`.

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Audit data orchestrators against their specifications to identify schema gaps, missing operations, controller mismatches, and coding standards violations, then remediate approved changes.
**When to use**:
- Reviewing data domain completeness after spec updates
- Validating Prisma schema alignment with Notion entity definitions
- Checking operation coverage for all declared entities
- Verifying controller methods match implemented operations
- Quality assurance before release

**Prerequisites**:
- Data orchestrator must exist as `@theriety/data-{domain}`
- Specification must be available in DESIGN.md or Notion
- Access to Notion workspace with Data Controllers database

**What this skill does NOT do**:
- Build new data orchestrators from scratch (use `build-data`)
- Create service packages (use `build-service`)
- Modify Notion specifications without user approval

### Your Role

You are a **Data Audit Director** who orchestrates like a database integrity auditor. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Systematic Schema Auditing**: Compare every Prisma model against Notion entity definitions
- **Operation Coverage Analysis**: Verify every entity has appropriate CRUD operations
- **Controller Alignment**: Ensure controller methods match implemented operations 1:1
- **Evidence-Based Reporting**: Every finding backed by specific file/line/model references

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **Domain Name**: The data domain to audit (maps to `@theriety/data-{domain}`)

#### Optional Inputs

- **Operation Filter**: Specific operation(s) for focused audit
- **Entity Filter**: Specific entity(ies) for focused audit
- **--auto-fix**: Automatically approve all findings

#### Expected Outputs

- **AUDIT.md**: Discrepancy report with schema/operation/controller findings
- **Updated Notion Spec**: Decisions synced back (if approved)
- **Remediated Code**: Fixes implemented via `build-data`
- **Compliance Status**: Pass/fail per entity and operation

#### Data Flow Summary

Load spec from Notion → audit schema, operations, controllers → generate AUDIT.md → collect user decisions → sync to Notion → remediate via build-data → final report.

### Visual Overview

```plaintext
  YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Load Spec] -------------> (Sub-skill: specification:sync-notion)
   |
   v
[Step 2: Audit vs Spec] ---------> (Subagents: 3 parallel streams)
   |                    +- Schema audit (Prisma vs Notion entities)
   |                    +- Operation audit (coverage + patterns)
   |                    +- Controller audit (method alignment)
   |                    +- coding:review + coding:lint + coding:find-unused
   v
[Step 3: Generate Report] --------- (You: compile AUDIT.md)
   |
   v
[Step 4: Decision Gate] ----------- (You: present findings, collect decisions)
   |
   v
[Step 5: Sync to Notion] --------> (Sub-skill: specification:sync-notion)
   |
   v
[Step 6: Remediate] -------------> (Sub-skill: backend:build-data)
   |
   v
[Step 7: Final Report] ----------- (You: compile summary)
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════
• Step 2: Three parallel audit streams for comprehensive coverage
• Step 6: Remediation via build-data (NOT build-service)
═══════════════════════════════════════════════════════════════
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. Step 1: Load Spec
2. Step 2: Audit vs Spec
3. Step 3: Generate Discrepancy Report
4. Step 4: Decision Gate
5. Step 5: Sync Decisions to Notion
6. Step 6: Implement Approved Changes
7. Step 7: Final Report

---

### Step 1: Load Spec

**Step Configuration**:

- **Purpose**: Fetch data domain specification from Notion
- **Input**: Domain name
- **Output**: Entity definitions, operation specs, controller expectations
- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/specification/skills/sync-notion/SKILL.md`
- **Parallel Execution**: No

#### Execute Sync Sub-Skill (You)

1. Load specification:sync-notion in **pull mode**
2. Search for Data Controllers database in Notion
3. Locate the controller page for the specified domain
4. Extract: entity definitions with attributes, operation specifications, relationship definitions
5. Continue to Step 2

---

### Step 2: Audit vs Spec

**Step Configuration**:

- **Purpose**: Validate schema, operations, and controllers against specification
- **Sub-skills**: `/Users/alvis/Repositories/.claude/plugins/coding/skills/review/SKILL.md`, `/Users/alvis/Repositories/.claude/plugins/coding/skills/lint/SKILL.md`, `/Users/alvis/Repositories/.claude/plugins/coding/skills/find-unused/SKILL.md`
- **Parallel Execution**: Yes (3 audit streams in parallel)

#### Phase 1: Planning (You)

1. **List all entities** from Notion spec
2. **List all operations** from Notion spec
3. **Read local codebase**: prisma schema, operations directory, controller class
4. **Create 3 audit streams**: schema, operations, controllers
5. **Apply filters** if specified

#### Phase 2: Execution (Subagents)

Spin up **3 parallel audit subagents**:

**Stream 1 — Schema Audit**:

    >>>
    **ultrathink: adopt the Schema Auditor mindset**

    **Assignment**: Compare Prisma schema against Notion entity definitions

    **Steps**:
    1. Read all Prisma schema files in `prisma/`
    2. Compare each model against corresponding Notion entity
    3. Check: missing fields, type mismatches, missing relations, missing indexes, missing constraints
    4. Check: orphaned models (in Prisma but not in Notion)
    5. Check: missing models (in Notion but not in Prisma)
    6. Verify JSDoc documentation on every field

    **Report** (<1000 tokens):
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
    <<<

**Stream 2 — Operation Audit**:

    >>>
    **ultrathink: adopt the Operation Coverage Auditor mindset**

    **Assignment**: Verify operation coverage and pattern compliance

    **Steps**:
    1. List all operations in `src/operations/`
    2. Compare against Notion operation specs
    3. Check: missing operations, extra operations, verb pattern compliance
    4. For each operation: verify type safety, error handling, selector usage
    5. Check barrel exports in `src/operations/index.ts`
    6. Verify test coverage: unit test exists, integration test exists

    **Report** (<1000 tokens):
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
    <<<

**Stream 3 — Controller Audit**:

    >>>
    **ultrathink: adopt the Controller Integration Auditor mindset**

    **Assignment**: Verify controller methods match operations 1:1

    **Steps**:
    1. Read controller class in `source/index.ts`
    2. List all public methods
    3. Compare against operations barrel exports
    4. Check: missing methods, extra methods, delegation pattern (`Parameters<typeof op>[1]` / `ReturnType<typeof op>`)
    5. Verify alphabetical ordering
    6. Check type re-exports

    **Report** (<1000 tokens):
    ```yaml
    status: success|failure|partial
    outputs:
      methods_checked: N
      missing_methods: ['method1', ...]
      extra_methods: ['method2', ...]
      pattern_violations: ['method3: wrong delegation', ...]
    issues: []
    ```
    <<<

Also execute in parallel: `coding:review`, `coding:lint`, `coding:find-unused`

#### Phase 4: Decision (You)

Consolidate all 3 audit streams + quality results → proceed to Step 3

---

### Step 3: Generate Discrepancy Report

**Step Configuration**:

- **Purpose**: Produce AUDIT.md
- **Parallel Execution**: No

#### Phase 1: Planning (You)

Generate AUDIT.md:

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

---

### Step 4: Decision Gate

Present AUDIT.md to user. Collect accept/reject/defer per finding. If `--auto-fix`: auto-accept all.

---

### Step 5: Sync Decisions to Notion

- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/specification/skills/sync-notion/SKILL.md`
- Execute in **push mode**

---

### Step 6: Implement Approved Changes

**Step Configuration**:

- **Purpose**: Remediate accepted findings
- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/backend/skills/build-data/SKILL.md`
- **Skip condition**: No accepted findings

#### Execute Build Sub-Skill (You)

1. Compile accepted schema changes, missing operations, and controller fixes into a domain extension spec
2. Load `/Users/alvis/Repositories/.claude/plugins/backend/skills/build-data/SKILL.md`
3. Execute in **extend mode** with the accepted changes

---

### Step 7: Final Report

```yaml
status: success|partial|failure
domain_name: '{domain}'
entities_audited: [count]
operations_audited: [count]
findings_total: [count]
findings_accepted: [count]
findings_rejected: [count]
findings_deferred: [count]
remediation_status: completed|partial|skipped
notion_synced: true|false
```

---

### Skill Completion

```yaml
status: success|partial|failure
domain_name: '{domain}'
audit_report: 'AUDIT.md'
schema_compliance:
  Entity1: pass|fail
  Entity2: pass|fail
operation_compliance:
  op1: pass|fail
  op2: pass|fail
controller_compliance: pass|fail
findings: [count]
remediated: [count]
deferred: [count]
```

## Examples

### Audit All

```bash
/audit-data "product"
# Audits schema, operations, and controller for the product domain
```

### Audit Specific Entity

```bash
/audit-data "product" --entity="Offering"
# Focus audit on the Offering entity only
```

### Auto-Fix Mode

```bash
/audit-data "vault" --auto-fix
# Accepts and implements all findings automatically
```
