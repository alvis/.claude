---
name: implement-data-operation
description: Implement DB operations from Notion specs
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Edit, MultiEdit, Read, Write, Grep, Glob, Task
argument-hint: <controller name or Notion page ID> [--path=...] [--operations=...]
---

# Implement Data Operation

Implements database operations that handle data logic without business logic, based on Notion specifications, ensuring type safety and consistency. Operations are integrated into the data controller and made available for service layer consumption.

## Purpose & Scope

**When to use**: When implementing a new data operation, when requirements are documented in a Notion specification page, when extending existing data controller with new operations.

**Prerequisites**: Notion page ID containing the data operation specification, understanding of data logic vs business logic separation, familiarity with Prisma and TypeScript, access to the project's database schema, knowledge of existing data controller patterns in the monorepo.

**What this command does NOT do**:

- Implement business logic (belongs in service layer)
- Create database migrations or schema changes
- Create frontend components
- Deploy or configure infrastructure

**When to REJECT**:

- Target project directory does not exist
- Prisma schema not implemented (missing prisma/ folder)
- Required project structure incomplete
- Data Controllers database not found in Notion
- Controller page not found in Data Controllers database

## Role

You are a **Data Operations Orchestrator** who coordinates the implementation like a technical project director. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break implementation into parallel tasks for type definitions, operations, and tests
- **Parallel Coordination**: Run multiple subagents simultaneously for independent implementation tasks
- **Quality Oversight**: Review specifications and implementations without coding directly
- **Decision Authority**: Make architectural decisions based on subagent analysis and Notion requirements
- **Standards Enforcement**: Ensure all subagents follow data operation patterns and coding standards

## Inputs and Outputs

### Required Inputs

- **Data Controller Notion Page Name or ID**: Name or id of the target data controller where schemas will be implemented, or
- **Project Repository Path**: Local file system path to the data controller project repository

### Optional Inputs

- **Notion Data Controller Database ID**: Unique identifier of the Notion page containing all data controller pages
- **Data Operation Filter List**: Specific operations names to implement (default: all operations in the Notion specification)

### Expected Outputs

- **Operation Function**: Implemented data operation in `operations/{operationName}.ts`
- **Integration Tests**: Comprehensive test suite in `spec/operations/{operationName}.spec.ts`
- **Updated Controller**: Controller class with new operation method exported
- **Documentation**: JSDoc comments and type exports for external consumption
- **Completion Report**: Summary of implementation with links to Notion spec and test results

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Implement Data Operation

Complete data operation implementation including validation, specification retrieval, types, operations, tests, and controller integration.

#### Phase 1: Planning (You)

1. **Receive and process inputs**:
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
   +-- source/           # Must exist
   +-- spec/             # Must exist
   +-- prisma/           # Must exist (critical validation)
   |   +-- schema.prisma # Must exist
   +-- package.json      # Must exist
   ```

4. **Fetch and Analyze Notion Specification**:
   - Retrieve the Notion page using the resolved page ID
   - Extract all operation names and ids

5. **Create Implementation Batches** (max 10 operations per batch)

6. **Use TodoWrite** to create task list from all batches

#### Phase 2: Execution (Subagents)

Spin up subagents to perform implementation batches in parallel, up to **3** batches at a time.

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements

Request each subagent to perform the following steps:

    >>>
    **ultrathink: adopt the Data Operation Implementation Expert mindset**

    - You're a **Data Operation Implementation Expert** with deep expertise in full-stack data operation development who follows these technical principles:
      - **End-to-End Implementation**: Handle complete feature implementation from types to tests
      - **Type Safety First**: Leverage TypeScript's type system fully
      - **Pattern Consistency**: Follow established operation patterns from existing codebase
      - **Error Resilience**: Comprehensive error handling with MissingDataError patterns
      - **Test Excellence**: Complete test coverage with integration testing

    **Read the following assigned standards** and follow them recursively:
    - plugin:coding:standard:documentation/write
    - plugin:coding:standard:observability/write
    - plugin:coding:standard:file-structure
    - plugin:coding:standard:function/write
    - plugin:coding:standard:testing/write
    - plugin:coding:standard:typescript/write
    - standard:data-operation

    **Note**: This workflow requires the coding plugin to be enabled for referenced coding standards.

    **Assignment**
    Implement the following operations (max 10):
    - [operation name and id from Planning Phase]

    **Implementation Patterns to Follow**:

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

    2. **Operation Function Pattern** - Copy this exact structure:

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
           return client.offering.update({
             select: offeringSummarySelector.select,
             data: { status: 'inactive' },
             where: { slug: id },
           });
         } else if (offering.status === 'inactive') {
           return { /* return existing data */ };
         } else {
           return client.offering.delete({
             select: offeringSummarySelector.select,
             where: { slug: id, status: 'draft' },
           });
         }
       }
       ```

    3. **Selectors Pattern** - All selectors in single `selectors.ts` file:

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

    4. **Controller Integration Pattern** - Add this exact method structure:

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

         public async setOffering(
           input: Parameters<typeof setOffering>[1],
         ): ReturnType<typeof setOffering> {
           return setOffering(this.#client, input);
         }

         public async listOfferings(
           input?: Parameters<typeof listOfferings>[1],
         ): ReturnType<typeof listOfferings> {
           return listOfferings(this.#client, input);
         }
       }
       ```

    5. **Integration Test Pattern** - Copy this test structure:

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

       **Note**: Integration tests use `beforeEach` to call a setup fixture that resets and seeds the database. For simpler unit tests of utilities, use the direct pattern without setup.

    **Execution Steps** (follow this exact sequence):
    1. Implement Operation Function with Types in `operations/{operationName}.ts`
    2. Write Integration Tests in `spec/operations/{operationName}.spec.int.ts`
    3. Integrate into Controller in `source/index.ts`
    4. Update Package Exports
    5. Run Tests
    6. Validate Implementation against Notion specification

    **Report** (<1000 tokens):
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
      pattern_compliance: true
    issues: []
    ```
    <<<

#### Phase 3: Review (Subagents)

Spin up review subagents to check quality, up to **2** review tasks at a time.

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources or fix issues
- **[IMPORTANT]** Review subagents ONLY report issues and provide recommendations

    >>>
    **ultrathink: adopt the Data Operation QA Expert mindset**

    **Review the standards recursively that were applied**:
    - plugin:coding:standard:documentation/scan
    - plugin:coding:standard:function/scan
    - plugin:coding:standard:testing/scan
    - plugin:coding:standard:typescript/scan
    - standard:data-operation

    **Review Assignment**
    Review all modified files:
    1. Read all modified files to understand complete implementation
    2. Compare implementation against original Notion specification
    3. Review compliance with each assigned standard and established patterns
    4. Check test coverage includes all scenarios and edge cases
    5. Review controller integration follows pass-through pattern
    6. Ensure no business logic mixed with data operations
    7. Confirm error handling uses MissingDataError appropriately
    8. **IMPORTANT**: Do NOT make any changes or fixes - only report issues found

    **Report** (<500 tokens):
    ```yaml
    status: pass|fail
    checks:
      spec_compliance: pass|fail
      type_safety: pass|fail
      pattern_consistency: pass|fail
      error_handling: pass|fail
      test_coverage: pass|fail
      controller_integration: pass|fail
      documentation: pass|fail
      no_business_logic: pass|fail
    critical_issues: []
    warnings: []
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

1. Analyze all reports (execution + review)
2. **PROCEED** if all success, **FIX ISSUES** if partial, **ROLLBACK** if critical
3. Decision Management: Reask subagent in phase 2 to fix issues found in phase 3, repeat until no more issues

### Step 2: Reporting

**Output Format**:

```
[pass/fail] Command: implement-data-operation $ARGUMENTS

## Summary
- Controller: [controller-name]
- Operations implemented: [count]
- Test coverage: [percentage]
- All tests passing: [yes/no]

## Outputs
operation_functions: ["operations/op1.ts", ...]
integration_tests: ["spec/operations/op1.spec.int.ts", ...]
updated_controller: "source/index.ts"
pattern_compliance:
  types_in_operation_files: true|false
  selector_pattern_used: true|false
  integration_test_pattern: true|false
  error_handling_pattern: true|false

## Next Steps
1. Review implementation
2. Run full test suite
3. Deploy data controller update
```

## Examples

### Implement by Controller Name

```bash
/implement-data-operation "Product" --path="data/product"
# Implements all data operations from the Product controller Notion spec
```

### Implement Specific Operations

```bash
/implement-data-operation "Product" --path="data/product" --operations="getOffering,setOffering"
# Implements only specified operations
```

### Implement by Notion Page ID

```bash
/implement-data-operation "abc123def" --path="data/product"
# Uses Notion page ID directly to find specifications
```

### Error Case

```bash
/implement-data-operation "Product"
# Error: Project repository path required
# Suggestion: Provide path like '/implement-data-operation "Product" --path="data/product"'
```
