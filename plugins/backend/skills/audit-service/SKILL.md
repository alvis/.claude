---
name: audit-service
description: "Audit backend services against specifications, generate discrepancy reports, and remediate approved changes. Use when reviewing service completeness, checking spec compliance, or performing service quality audits."
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: <service-name> [--operation=...] [--area=...] [--auto-fix]
---

# Audit Service

Audits backend services against their Notion specifications, validates operation completeness and coding standards compliance, generates discrepancy reports, and remediates approved changes by invoking `build-service`.

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Audit backend services against their specifications to identify gaps, generate actionable discrepancy reports, sync decisions to Notion, and remediate approved changes.
**When to use**:
- Reviewing service operations for standards compliance before release
- Validating completeness after specification updates
- Conducting quality assurance on service operation documentation
- Checking operation manifest alignment with Notion specs

**Prerequisites**:
- Service must exist as `@theriety/service-{name}` or `@theriety/manifest-{name}`
- Specification must be available in DESIGN.md or Notion
- Access to Notion workspace with Services and Service Operations databases

**What this skill does NOT do**:
- Build new services from scratch (use `build-service`)
- Create data packages (use `build-data`)
- Modify Notion specifications without user approval

### Your Role

You are a **Service Audit Director** who orchestrates like a quality assurance executive overseeing comprehensive service reviews. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Systematic Auditing**: Methodically compare implementation against specification
- **Evidence-Based Reporting**: Every finding backed by specific file/line references
- **User-Driven Remediation**: Present findings and wait for user decisions before fixing
- **Traceability**: Every change tracked from spec → finding → decision → implementation

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **Service Name**: The name of the service to audit (maps to `@theriety/service-{name}`)

#### Optional Inputs

- **Operation Filter**: Specific operation name(s) for focused audit (default: all operations)
- **Area Filter**: Functional domain filter (default: all areas)
- **--auto-fix**: Automatically approve and implement all findings (default: interactive)

#### Expected Outputs

- **AUDIT.md**: Comprehensive discrepancy report with per-operation findings
- **Updated Notion Spec**: Decisions synced back to Notion (if approved)
- **Remediated Code**: Implemented fixes for approved changes (via `build-service`)
- **Compliance Status**: Pass/fail for each operation

#### Data Flow Summary

Load spec from Notion → audit each operation against spec → generate AUDIT.md → present findings to user → sync decisions to Notion → remediate approved changes → final report.

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
[Step 2: Audit vs Spec] ---------> (Subagents: validate operations in parallel batches)
   |                    +- coding:review
   |                    +- coding:lint
   |                    +- coding:find-unused
   |                    +- Operation completeness check
   v
[Step 3: Generate Report] --------- (You: compile AUDIT.md)
   |
   v
[Step 4: Decision Gate] ----------- (You: present findings, collect user decisions)
   |
   v
[Step 5: Sync to Notion] --------> (Sub-skill: specification:sync-notion)
   |
   v
[Step 6: Remediate] -------------> (Sub-skill: backend:build-service)
   |
   v
[Step 7: Final Report] ----------- (You: compile summary)
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════
• Steps 1,5: Notion sync via specification plugin
• Step 2: Parallel validation subagents
• Step 6: Remediation via build-service
• Steps 3,4,7: Orchestrator decisions
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

- **Purpose**: Fetch service specification from Notion
- **Input**: Service name
- **Output**: Complete spec with operations list, data operations, service context
- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/specification/skills/sync-notion/SKILL.md`
- **Parallel Execution**: No

#### Execute Sync Sub-Skill (You)

1. Load `/Users/alvis/Repositories/.claude/plugins/specification/skills/sync-notion/SKILL.md`
2. Execute in **pull mode** to fetch the latest spec from Notion
3. Extract: service metadata, all service operation pages, data operation dependencies
4. Continue to Step 2

---

### Step 2: Audit vs Spec

**Step Configuration**:

- **Purpose**: Validate each operation against its specification for completeness and standards compliance
- **Input**: Spec from Step 1 + local service codebase
- **Output**: Per-operation validation results
- **Sub-skills**: `/Users/alvis/Repositories/.claude/plugins/coding/skills/review/SKILL.md`, `/Users/alvis/Repositories/.claude/plugins/coding/skills/lint/SKILL.md`, `/Users/alvis/Repositories/.claude/plugins/coding/skills/find-unused/SKILL.md`
- **Parallel Execution**: Yes (operations validated in parallel, max 2 at a time)

#### Phase 1: Planning (You)

1. **List all operations** from the spec
2. **Apply filters** (operation filter, area filter) if specified
3. **Discover service** by searching Notion for the Services database, locating the service page, extracting operation metadata
4. **Create batches** (max 2 operations per batch)
5. **Use TodoWrite** to track

#### Phase 2: Execution (Subagents)

Spin up validation subagents, up to **2** at a time:

    >>>
    **ultrathink: adopt the Service Operation Validator mindset**

    - You're a **Service Operation Validator** with deep expertise in service operation documentation who follows these technical principles:
      - **Standards Compliance**: Rigorously validate against coding and documentation standards
      - **Completeness Verification**: Ensure all required sections are present and complete
      - **Consistency Checking**: Verify alignment between use cases, requirements, and pseudo code
      - **Quality Assurance**: Identify gaps and provide actionable recommendations

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively:
    - documentation.md
    - observability/scan.md
    - typescript.md
    - function/scan.md
    - universal/scan.md

    **Assignment**
    Validate this service operation:
    - **Operation**: [operation name and ID]
    - **Service Context**: [service context from discovery]
    - **Data Operations Available**: [list from discovery]

    **Steps**
    1. **Fetch Operation Content**: Use Notion fetch to retrieve complete operation page
    2. **Validate Use Cases**: Verify documented use cases exist, check sync block alignment
    3. **Check Requirements**: Verify input parameters, output interfaces, functional requirements
    4. **Validate Pseudo Code**: Check structure follows `createOperation` pattern:
       ```typescript
       import { createOperation } from '#factory';
       export default createOperation.<operationName>(
         async ({ input }, { verifyAccess, data: { entity }, integration: { lib }, service: { self, other } }) => {
           verifyAccess(`<resource>:<identifier>:<action>`);
           const result = await entity.dataOperation({ params });
           return result;
         },
       );
       ```
    5. **Verify Data Operations**: Compare pseudo code data calls with Data Operations field
    6. **Check Requirements Alignment**: Ensure use cases covered by requirements
    7. **Validate Permissions**: Verify permission checks match permission field
    8. **Assess Code-Requirements Consistency**: Confirm logic implements all requirements

    **Validation Criteria**:
    - Use Cases: At least one documented, sync block alignment checked
    - Requirements: Input params with types, output interfaces, functional requirements
    - Pseudo Code: Import order, naming conventions, TypeScript strict typing, lowercase comments
    - Data Operations: PascalCase in field → camelCase in code mapping verified
    - [IMPORTANT] DO NOT complain about template placeholders in use case section
    - [IMPORTANT] Pseudo code is meant to be incomplete — focus on business logic

    **Report** (<1000 tokens):
    ```yaml
    status: success|failure|partial
    summary: 'Validation completed for [operation]'
    modifications: []
    outputs:
      operation_name: '[name]'
      validation_status: 'pass|issues_found'
      issues_found: ['issue with location and fix', ...]
      recommendations: ['improvement', ...]
    issues: []
    ```
    <<<

**Issue Escalation**: When issues found, pause further validation, present detailed report with code snippets and fix suggestions, await user approval before continuing.

Also execute in parallel:
- `coding:review` — code quality review of the service package
- `coding:lint` — lint check
- `coding:find-unused` — dead code detection

#### Phase 4: Decision (You)

1. Collect all validation reports
2. Consolidate into per-operation findings
3. Categorize by functional domain
4. **PROCEED** to Step 3

---

### Step 3: Generate Discrepancy Report

**Step Configuration**:

- **Purpose**: Produce AUDIT.md with consolidated findings
- **Input**: All validation results from Step 2
- **Output**: AUDIT.md file
- **Sub-skill**: (none — orchestrator compiles)
- **Parallel Execution**: No

#### Phase 1: Planning (You)

Generate AUDIT.md with this structure:

```markdown
# Service Audit: @theriety/service-{name}
Date: [YYYY-MM-DD]

## Summary
- Operations audited: [count]
- Issues found: [count]
- Overall status: [PASS/NEEDS_ATTENTION/CRITICAL]

## Operations by Domain

### [Domain Group]

#### ✅ [Operation Name] — PASS
No issues found.

#### ❌ [Operation Name] — ISSUES FOUND
| # | Severity | Category | Finding | Recommendation |
|---|----------|----------|---------|----------------|
| 1 | critical | Pseudo Code | Missing error handling | Add MissingDataError check |
| 2 | warning | Requirements | Input type incomplete | Add constraints for field X |

## Code Quality
- Review: [summary]
- Lint: [N warnings]
- Unused code: [list]

## Decisions Required
- [ ] Finding #1: [accept/reject/defer]
- [ ] Finding #2: [accept/reject/defer]
```

---

### Step 4: Decision Gate

**Step Configuration**:

- **Purpose**: Present findings and collect user decisions
- **Input**: AUDIT.md from Step 3
- **Output**: User decisions per finding (accept/reject/defer)
- **Parallel Execution**: No

#### Phase 4: Decision (You)

1. Present AUDIT.md to user
2. For each finding, collect: **accept** (will fix), **reject** (won't fix), **defer** (later)
3. If `--auto-fix` flag: auto-accept all findings
4. Record decisions for Step 5

---

### Step 5: Sync Decisions to Notion

**Step Configuration**:

- **Purpose**: Update Notion spec with audit decisions
- **Input**: User decisions from Step 4
- **Output**: Updated Notion pages
- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/specification/skills/sync-notion/SKILL.md`
- **Parallel Execution**: No

#### Execute Sync Sub-Skill (You)

1. Load sync-notion sub-skill
2. Execute in **push mode** to sync decisions back to Notion
3. Continue to Step 6

---

### Step 6: Implement Approved Changes

**Step Configuration**:

- **Purpose**: Remediate accepted findings using build-service
- **Input**: Accepted findings from Step 4
- **Output**: Implemented fixes
- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/backend/skills/build-service/SKILL.md`
- **Parallel Execution**: No
- **Skip condition**: If no findings accepted, skip to Step 7

#### Execute Build Sub-Skill (You)

1. Compile list of accepted changes into a service extension specification
2. Load `/Users/alvis/Repositories/.claude/plugins/backend/skills/build-service/SKILL.md`
3. Execute in **extend mode** with the accepted changes
4. Continue to Step 7

---

### Step 7: Final Report

**Step Configuration**:

- **Purpose**: Compile final audit summary
- **Input**: Results from all previous steps
- **Output**: Final report to user
- **Parallel Execution**: No

#### Phase 4: Decision (You)

Compile and present:

```yaml
status: success|partial|failure
service_name: '{name}'
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
service_name: '{name}'
audit_report: 'AUDIT.md'
operations_audited: ['op1', 'op2', ...]
compliance_status:
  op1: pass|fail
  op2: pass|fail
findings: [count]
remediated: [count]
deferred: [count]
```

## Examples

### Audit All Operations

```bash
/audit-service "billing"
# Audits all operations in the billing service against Notion spec
```

### Audit Specific Operation

```bash
/audit-service "billing" --operation="create-checkout-session"
```

### Auto-Fix Mode

```bash
/audit-service "product" --auto-fix
# Accepts and implements all findings automatically
```
