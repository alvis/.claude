---
name: build-data
description: "Build complete data orchestrators from spec to commit, including schema setup, operations, controllers, and quality gates. Use when creating new data domains, adding operations to existing orchestrators, or implementing Prisma schemas from Notion."
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task, TodoRead, TodoWrite, Skill
argument-hint: <domain-name> <operations...> [--extend] [--notion-url=...]
---

# Build Data

Orchestrates the complete data orchestrator creation/extension lifecycle from spec to commit. Absorbs schema implementation, operation implementation, controller integration, and the orchestrator TDD pipeline into a unified workflow.

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Build complete data orchestrators following the `@theriety/data` architecture — from specification through Prisma schema setup, operation implementation, controller integration, testing, quality verification, review, and commit.
**When to use**:
- Creating a new data orchestrator package from scratch
- Adding operations to an existing data orchestrator
- Implementing Prisma schemas from Notion entity definitions
- Implementing data operations from Notion specifications
- Integrating operations into data controllers

**Prerequisites**:
- Domain entities identified with Prisma schema models (or Notion entity definitions)
- `@theriety/data` and `@theriety/core` packages available in the workspace
- Operations specified with verb prefixes (get/list/set/drop/resolve/attach/detach/initiate)

**What this skill does NOT do**:
- Create service packages (use `build-service`)
- Create manifest packages (those are for services)
- Audit existing data layers (use `audit-data`)

### Your Role

You are a **Data Architecture Director** who orchestrates like a database migration planner — ensuring schemas are defined before operations, and operations before tests. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Sequential Integrity**: Each phase builds on the previous — schemas before types, types before selectors, selectors before operations
- **Mode Awareness**: Detect new vs extend mode early, skip irrelevant steps
- **Pattern Compliance**: Every operation follows one of 8 verb patterns exactly
- **Verification Gates**: No step proceeds without prior step's validation

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **Domain Name**: kebab-case name (e.g., `product`, `vault`) — maps to `@theriety/data-{domain}`
- **Operations List**: Array of operations with verb prefix. Valid verbs: `get`, `list`, `set`, `drop`, `resolve`, `attach`, `detach`, `initiate`
- **Entities List**: Domain entities (e.g., `offering`, `suite`, `tariff`)

#### Optional Inputs

- **--extend flag**: Force extend mode
- **--notion-url**: Notion page with entity/operation specifications
- **Selector Pattern**: `simple` (single `selectors.ts`) or `complex` (co-located `entities/*.ts`)

#### Expected Outputs

- **Data Package**: Complete `@theriety/data-{domain}` at `data/{domain}/`
- **Prisma Schema**: Entity models with relationships and constraints
- **Operations**: Type-safe data operations following verb patterns
- **Controller**: Class with delegating methods for each operation
- **Test Suite**: Unit tests (mocked Prisma) + integration tests (real DB)
- **Verification Report**: typecheck + lint + test results

#### Data Flow Summary

User provides domain specification → Step 1 discovers requirements → Step 2 implements Prisma schema → Step 3 scaffolds project (new mode) → Step 4 builds orchestrator (types, selectors, operations, factory) → Step 5 implements individual operations → Step 6 integrates controller → Step 7 quality gate → Step 8 review → Step 9 commit.

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
[Step 2: Schema Setup] ----------> (Subagents: Notion entities → Prisma schema → generate types)
   |
   +-- new mode --+
   |              v
   |   [Step 3: Project Setup] --> (Sub-skill: coding:setup-project)
   |              |
   +-- extend ----+
   |
   v
[Step 4: Build Orchestrator] ----> (Sub-skills: coding:draft-code → complete-code → complete-test)
   |                    +- Types + Selectors
   |                    +- Operations
   |                    +- Factory
   v
[Step 5: Implement Operations] --> (Subagents: per-operation implementation + tests)
   |
   v
[Step 6: Implement Controllers] -> (Subagents: controller class integration)
   |
   v
[Step 7: Quality Gate] ---------> (Sub-skills: coding:fix + coding:lint + coding:refactor)
   |
   v
[Step 8: Review] ----------------> (Sub-skill: coding:review)
   |
   v
[Step 9: Commit Gate] -----------> (Sub-skill: coding:commit or coding:handover)
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════
• Steps 2,5,6: Domain-specific subagents with Theriety patterns
• Steps 3,4,7-9: Coding plugin sub-skills
• Step 1: Orchestrator planning
═══════════════════════════════════════════════════════════════
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. Step 1: Spec Discovery
2. Step 2: Schema Setup
3. Step 3: Project Setup (skip if extend mode)
4. Step 4: Build Orchestrator
5. Step 5: Implement Operations
6. Step 6: Implement Controllers
7. Step 7: Quality Gate
8. Step 8: Review
9. Step 9: Commit Gate

---

### Step 1: Spec Discovery

**Step Configuration**:

- **Purpose**: Parse domain specification, detect mode, verify dependencies, determine selector pattern
- **Input**: User's domain specification
- **Output**: Validated requirements + file manifest + mode
- **Sub-skill**: (none)
- **Parallel Execution**: No

#### Phase 1: Planning (You)

1. **Parse inputs**: domain name, operations list (with verb validation), entities list, selector pattern
2. **Detect mode**: Check `ls /Users/alvis/Repositories/core/data/{domain}/`
3. **Verify packages**: `@theriety/data` and `@theriety/core` must exist
4. **Validate operation verbs**: Must start with get/list/set/drop/resolve/attach/detach/initiate
5. **Determine selector pattern**: simple (≤3 entities) or complex (>3 entities)
6. **In extend mode**: read existing factory, operations barrel, package.json
7. **If Notion URL provided**: fetch entity definitions and operation specifications
8. **Produce file manifest** and **TodoWrite** to track all steps

#### Phase 4: Decision (You)

- **PROCEED** if all verified → Step 2
- **STOP** if packages missing or invalid verbs

---

### Step 2: Schema Setup

**Step Configuration**:

- **Purpose**: Implement Prisma schema models from entity definitions (from Notion or user input)
- **Input**: Entity definitions from Step 1
- **Output**: Prisma schema files with generated TypeScript types
- **Sub-skill**: (none — uses domain-specific subagents)
- **Parallel Execution**: No

#### Phase 2: Execution (Subagents)

Spin up **1** comprehensive subagent:

    >>>
    **ultrathink: adopt the Data Implementation Architect mindset**

    - You're a **Data Implementation Architect** with deep expertise in Prisma schema design and TypeScript

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively:
    - plugin:coding:standard:documentation/write
    - plugin:coding:standard:naming/write
    - plugin:coding:standard:typescript/write
    - standard:data-entity

    **Assignment**
    Implement Prisma schema for domain: [{domain}] with entities: [{entity list}]

    **Steps**
    1. If Notion URL provided: fetch entity definitions from Notion (locate Data Controllers database, find controller page, extract entity specs)
    2. Validate project structure (prisma/ folder, package.json)
    3. Translate each entity into Prisma schema model syntax
    4. Write individual schema files with JSDoc documentation for every field
    5. Ensure proper relationships, constraints, and indexes
    6. Run `npx prisma generate` to create TypeScript types
    7. Run `npm run build` to verify no breaking changes
    8. Fix any compilation errors

    **Report** (<1000 tokens):
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
    <<<

#### Phase 3: Review (Subagents) — read-only schema validation

#### Phase 4: Decision (You)

- **PROCEED** if schemas valid → Step 3 (new) or Step 4 (extend)
- **FIX ISSUES** if compilation errors

---

### Step 3: Project Setup

**Step Configuration**:

- **Purpose**: Scaffold the data orchestrator directory tree
- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/coding/skills/setup-project/SKILL.md`
- **Skip condition**: If extend mode, skip entirely

#### Execute Setup Sub-Skill (You)

Execute with the `@theriety/data-{domain}` package structure including:
- package.json with imports map (#prisma, #types, #operations/*, #*)
- vitest configs (unit + integration)
- prisma/ directory
- src/ with operations/, types/, optional entities/ or selectors.ts
- spec/ with orchestrator.ts, fixture.ts, operations/

Reference: `/Users/alvis/Repositories/core/data/product/` for simple, `/Users/alvis/Repositories/core/data/vault/` for complex

---

### Step 4: Build Orchestrator

**Step Configuration**:

- **Purpose**: Implement types, selectors, operations, and factory
- **Sub-skills**: `/Users/alvis/Repositories/.claude/plugins/coding/skills/draft-code/SKILL.md` → `/Users/alvis/Repositories/.claude/plugins/coding/skills/complete-code/SKILL.md` → `/Users/alvis/Repositories/.claude/plugins/coding/skills/complete-test/SKILL.md`

#### Execute Sub-Skills (You)

1. **Draft** with `coding:draft-code` — create TODO-placeholder files for all operation verbs, types, selectors, factory
2. **Implement** with `coding:complete-code` — fill implementations following verb patterns:
   - **get**: `findUnique` + `MissingDataError`
   - **list**: `findMany` with filter/cursor/sort
   - **set**: upsert with `CreateInput | UpdateInput`
   - **drop**: status-based soft/hard delete
   - **resolve**: priority-based fallback matching
   - **attach/detach**: junction record management
   - **initiate**: idempotent upsert with nested relations

   Reference files per verb in `/Users/alvis/Repositories/core/data/`

3. **Test** with `coding:complete-test` — write unit tests (mocked Prisma) + integration tests (real DB)

   Unit test pattern (mocked Prisma, NOT operationMockFactory):
   ```typescript
   const client = {
     entity: { findUnique: vi.fn(async () => entity) },
   } satisfies PartialDeep<PrismaClient> as PartialDeep<PrismaClient> as PrismaClient;
   ```

   Integration test pattern (real DB):
   ```typescript
   beforeEach(async () => { await setup(); });
   it('should return entity', async () => {
     const result = await orchestrator.getEntity({ slug: 'test' });
     expect(result).toMatchObject({ slug: 'test' });
   });
   ```

---

### Step 5: Implement Operations

**Step Configuration**:

- **Purpose**: Implement individual data operations with types, error handling, and Notion spec alignment
- **Input**: Operation specs from Step 1
- **Output**: Implemented operations in `operations/{operationName}.ts`
- **Sub-skill**: (none — uses domain-specific subagents)
- **Parallel Execution**: Yes (up to 3 batches)

#### Phase 2: Execution (Subagents)

    >>>
    **ultrathink: adopt the Data Operation Implementation Expert mindset**

    **Read the following assigned standards** and follow them recursively:
    - plugin:coding:standard:documentation/write
    - plugin:coding:standard:function/write
    - plugin:coding:standard:testing/write
    - plugin:coding:standard:typescript/write
    - standard:data-operation

    **Assignment**: Implement operations: [list]

    **Steps** (per operation):
    1. Implement operation function with types in `operations/{operationName}.ts`
    2. Write integration tests in `spec/operations/{operationName}.spec.int.ts`
    3. Follow patterns: types at top of file, selectors from `#selectors`, `MissingDataError` for not-found
    4. Controller integration: `Parameters<typeof op>[1]` / `ReturnType<typeof op>` delegation pattern

    **Report** (<1000 tokens):
    ```yaml
    status: success|failure|partial
    modifications: ['operations/op.ts', 'spec/operations/op.spec.int.ts', 'source/index.ts']
    outputs:
      operations_implemented: ['op1', 'op2']
      test_count: N
    issues: []
    ```
    <<<

---

### Step 6: Implement Controllers

**Step Configuration**:

- **Purpose**: Integrate all operations into the controller class
- **Input**: Implemented operations from Step 5
- **Output**: Updated controller with delegating methods
- **Sub-skill**: (none — uses subagent)
- **Parallel Execution**: No

#### Phase 2: Execution (Subagents)

    >>>
    **Assignment**: Update controller in `source/index.ts`

    **Controller Pattern**:
    ```typescript
    import { getEntity } from '#operations/getEntity';
    export class DomainName {
      #client: PrismaClient;
      public async getEntity(
        input: Parameters<typeof getEntity>[1],
      ): ReturnType<typeof getEntity> {
        return getEntity(this.#client, input);
      }
    }
    ```

    Add methods for ALL new operations in alphabetical order.
    <<<

---

### Step 7: Quality Gate

**Step Configuration**:

- **Sub-skills**: `/Users/alvis/Repositories/.claude/plugins/coding/skills/fix/SKILL.md`, `/Users/alvis/Repositories/.claude/plugins/coding/skills/lint/SKILL.md`, `/Users/alvis/Repositories/.claude/plugins/coding/skills/refactor/SKILL.md`

Execute sequentially: fix → lint → refactor → verify with `pnpm typecheck && pnpm lint && pnpm test`

---

### Step 8: Review

- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/coding/skills/review/SKILL.md`

If review finds issues → loop back to Step 7. If passes → Step 9.

---

### Step 9: Commit Gate

- **Sub-skill**: `/Users/alvis/Repositories/.claude/plugins/coding/skills/commit/SKILL.md` or `/Users/alvis/Repositories/.claude/plugins/coding/skills/handover/SKILL.md`

---

### Skill Completion

```yaml
status: success|failure|partial
domain_name: '{domain}'
mode: new|extend
package_path: '/Users/alvis/Repositories/core/data/{domain}/'
package_name: '@theriety/data-{domain}'
entities: ['entity1', ...]
selector_pattern: simple|complex
operations_implemented: ['op1', ...]
tests:
  unit_tests: [count]
  integration_tests: [count]
verification:
  typecheck: pass|fail
  lint: pass|fail
  test: pass|fail
review: pass|fail
commit: committed|handed-over
issues: []
```

## Standards Compliance

- **TYP-IMPT-01/02**: Import ordering, type imports separated
- **TYP-CORE-03**: No `as unknown as` — use `satisfies PartialDeep<T>` bridge
- **FUNC-SIGN-01/02**: Explicit return types, ≤2 positional params
- **TST-MOCK-03/04/05/09**: Mock patterns (vi.fn, no beforeEach mocks, satisfies, no as unknown as)
- **TST-STRU-02/03**: File layout, AAA blank lines
- **TST-CORE-03**: `should` in it(), `op:`/`fn:` in describe()

## Examples

### Create a New Data Orchestrator

```bash
/build-data inventory --operations "get-item: Retrieve by id" "list-items: Filter items" "set-item: Create/update" "drop-item: Deactivate" --entities item category
```

### Extend with Notion Spec

```bash
/build-data product --operations "resolve-tariff: Find best tariff" --extend --notion-url="https://notion.so/..."
```

### Implement Schema Only

```bash
/build-data vault --entities dek kek --notion-url="https://notion.so/..."
```
