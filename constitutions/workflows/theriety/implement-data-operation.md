# Implement Data Operation

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Implement a database operation that handles data logic without business logic, based on a Notion specification, ensuring type safety and consistency
**When to use**: When implementing a new data operation, when requirements are documented in a Notion specification page, when extending existing data controller with new operations
**Prerequisites**: Notion page ID containing the data operation specification, understanding of data logic vs business logic separation, familiarity with Prisma and TypeScript, access to the project's database schema, knowledge of existing data controller patterns in the monorepo

### Your Role

You are a **Data Operations Orchestrator** who coordinates the implementation like a technical project director. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break implementation into parallel tasks for type definitions, operations, and tests
- **Parallel Coordination**: Run multiple subagents simultaneously for independent implementation tasks
- **Quality Oversight**: Review specifications and implementations without coding directly
- **Decision Authority**: Make architectural decisions based on subagent analysis and Notion requirements
- **Standards Enforcement**: Ensure all subagents follow data operation patterns and coding standards

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Data Controller Notion Page Name or ID**: Name or id of the target data controller where schemas will be implemented, or
- **Project Repository Path**: Local file system path to the data controller project repository

#### Optional Inputs

- **Notion Data Controller Database ID**: Unique identifier of the Notion page containing all data controller pages, including target controller page
- **Data Operation Filter List**: Specific operations names to implement (default: all operations in the Notion specification)

#### Expected Outputs

- **Operation Function**: Implemented data operation in `operations/{operationName}.ts`
- **Integration Tests**: Comprehensive test suite in `spec/operations/{operationName}.spec.ts`
- **Updated Controller**: Controller class with new operation method exported
- **Documentation**: JSDoc comments and type exports for external consumption
- **Completion Report**: Summary of implementation with links to Notion spec and test results

#### Data Flow Summary

The workflow takes a Notion specification ID, retrieves the requirements, and produces a fully tested data operation implementation with type-safe interfaces. The operation is integrated into the data controller and made available for service layer consumption.

### Visual Overview

#### Main Workflow Flow

```plaintext
  YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
   |
   v
[START]
   |
   v
[Step 1: Implement Data Operation] ─→ (Complete implementation with validation, specification retrieval, and parallel batches)
   |               ├─ Batch A: Max 10 operations (Types, Core Logic)     ─┐
   |               ├─ Batch B: Max 10 operations (Tests, Integration)    ─┼─→ [Decision: Proceed?]
   |               └─ Batch C: Max 10 operations (Controller, Validation) ─┘
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute tasks in parallel
• ARROWS (───→): You assign work to subagents
• DECISIONS: You decide based on subagent reports
═══════════════════════════════════════════════════════════════════

Note: 
• You: Lists resources, batches work, assigns tasks, makes decisions
• Execution Subagents: Perform actual work, report back (<1k tokens)
• Verification Subagents: Check quality when needed (<500 tokens)
• Workflow is LINEAR: Single step with validation in Planning Phase
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Implement Data Operation

### Step 1: Implement Data Operation

**Step Configuration**:

- **Purpose**: Complete data operation implementation including validation, specification retrieval, types, operations, tests, and controller integration
- **Input**: All workflow inputs (Notion page ID/name, project path, operation filters)
- **Output**: Fully implemented and tested data operation integrated into controller
- **Sub-workflow**: None
- **Parallel Execution**: Yes - multiple batches with max 10 operations per subagent

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive and process inputs** from workflow initiation:
   - Data Controller Notion Page Name or ID
   - Project Repository Path
   - Optional Notion Data Controller Database ID
   - Optional Data Operation Filter List

2. **Handle Notion Page Lookup** (if name provided instead of ID):
   - Search for "Data Controllers" database in Notion using search tools
   - Fetch the database to get list of all data controller pages
   - Find the controller page that matches the provided name
   - Extract the controller page ID for subsequent operations
   - If no match found, REJECT workflow with error message

3. **Validate Project Structure** (REJECT workflow if validation fails):
   - Check if provided project repository path exists on filesystem
   - Verify existence of `prisma/` folder in project directory
   - Validate required data controller structure:

   ```plaintext
   data/{service}/
   ├── source/           # Must exist
   ├── spec/            # Must exist  
   ├── prisma/          # Must exist (critical validation)
   │   └── schema.prisma # Must exist
   └── package.json     # Must exist
   ```

4. **Fetch and Analyze Notion Specification**:
   - Retrieve the Notion page using the resolved page ID
   - Extract all operation names and ids

5. **Create Implementation Batches** following these rules:
   - Generate batches based on discovered operations and implementation tasks
   - Limit each batch to max 10 operations
   - Assign specialized subagents to each batch

6. **Use TodoWrite** to create task list from all batches (each batch = one todo item)

7. **Prepare comprehensive task assignments** for parallel execution

**OUTPUT from Planning**: Implementation batch assignments with validated inputs

**Rejection Messages**:

- "Target project directory does not exist: [path]"
- "Prisma schema not implemented: missing prisma/ folder in [path]"  
- "Required project structure incomplete: missing [specific requirements]"
- "Data Controllers database not found in Notion"
- "Controller page '[name]' not found in Data Controllers database"

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, you spin up subagents to perform implementation batches in parallel, up to **3** batches at a time.

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

```yaml
**ultrathink: adopt the Data Operation Implementation Expert mindset**

- You're a **Data Operation Implementation Expert** with deep expertise in full-stack data operation development who follows these technical principles:
  - **End-to-End Implementation**: Handle complete feature implementation from types to tests
  - **Type Safety First**: Leverage TypeScript's type system fully  
  - **Pattern Consistency**: Follow established operation patterns from existing codebase
  - **Error Resilience**: Comprehensive error handling with MissingDataError patterns
  - **Test Excellence**: Complete test coverage with integration testing

**Read the following assigned standards** and follow them recursively:

- @../../standards/coding/typescript.md
- @../../standards/coding/error-handling-logging.md
- @../../standards/coding/documentation.md
- @../../standards/coding/functions.md
- @../../standards/coding/backend/data-operation.md
- @../../standards/coding/testing.md

**Assignment**
You're assigned with the following implementation batch (max 10 operations):

- [operation name and id from Planning Phase]
- ...

**Implementation Patterns to Follow** (copy these exact patterns):

1. **Type Definition Pattern** - Define types directly in operation files:

   ```typescript
   // operations/setOffering.ts (types at top of file)
   import type { SetOptional, SetRequired } from 'type-fest';
   import type { OfferingAttribute } from '#types';
   
   /** input parameters for setOffering */
   export type SetOfferingInput = CreateOfferingInput | UpdateOfferingInput;
   export type CreateOfferingInput = SetOptional<
     Omit<OfferingAttribute, 'slug'>,
     'id'
   >;
   export type UpdateOfferingInput = SetRequired<
     Partial<Omit<OfferingAttribute, 'slug'>>,
     'id'
   >;
   ```

   For simple get/drop operations, use interfaces:

   ```typescript
   // operations/getOffering.ts
   /** input parameters for getOffering */
   export type GetOfferingInput =
     | { /** unique identifier */ id: string }
     | { /** unique slug */ slug: string };
   ```

1. **Operation Function Pattern** - Copy this exact structure:

   ```typescript
   // operations/getOffering.ts (GET pattern)
   import { MissingDataError } from '@theriety/error';
   import { offeringAttributeSelector, offeringSummarySelector } from '#selectors';
   import type { PrismaClient } from '#prisma';
   import type { Offering } from '#types';
   
   /**
    * retrieves an offering based on the provided criteria
    * @param client the Prisma client instance
    * @param input collection of input parameters
    * @param input.id unique identifier or slug of the offering
    * @returns a promise that resolves to an offering
    * @throws MissingDataError if the offering is not found
    */
   export async function getOffering(
     client: PrismaClient,
     input: GetOfferingInput,
   ): Promise<Offering> {
     const offering = await client.offering.findUnique({
       ...offeringAttributeSelector,
       where: input,
       include: {
         ancestors: offeringSummarySelector,
         descendants: offeringSummarySelector,
       },
     });

     if (!offering) {
       throw new MissingDataError('offering not found', { meta: input });
     }

     return { ...offering };
   }
   ```

   ```typescript
   // operations/setOffering.ts (SET pattern with upsert)
   import { ValidationError } from '@theriety/error';
   import slugify from 'slug';
   import { normalize } from '#utilities';
   import type { PrismaClient } from '#prisma';
   import type { Offering } from '#types';

   /**
    * sets an offering based on the provided data
    * @param client the Prisma client instance
    * @param input either complete data for creation or partial data for update
    * @returns a promise that resolves to the created or updated offering
    */
   export async function setOffering(
     client: PrismaClient,
     input: SetOfferingInput,
   ): Promise<Offering> {
     const { status, suiteId, parentId, features, display } = input;
     const slug = display?.en.name ? slugify(display.en.name) : undefined;

     const data = {
       status, suiteId, parentId, features, display, slug,
       quota: normalize(input.quota),
       rate: normalize(input.rate),
     };

     return client.offering.upsert({
       where: { slug: input.id },
       update: data,
       create: { ...data, slug: slug ?? input.id },
       include: { ancestors: offeringSummarySelector },
     });
   }
   ```

   ```typescript
   // operations/dropOffering.ts (DROP pattern with status-based logic)
   import { MissingDataError } from '@theriety/error';
   import { offeringSummarySelector } from '#selectors';
   import type { PrismaClient } from '#prisma';
   import type { OfferingSummary } from '#types';

   /** input parameters for dropOffering */
   export interface DropOfferingInput {
     /** unique identifier of the offering */
     id: string;
   }

   /**
    * remove or mark an offering as inactive
    * @param client the Prisma client instance
    * @param input collection of input parameters
    * @param input.id unique identifier of the offering (slug)
    * @returns the summary of the removed offering
    */
   export async function dropOffering(
     client: PrismaClient,
     { id }: DropOfferingInput,
   ): Promise<OfferingSummary> {
     const offering = await client.offering.findUnique({ where: { slug: id } });

     if (!offering) {
       throw new MissingDataError('offering not found', { meta: { id } });
     }

     if (offering.status === 'active') {
       // Mark as inactive
       return client.offering.update({
         select: offeringSummarySelector.select,
         data: { status: 'inactive' },
         where: { slug: id },
       });
     } else if (offering.status === 'inactive') {
       // Already inactive, return as is
       return { /* return existing data */ };
     } else {
       // Delete draft offerings
       return client.offering.delete({
         select: offeringSummarySelector.select,
         where: { slug: id, status: 'draft' },
       });
     }
   }
   ```

1. **Selectors Pattern** - All selectors in single `selectors.ts` file:

   ```typescript
   // source/selectors.ts
   import type { Prisma } from '#prisma';

   export const offeringAttributeSelector = {
     select: {
       id: true,
       slug: true,
       status: true,
       suiteId: true,
       features: true,
       display: true,
       quota: true,
       rate: true,
     } as const satisfies Prisma.OfferingSelect,
   } as const;

   export const offeringSummarySelector = {
     select: {
       id: true,
       slug: true,
       status: true,
       suiteId: true,
       display: true,
     } as const satisfies Prisma.OfferingSelect,
   } as const;
   ```

1. **Controller Integration Pattern** - Add this exact method structure:

   ```typescript
   // source/index.ts
   import { getOffering } from '#operations/getOffering';
   import { setOffering } from '#operations/setOffering';
   import { dropOffering } from '#operations/dropOffering';
   import { listOfferings } from '#operations/listOfferings';
   
   export class Product {
     #client: PrismaClient;
     
     /**
      * retrieves an offering based on the provided criteria
      * @param input collection of input parameters
      * @param input.slug unique identifier of the offering
      * @returns a promise that resolves to an offering
      * @throws MissingDataError if the offering is not found
      */
     public async getOffering(
       input: Parameters<typeof getOffering>[1],
     ): ReturnType<typeof getOffering> {
       return getOffering(this.#client, input);
     }

     /**
      * sets an offering based on the provided data
      * @param input either complete data for creation or partial data for update
      * @returns a promise that resolves to the created or updated offering
      */
     public async setOffering(
       input: Parameters<typeof setOffering>[1],
     ): ReturnType<typeof setOffering> {
       return setOffering(this.#client, input);
     }

     /**
      * lists offerings based on the provided filter criteria
      * @param input collection of input parameters
      * @returns a promise that resolves to an array of offering summaries
      */
     public async listOfferings(
       input?: Parameters<typeof listOfferings>[1],
     ): ReturnType<typeof listOfferings> {
       return listOfferings(this.#client, input);
     }
   }
   ```

1. **Integration Test Pattern** - Copy this test structure:

   ```typescript
   // spec/operations/setOffering.spec.int.ts
   import { beforeEach, describe, expect, it } from 'vitest';
   
   import { instance } from '../common';
   import setup from '../fixture';
   
   import type { Offering } from '#types';
   
   beforeEach(async () => {
     await setup();
   });
   
   describe('op:setOffering', () => {
     it('should create a new offering when id does not exist', async () => {
       const input = {
         id: 'new-test-offering',
         status: 'draft' as const,
         suiteId: 'draft-suite',
         display: {
           en: {
             name: 'New Test Offering',
             description: 'A newly created test offering',
           },
         },
         features: ['new-feature-1', 'new-feature-2'],
         quota: {},
         rate: {},
       };

       const expected: Partial<Offering> = {
         slug: 'new-test-offering',
         status: 'draft',
         suiteId: 'draft-suite',
       };

       const result = await instance.setOffering(input);

       expect(result).toMatchObject(expected);
       expect(result.features).toEqual(['new-feature-1', 'new-feature-2']);
     });

     it('should update an existing offering when id already exists', async () => {
       const input = {
         id: 'draft-offering',
         status: 'active' as const,
         display: {
           en: {
             name: 'Updated Draft Offering',
             description: 'An updated draft offering',
           },
         },
       };

       const expected: Partial<Offering> = {
         slug: 'updated-draft-offering',
         status: 'active',
       };

       const result = await instance.setOffering(input);

       expect(result).toMatchObject(expected);
     });
   });
   ```

   **Note**: Integration tests use `beforeEach` to call a setup fixture that resets and seeds the database.
   For simpler unit tests of utilities, use the direct pattern without setup:

   ```typescript
   // spec/utilities/normalize.spec.ts
   import { describe, expect, it } from 'vitest';
   import { normalize } from '#utilities/normalize';
   
   describe('fn:normalize', () => {
     it('should convert null values to Prisma.DbNull', () => {
       const result = normalize(null);
       expect(result).toBe(Prisma.DbNull);
     });
   });
   ```

**Execution Steps** (follow this exact sequence):

1. **Implement Operation Function with Types**: Create `operations/{operationName}.ts` file with:
   - Type definitions at the top of the file (not in separate types/operations.ts)
   - Use union types for set operations (Create | Update)
   - Use simple interfaces/types for get/drop/list operations
   - Function implementation following patterns above
   - Import selectors from `#selectors`

2. **Write Integration Tests**: Create `spec/operations/{operationName}.spec.int.ts`:
   - Use `beforeEach(async () => { await setup(); })` for database reset
   - Import `instance` from `../common` and use controller methods
   - Test create, update, error cases, and edge scenarios
   - Use `toMatchObject` for partial matching

3. **Integrate into Controller**: Update `source/index.ts`:
   - Import operation function from `#operations/{operationName}`
   - Add public method using Parameters/ReturnType utilities
   - Include proper JSDoc matching the operation function

4. **Update Package Exports**: Ensure the operation types are exported from main types

5. **Run Tests**: Execute `npm test` or test command for the service

6. **Validate Implementation**: Verify against Notion specification compliance

**Report**
**[IMPORTANT]** You're requested to return the following:

- Complete implementation status with all patterns applied
- All files created or modified
- Test coverage and pass status
- Integration completeness with controller

**[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

```yaml
status: success|failure|partial
summary: 'Implemented complete data operation [operation] with established patterns'
modifications: ['operations/setOffering.ts', 'spec/operations/setOffering.spec.int.ts', 'source/index.ts', 'source/selectors.ts']
outputs:
  operation_name: 'setOffering'
  input_type: 'SetOfferingInput' 
  output_type: 'Offering'
  test_count: 8
  test_coverage: '100%'
  controller_integrated: true
  selector_pattern_used: true
  types_in_operation_file: true
  integration_test_pattern: true
  pattern_compliance: true
issues: []  # only if problems encountered
```

#### Phase 3: Review (Subagents)

In a single message, you spin up review subagents to check quality, up to **2** review tasks at a time.

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources or fix issues
- **[IMPORTANT]** Review subagents ONLY report issues and provide recommendations - they do not implement fixes
- **[IMPORTANT]** You MUST ask review subagents to be thorough and critical in their analysis
- **[IMPORTANT]** Use TodoWrite to track review tasks separately from execution tasks

Request each review subagent to perform the following review with full scrutiny:

```yaml
**ultrathink: adopt the Data Operation QA Expert mindset**

- You're a **Data Operation QA Expert** with expertise in comprehensive review who follows these principles:
  - **Specification Compliance**: Review against original Notion requirements
  - **Pattern Adherence**: Check established patterns are followed correctly
  - **Integration Completeness**: Ensure all components work together seamlessly
  - **Test Coverage Excellence**: Review comprehensive testing with edge cases
  - **Review-Only Role**: Identify issues and provide recommendations without making any changes

**Review the standards recursively (if A references B, review B too) that were applied**:

- @../../standards/coding/typescript.md - Review type safety and strict mode compliance
- @../../standards/coding/documentation.md - Review JSDoc completeness
- @../../standards/coding/functions.md - Review pure function patterns
- @../../standards/coding/backend/data-operation.md - Check data vs business logic separation
- @../../standards/coding/testing.md - Review testing standards compliance

**Review Assignment**
You're assigned to review the following resources that were modified:

1. Read all modified files to understand complete implementation
2. Compare implementation against original Notion specification
3. Review compliance with each assigned standard and established patterns
4. Check test coverage includes all scenarios and edge cases
5. Review controller integration follows pass-through pattern
6. Ensure no business logic mixed with data operations
7. Confirm error handling uses MissingDataError appropriately
8. **IMPORTANT**: Do NOT make any changes or fixes - only report issues found

**Report**
**[IMPORTANT]** You're requested to review and report:

- Specification compliance status
- Standards adherence for each category  
- Pattern consistency with existing codebase
- Test coverage adequacy and edge case handling
- Integration completeness
- Any critical issues or recommendations

**[IMPORTANT]** You MUST return the following review report (<500 tokens):


```yaml
status: pass|fail
summary: 'Complete data operation review with pattern compliance'
checks:
  spec_compliance: pass|fail
  type_safety: pass|fail
  pattern_consistency: pass|fail
  error_handling: pass|fail
  test_coverage: pass|fail
  controller_integration: pass|fail
  documentation: pass|fail
  no_business_logic: pass|fail
critical_issues: []  # Only critical blockers
warnings: []  # Non-blocking issues  
recommendation: proceed|retry|rollback
```

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze all reports** (execution + review)
2. **Apply decision criteria**:
   - Review any critical failures from implementation batches
   - Consider review recommendations
   - Check completion status of all implementation components
   - Validate pattern consistency with existing codebase
3. **Select next action**:
   - **PROCEED**: All success or acceptable partial success → Mark workflow complete
   - **FIX ISSUES**: Partial success with minor issues → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
   - **ROLLBACK**: Critical failures → Revert changes → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark remaining 'in_progress' items as 'completed'
   - If FIX ISSUES: Add new todo items for retry batches with failed items
   - If ROLLBACK: Mark all items as 'failed' and document issues
5. **Prepare transition**:
   - If PROCEED: Generate completion report with all deliverables
   - If FIX ISSUES: Generate retry batches with same standards for failed components, repeat until review reports no more issues
   - If ROLLBACK: Document rollback actions and specification issues
6. **Decision Management**: In phase 4, you (the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues

### Workflow Completion

**Report the workflow output as specified:**

```yaml
operation_functions: ["operations/operation1.ts", "operations/operation2.ts", "..."]
integration_tests: ["spec/operations/operation1.spec.int.ts", "spec/operations/operation2.spec.int.ts", "..."]
updated_controller: "source/index.ts"
documentation: ["JSDoc for operation1", "JSDoc for operation2", "..."]
completion_report:
  controller_name: "controller-name-from-notion"
  operations_implemented: ["operation1", "operation2", "..."]
  test_coverage_percentage: "XX%"
  all_tests_passing: true|false
  notion_page_id: "notion-page-id"
pattern_compliance:
  types_in_operation_files: true|false
  selector_pattern_used: true|false
  integration_test_pattern: true|false
  error_handling_pattern: true|false
standards_compliance:
  typescript_standards: true|false
  documentation_standards: true|false
  data_operations_standards: true|false
  testing_standards: true|false
notion_specification_compliance:
  all_operations_implemented: true|false
  data_logic_separation_verified: true|false
  specification_deviations: ["deviation1", "deviation2", "..."]
workflow_status: "success|partial|failure"
summary: "Brief description of data operation implementation completion"
```
