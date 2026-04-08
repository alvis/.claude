---
name: build-service
description: "Build complete backend services from spec to commit, including operation declaration, implementation, and quality gates. Use when creating new services, adding operations to existing services, or declaring manifest schemas."
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: <service-name> <operations...> [--extend] [--notion-url=...]
---

# Build Service

Orchestrates the complete service creation/extension lifecycle from spec to commit. Absorbs manifest declaration and service implementation into a unified pipeline: spec discovery, operation declaration, project scaffolding, implementation, testing, quality gates, review, and commit.

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Build complete backend services following the `@theriety/service` architecture — from specification through manifest declaration, implementation, testing, quality verification, review, and commit.
**When to use**:
- Creating a new service package from scratch
- Adding operations, integrations, or webhooks to an existing service
- Declaring operation manifests with schema definitions
- Implementing a service defined in a DESIGN.md or Notion specification

**Prerequisites**:
- Domain entities identified (or `@theriety/data-{domain}` exists)
- Service operations specified (names + brief descriptions)
- For extend mode: existing `@theriety/service-{name}` package

**What this skill does NOT do**:
- Create data packages (use `build-data`)
- Perform only scaffolding without implementation (use `coding:draft-code`)
- Fix only test failures (use `coding:fix`)
- Audit existing services (use `audit-service`)

### Your Role

You are a **Service Delivery Director** who orchestrates like a construction project manager — ensuring foundations are laid before walls go up. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Sequential Integrity**: Each phase builds on the previous — manifests before scaffolding, scaffolding before implementation, implementation before testing
- **Mode Awareness**: Detect new vs extend mode early, skip irrelevant steps
- **Reference-Driven Quality**: Every subagent receives exact code patterns and reference file paths
- **Verification Gates**: No step proceeds without prior step's validation

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **Service Name**: kebab-case name (e.g., `notifications`, `billing`) — maps to `@theriety/service-{name}`
- **Operations List**: Array of operation names with brief descriptions

#### Optional Inputs

- **Data Domain**: The `@theriety/data-{domain}` package (default: auto-detect)
- **External Integrations**: Third-party APIs to integrate (e.g., Stripe, SendGrid)
- **Peer Services**: Other `@theriety/service-*` services this one calls
- **Webhooks**: External webhook handlers needed
- **Guards**: Authorization scopes and rules for `ensure()` calls
- **--extend flag**: Force extend mode
- **--notion-url**: Notion page with operation specifications

#### Expected Outputs

- **Manifest Package**: Complete `@theriety/manifest-{name}` with operation schemas (if new)
- **Service Package**: Complete `@theriety/service-{name}` package at `services/{name}/`
- **Test Suite**: Unit tests (`spec/**/*.spec.ts`) + integration tests (`spec/**/*.spec.int.ts`)
- **Verification Report**: typecheck + lint + test pass/fail results

#### Data Flow Summary

User provides service specification → Step 1 discovers/validates requirements → Step 2 declares operation manifests → Step 3 scaffolds service (new mode) → Step 4 implements operations → Step 5 runs quality gates → Step 6 reviews → Step 7 commits or hands over.

### Visual Overview

```plaintext
  YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Spec Discovery] -------- (You: parse inputs, detect mode, verify deps)
   |
   v
[Step 2: Declare Operations] ----> (Subagents: schema defs, manifest build, integration)
   |
   +-- new mode --+
   |              v
   |   [Step 3: Project Setup] --> (Sub-skill: coding:setup-project)
   |              |
   +-- extend ----+
   |
   v
[Step 4: Draft→Implement→Test] -> (Sub-skills: coding:draft-code → complete-code → complete-test)
   |                    +- Operations batch
   |                    +- Integrations batch
   |                    +- Webhooks batch
   v
[Step 5: Quality Gate] ---------> (Sub-skills: coding:fix + coding:lint + coding:refactor)
   |                                  Fix cycle (max 3)
   v
[Step 6: Review] ----------------> (Sub-skill: coding:review)
   |
   v
[Step 7: Commit Gate] -----------> (Sub-skill: coding:commit or coding:handover)
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute tasks in parallel
• ARROWS (───→): You assign work to subagents
• DECISIONS: You decide based on subagent reports
═══════════════════════════════════════════════════════════════
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. Step 1: Spec Discovery
2. Step 2: Declare Operations
3. Step 3: Project Setup (skip if extend mode)
4. Step 4: Draft → Implement → Test
5. Step 5: Quality Gate
6. Step 6: Review
7. Step 7: Commit Gate

---

### Step 1: Spec Discovery

**Step Configuration**:

- **Purpose**: Parse service specification, detect new/extend mode, verify dependencies, produce file manifest
- **Input**: User's service specification (name, operations, domain, integrations, peers, webhooks, guards)
- **Output**: Validated requirements object + file manifest + mode (new/extend)
- **Sub-skill**: (none — orchestrator performs directly)
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Parse inputs** from user request:
   - Service name (kebab-case)
   - Operations list with descriptions
   - Data domain name
   - External integrations, peer services, webhooks, guards (all optional)

2. **Detect mode**:
   - Run `ls /Users/alvis/Repositories/core/services/{name}/ 2>/dev/null`
   - If directory exists → **extend mode**
   - If not → **new mode**

3. **Verify packages exist**:
   - Run `ls /Users/alvis/Repositories/core/packages/manifest-{name}/ 2>/dev/null`
   - Run `ls /Users/alvis/Repositories/core/packages/data-{domain}/ 2>/dev/null`
   - If manifest missing and new mode → Step 2 will create it
   - If data package missing → STOP and inform user

4. **If Notion URL provided**, fetch operation specifications from Notion using MCP tools

5. **In extend mode**, read:
   - `services/{name}/src/index.ts` to identify existing operations
   - `services/{name}/package.json` to identify existing deps

6. **Produce file manifest** listing all files to create/modify

7. **Use TodoWrite** to create task list for all remaining steps

**OUTPUT**: Validated requirements + file manifest + mode

#### Phase 4: Decision (You)

1. If all dependencies verified → **PROCEED** to Step 2
2. If packages missing → **STOP** and ask user
3. If requirements ambiguous → **ASK** for clarification

---

### Step 2: Declare Operations

**Step Configuration**:

- **Purpose**: Create operation manifest schemas with type-safe definitions, mock implementations, and service integration
- **Input**: Validated requirements from Step 1
- **Output**: Complete manifest package with all operation schemas
- **Sub-skill**: (none — uses direct subagents following declare-service-operation patterns)
- **Parallel Execution**: Yes (schemas can be created in parallel)
- **Skip condition**: If all operations already have manifests (extend mode with existing ops)

#### Phase 1: Planning (You)

1. **Determine manifest project**: Check if `manifests/{name}/` exists
2. **If new manifest needed**, plan project structure:
   ```
   manifests/{name}/
   ├── package.json
   ├── source/
   │   ├── index.ts
   │   └── operations/
   │       └── {operationName}/
   │           ├── index.ts      # Operation manifest
   │           └── schema/
   │               ├── index.ts  # Schema exports + types
   │               ├── input.ts  # Input schema
   │               └── output.ts # Output schema (if not void)
   └── spec/
       └── index.spec.ts
   ```
3. **Create batches** — one per operation (max 10 per batch)
4. **Use TodoWrite** to track

#### Phase 2: Execution (Subagents)

Spin up subagents for schema creation, up to **3** at a time:

    >>>
    **ultrathink: adopt the Schema Definition Specialist mindset**

    - You're a **Schema Definition Specialist** with deep expertise in JSON Schema and TypeScript integration who follows these technical principles:
      - **Type Safety First**: Ensure all schemas compile to strict TypeScript types
      - **Validation Completeness**: Include all necessary validation rules and constraints
      - **Documentation Integration**: Every schema field must have clear descriptions

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Assignment**
    Create schema and manifest for operation: [OPERATION_NAME] in service: [SERVICE_NAME]

    **Steps**
    1. Create operation directory with camelCase naming under `manifests/{service}/source/operations/`
    2. Define input schema using `as const satisfies JsonSchema` pattern
    3. Define output schema (if operation returns data)
    4. Export TypeScript types using `FromSchema` pattern
    5. Create operation manifest with `createOperationManifest` including comprehensive mock
    6. Register operation in `source/index.ts` (alphabetical order)

    **Schema Patterns**:

    Input Schema:
    ```typescript
    import type { JsonSchema } from '@theriety/manifest';
    export default {
      type: 'object',
      additionalProperties: false,
      required: ['field1'],
      properties: { field1: { type: 'string', format: 'uuid', description: '...' } },
    } as const satisfies JsonSchema;
    ```

    Schema Export:
    ```typescript
    import input from './input';
    import output from './output';
    import type { FromSchema } from '@theriety/manifest';
    export type Input = FromSchema<typeof input>;
    export type Output = FromSchema<typeof output>;
    export default { input, output };
    ```

    Manifest:
    ```typescript
    import { createOperationManifest } from '@theriety/manifest';
    import schema from './schema';
    import type { Input, Output } from './schema';
    export default createOperationManifest({
      path: import.meta.url,
      schema,
      async: true,
      mock: async (input: Input): Promise<Output> => ({ /* realistic mock */ }),
    });
    ```

    **Report** (<1000 tokens):
    ```yaml
    status: success|failure|partial
    summary: 'Schema and manifest created for [operation]'
    modifications: ['schema/input.ts', 'schema/output.ts', 'schema/index.ts', 'index.ts']
    outputs:
      input_schema_created: true|false
      output_schema_created: true|false|not_required
      manifest_created: true|false
    issues: []
    ```
    <<<

#### Phase 3: Review (Subagents)

Review TypeScript compilation, schema format, FromSchema types, and requirements alignment (read-only).

#### Phase 4: Decision (You)

- **PROCEED** if schemas validated → Step 3
- **FIX ISSUES** if compilation failures → retry Phase 2

---

### Step 3: Project Setup

**Step Configuration**:

- **Purpose**: Scaffold the service directory tree with boilerplate files
- **Input**: Validated requirements from Step 1
- **Output**: Service directory with skeleton files
- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/coding/skills/setup-project/SKILL.md`
- **Parallel Execution**: No
- **Skip condition**: If extend mode, skip entirely

#### Execute Setup Sub-Skill (You)

1. Load `/Users/alvis/Repositories/.claude/plugins/coding/skills/setup-project/SKILL.md`
2. Execute with context specifying the `@theriety/service-{name}` package structure
3. After complete, continue to Step 4

---

### Step 4: Draft → Implement → Test

**Step Configuration**:

- **Purpose**: Create skeleton, fill implementations, and write comprehensive tests
- **Input**: Scaffold from Step 3 (or existing files in extend mode)
- **Output**: Fully implemented and tested source files
- **Sub-skills**: Sequential pipeline of 3 sub-skills
- **Parallel Execution**: Within each sub-skill, batches run in parallel

#### Execute Draft Sub-Skill (You)

1. Load `/Users/alvis/Repositories/.claude/plugins/coding/skills/draft-code/SKILL.md`
2. Execute with context specifying files to create with TODO placeholders:
   - Operations: `src/operations/{op-name}/index.ts` following `createOperation.opName` pattern
   - Integrations: `src/integrations/{system}/` directories (if any)
   - Webhooks: `src/webhooks/{system}.ts` files (if any)
   - Supporting files: `factory.ts`, `config.ts`, `client.ts`, `peer.ts`, `index.ts`

   Reference files:
   - `/Users/alvis/Repositories/core/services/billing/package.json` — package structure
   - `/Users/alvis/Repositories/core/services/product/src/factory.ts` — createServiceFactory pattern
   - `/Users/alvis/Repositories/core/services/atc/src/config.ts` — ServiceConfigSpecification
   - `/Users/alvis/Repositories/core/services/billing/src/client.ts` — ClientInitializer

3. After draft complete, load `/Users/alvis/Repositories/.claude/plugins/coding/skills/complete-code/SKILL.md`
4. Execute with context specifying implementation patterns:
   - Operations: `createOperation.opName(async (payload, { data, integration, emit }, { initiator }) => { ... })`
   - Use `ensure()` from `@theriety/core` for authorization
   - Use `retry()`, `RetryableError` for transient failures
   - Reference: `/Users/alvis/Repositories/core/services/product/src/operations/set-offering/index.ts`

5. After implementation complete, load `/Users/alvis/Repositories/.claude/plugins/coding/skills/complete-test/SKILL.md`
6. Execute with context specifying test patterns:

   | Aspect | Unit Tests (*.spec.ts) | Integration Tests (*.spec.int.ts) |
   |--------|------------------------|--------------------------------------|
   | Scope | Each operation + integration | End-to-end flows |
   | Data layer | vi.fn() mocks | **Real** action.data |
   | External APIs | vi.hoisted() + vi.mock() | **Real** API calls |
   | Internal services | N/A | **Mock** via vi.mock() |
   | Framework | operationMockFactory | Direct calls |

   Reference files:
   - `/Users/alvis/Repositories/core/services/product/spec/operations/set-offering.spec.ts` — unit test
   - `/Users/alvis/Repositories/core/services/billing/spec/integrations/stripe/invoice.spec.ts` — integration test

---

### Step 5: Quality Gate

**Step Configuration**:

- **Purpose**: Fix issues, lint, and refactor for production quality
- **Input**: Implemented service from Step 4
- **Output**: Clean, production-ready code
- **Sub-skills**: `/Users/alvis/Repositories/.claude/plugins/coding/skills/fix/SKILL.md`, `/Users/alvis/Repositories/.claude/plugins/coding/skills/lint/SKILL.md`, `/Users/alvis/Repositories/.claude/plugins/coding/skills/refactor/SKILL.md`
- **Parallel Execution**: No (sequential — fix first, then lint, then refactor)

#### Execute Quality Sub-Skills (You)

1. Load and execute `coding:fix` — resolve any failing tests or type errors (max 3 cycles)
2. Load and execute `coding:lint` — apply coding standards
3. Load and execute `coding:refactor` — improve code quality and maintainability
4. After all complete, verify with `pnpm typecheck && pnpm lint && pnpm test`

---

### Step 6: Review

**Step Configuration**:

- **Purpose**: Comprehensive code review before commit
- **Input**: Quality-gated code from Step 5
- **Output**: Review report with approval or required changes
- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/coding/skills/review/SKILL.md`
- **Parallel Execution**: No

#### Execute Review Sub-Skill (You)

1. Load `/Users/alvis/Repositories/.claude/plugins/coding/skills/review/SKILL.md`
2. Execute review covering: correctness, patterns, security, test coverage
3. If review finds issues → loop back to Step 5
4. If review passes → proceed to Step 7

---

### Step 7: Commit Gate

**Step Configuration**:

- **Purpose**: Commit changes or create handover notes
- **Input**: Reviewed code from Step 6
- **Output**: Git commit or handover document
- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/coding/skills/commit/SKILL.md` or `/Users/alvis/Repositories/.claude/plugins/coding/skills/handover/SKILL.md`
- **Parallel Execution**: No

#### Phase 4: Decision (You)

1. **If all verification passed and review approved** → execute `coding:commit`
2. **If issues remain or user prefers manual review** → execute `coding:handover`

---

### Skill Completion

**Report the skill output as specified**:

```yaml
status: success|failure|partial
service_name: '{name}'
mode: new|extend
package_path: '/Users/alvis/Repositories/core/services/{name}/'
manifest_path: '/Users/alvis/Repositories/core/manifests/{name}/'
operations_declared: ['op1', 'op2', ...]
operations_implemented: ['op1', 'op2', ...]
integrations_implemented: ['system1', ...] # if any
webhooks_implemented: ['system1', ...] # if any
tests:
  unit_tests: [count]
  integration_tests: [count]
verification:
  typecheck: pass|fail
  lint: pass|fail
  test: pass|fail
review: pass|fail
commit: committed|handed-over
issues: ['remaining issue 1', ...] # if any
```

## Standards

- **TypeScript** (plugin:coding:standard:typescript) — Type safety and strict mode
- **Naming** (plugin:coding:standard:naming) — Consistent naming for operations, schemas, types
- **Documentation** (plugin:coding:standard:documentation) — Schema descriptions and code comments
- **Functions** (plugin:coding:standard:function) — Function structure and patterns
- **Testing** (plugin:coding:standard:testing) — Test patterns, mock rules, coverage requirements
- **Universal** (plugin:coding:standard:universal) — DRY, SRP, and fundamental principles

## Examples

### Create a New Service

```bash
/build-service notifications --operations "send-email: Send transactional email" "send-push: Send push notification" --domain comms --integrations sendgrid --webhooks sendgrid
```

### Extend an Existing Service

```bash
/build-service billing --operations "create-refund: Process a refund" --extend
```

### With Notion Spec

```bash
/build-service auth --operations "verify-token: Verify JWT" --notion-url="https://notion.so/..."
```
