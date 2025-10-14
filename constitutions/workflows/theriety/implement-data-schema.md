# Implement Data Schema

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Implement precision-engineered Prisma schema files for data controllers by translating entity definitions from Notion, ensuring maximum type safety and data model accuracy.
**When to use**: When creating new data models or updating existing entity schemas in a data controller project; when Notion entity definitions need to be translated into executable database schemas; when establishing type-safe data models for new services.
**Prerequisites**: Notion page containing entity definitions; understanding of Prisma schema design principles; familiarity with TypeScript and type-safe database modeling; access to the data controller project repository.

### Your Role

You are a **Data Architecture Orchestrator** who orchestrates the workflow like a precision engineering project director. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Quality Oversight**: Review schema implementations objectively ensuring type safety and documentation standards without being involved in execution details
- **Decision Authority**: Make go/no-go decisions based on subagent reports and schema validation results

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Data Controller Notion Page Name or ID**: Name or id of the target data controller where schemas will be implemented, or
- **Project Repository Path**: Local file system path to the data controller project repository

#### Optional Inputs

- **Notion Data Controller Database ID**: Unique identifier of the Notion page containing all data controller pages, including target controller page
- **Entity Filter List**: Specific entity names to implement (default: all entities in the Notion specification)

#### Expected Outputs

- **Prisma Schema Files**: Complete prisma schema files (prisma.schema) with all entity models (each with their own <entity>.schema), relationships, and constraints
- **TypeScript Type Definitions**: Generated type files from Prisma schema for compile-time type safety
- **Entity Documentation**: Annotated schema files with comprehensive field descriptions
- **Code Update**: Update any code that are affected by any schema changes
- **Migration Files**: Database migration files ready for deployment
- **Implementation Report**: Detailed report of entities implemented, schema validation results, and next steps

#### Data Flow Summary

The workflow takes Notion entity specifications and transforms them into executable Prisma schemas by first ensuring project structure exists, then systematically fetching entity definitions from Notion, translating each entity into properly-typed Prisma models with comprehensive documentation, and finally generating TypeScript types for maximum compile-time safety.

### Visual Overview

#### Main Workflow Flow

```plaintext
  YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Ensure Project] ───────→ (Subagent: Setup data controller project structure)
   |
   v
[Step 2: Extract, Transform, Write & Validate] ───────→ (Single comprehensive subagent: complete workflow)
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
• You: Lists entities, batches schema work, assigns tasks, makes decisions
• Execution Subagents: Perform actual work, report back (<1k tokens)
• Verification Subagents: Check quality when needed (<500 tokens)
• Workflow is LINEAR: Step 1 → 2 → 3
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Prepare Project Environment
2. Extract, Transform, Write & Validate Specifications
3. Completion Confirmation

### Step 1: Ensure Data Controller Project Structure

**Step Configuration**:

- **Purpose**: Establish proper data controller project structure with Prisma configuration
- **Input**: Project Repository Path from workflow inputs
- **Output**: Provides project structure validation and Prisma setup (by following common prisma setup among other data controllers) for Step 2
- **Sub-workflow**: @../project/ensure-project.md
- **Parallel Execution**: No

#### Execute Ensure-Project Workflow (You)

When you reach this step and see sub-workflow path:

1. Use Read tool to load the sub-workflow file
2. Parse the sub-workflow to identify its steps
3. Dynamically expand step to 1.1, 1.2, 1.3... from the sub-workflow content
4. Use todo to track the status of each step
5. Execute each step as instructed in the sub-workflow
6. After all sub-workflow steps are complete, continue to the next step

### Step 2: Extract, Transform, Write & Validate Specifications

**Step Configuration**:

- **Purpose**: Locate data controller, extract entity definitions, review specifications, write Prisma schema files, generate types, and validate implementation - all in one comprehensive task
- **Input**: Receives from Step 1: validated project structure; uses Data Controller Name from workflow inputs
- **Output**: Final deliverables - generated Prisma schema files, TypeScript types, and validation report
- **Sub-workflow**: None
- **Parallel Execution**: No

#### Step 2 - Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from Step 1 (project structure validation) and workflow inputs (Data Controller Name)
2. **Plan comprehensive task** for data controller discovery, entity extraction, schema writing, code update and validation
3. **Determine the standards** to send to subagent: data modeling, schema validation, Notion navigation, TypeScript, and documentation standards
4. **Create single comprehensive task**:
   - Generate one task covering discovery, extraction, review, schema writing, type generation, code update and validation
   - Assign one specialist subagent to perform all tasks comprehensively
5. **Use TodoWrite** to create task list with status 'pending'
6. **Prepare task assignment** with complete instructions for the entire implementation workflow
7. **Queue task** for execution by comprehensive data implementation specialist

**OUTPUT from Planning**: Single comprehensive data implementation task assignment

#### Step 2 - Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, You spin up one comprehensive subagent to handle the complete data specification workflow.

- **[IMPORTANT]** Use TodoWrite to update task status from 'pending' to 'in_progress' when dispatched
- **[IMPORTANT]** You MUST ask the subagent to ultrathink hard about all aspects of the task

Request the subagent to perform the following comprehensive steps:

```text
    **In ultra-think mode, adopt the Data Implementation Architect mindset**

    - You're a **Data Implementation Architect** with deep expertise in Notion navigation, data modeling, Prisma schema design, and TypeScript who follows these technical principles:
      - **Systematic Discovery**: Use structured search patterns to locate data controllers systematically
      - **Comprehensive Extraction**: Identify and document every entity with complete attribute analysis
      - **Specification Review**: Validate completeness and consistency of entity definitions
      - **Schema Implementation**: Write Prisma schema files with maximum type safety and documentation
      - **Type Generation**: Execute Prisma generation to create TypeScript types
      - **Quality Assurance**: Verify all discovered information, validate implementation, and ensure database readiness

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - @../../standards/coding/backend/data-entity.md
    - @../../standards/coding/typescript.md
    - @../../standards/coding/documentation.md
    - @../../standards/coding/naming/functions.md
    - @../../standards/coding/naming/files.md

    **Assignment**
    You're assigned to comprehensively discover, extract, analyze, write, and validate the complete data implementation:

    - Data Controller Name: {from workflow inputs}
    - Complete discovery, extraction, review, schema writing, type generation, and validation in one comprehensive workflow

    **Steps**

    Part A - Locate Data Controller:
    1. Use the given Notion data controller database ID or use Notion Search to systematically locate the "Data Controllers" database or similar container
    2. Retrieve and parse the complete list of available data controllers via notion fetch
    3. Filter and identify the exact target data controller matching the provided name
    4. Validate data controller page access and confirm entity content availability
    5. Extract and validate data controller page ID for entity discovery

    Part B - Extract and Transform Specifications:
    6. Access the data controller Notion page using the discovered page ID
    7. Systematically extract all entity definitions from the specification
    8. For each entity, capture its data structure and its documentation
    9. Analyze entity relationships and dependencies for schema generation

    Part C - Review and Validate:
    10. Review specifications for completeness, consistency, and implementation readiness
    11. Identify any missing information, specification gaps, or potential issues
    12. Validate that all entities are properly defined and implementable

    Part D - Prepare Prisma Schemas:
    13. Translate each entity into Prisma schema model syntax
    14. Ensure proper field types, relations, and constraints are defined
    15. Structure models for optimal database implementation

    Part E - Write Schema Files and Generate Types:
    16. For each entity, create individual schema files with the Prisma model
    17. Add comprehensive JSDoc documentation for every field following top-of-field style
    18. Ensure proper type definitions and constraints for each field
    19. Write the schema models to appropriate files in the project structure
    20. Validate schema syntax and type safety requirements
    21. Ensure all entity relationships are properly mapped in the files
    22. Navigate to the project directory containing Prisma schemas
    23. Run `npx prisma generate` to create TypeScript type definitions

    Part F - Update Code Files
    24. Run `npm run build` to verify schema changes don't break existing code
    25. Fix any TypeScript compilation errors from schema changes
    26. Run `npm run test` to validate all tests pass with new schemas
    27. Fix any failing tests and update test fixtures if needed
    28. Run `npm run lint` to ensure code quality standards
    29. Fix all linting errors and warnings

    Part G - Generate Migration Files
    30. Run `npx prisma migrate dev --create-only` to generate migration files
    31. Review generated SQL migration for accuracy and safety
    32. Test migration in development environment
    33. Document any manual migration steps if required

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - Confirmed data controller page ID and validation status
    - Complete list of entities with detailed attribute specifications
    - Entity relationship mapping and dependency analysis
    - Specification review results and quality assessment
    - Generated Prisma schema files for each entity
    - Documentation completeness confirmation
    - Prisma generation success confirmation
    - TypeScript type validation status
    - Any missing information or specification gaps identified

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of complete data implementation workflow results'
    modifications: ['entity1.prisma', 'entity2.prisma', ...]  # schema files created/modified
    outputs:
      controller_page_id: '{page-id}'
      controller_name_confirmed: '{name}'
      access_verified: true|false
      entity_count: N
      entity_list: ['Entity1', 'Entity2', ...]
      entities_detailed: 
        Entity1: 'model Entity1 {...}'
        Entity2: 'model Entity2 {...}'
      relationship_map: {dependencies and connections}
      review_results:
        completeness: 'All entities fully specified|Missing: [...]'
        consistency: 'All consistent|Issues found: [...]'
        implementability: 'Ready for implementation|Blockers: [...]'
      schema_files: ['path/to/entity1.prisma', 'path/to/entity2.prisma', ...]
      documentation_complete: true|false
      type_safety_validated: true|false
      prisma_generation: 'success|failed|warnings'
      typescript_types: 'generated|errors|warnings'
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
```

#### Step 2 - Phase 3: Review and Finalization (Subagents)

**When You Trigger This Phase**: After the comprehensive subagent completes all implementation tasks

In a single message, You spin up one review subagent to validate the complete implementation.

- **[IMPORTANT]** This phase reviews the entire implementation done by the previous subagent
- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources or fix issues
- **[IMPORTANT]** Review subagents ONLY report issues and provide recommendations - they do not implement fixes
- **[IMPORTANT]** The subagent will review schemas, types, and database integration
- **[IMPORTANT]** Use TodoWrite to track this review task

Request the subagent to perform the following comprehensive review:

```text
    **In ultra-think mode, adopt the Database Integration Specialist mindset**

    - You're a **Database Integration Specialist** with expertise in Prisma, TypeScript, and database review who follows these principles:
      - **Schema Review**: Review correct Prisma schema syntax and conventions
      - **Type Review**: Review generated TypeScript types
      - **Integration Testing**: Review the complete database integration
      - **Documentation Quality**: Ensure comprehensive documentation
      - **Migration Readiness**: Confirm database migration compatibility
      - **Review-Only Role**: Identify issues and provide recommendations without making any changes

    **Review the standards recursively (if A references B, review B too) that were applied**:

    - @../../standards/coding/backend/data-entity.md
    - @../../standards/coding/typescript.md - Review compliance with TypeScript standards
    - @../../standards/coding/documentation.md - Check documentation completeness
    - @../../standards/coding/naming/functions.md - Review naming conventions
    - Database migration best practices

    **Review Assignment**
    You're assigned to review and validate the complete Prisma implementation:

    - All generated schema files from Phase 2
    - Complete type generation and validation requirements

    **Steps**

    Part A - Review Schema Files:
    1. Read all generated schema files to understand structure
    2. Review Prisma schema syntax and naming conventions
    3. Check type definitions and constraints for correctness
    4. Review entity relationships and foreign key mappings
    5. Ensure documentation is comprehensive and accurate

    Part B - Review TypeScript Types and Integration:
    6. Check generated Prisma client for completeness
    7. Review TypeScript types match entity specifications
    8. Review successful generation without errors or warnings
    9. Check for any type safety issues or compilation errors
    10. Ensure all relationships are properly typed and navigable

    Part C - Final Review:
    11. Test database connection and migration readiness
    12. Review all entity models are accessible through Prisma client
    13. Check for any type safety issues or compilation errors
    14. Ensure all relationships are properly typed and navigable
    15. Confirm the implementation matches original Notion specifications

    Part D - Review Code Changes:
    16. Run `npm run build` to review schema changes don't break existing code
    18. Run `npm run test` to review all tests pass with new schemas
    20. Run `npm run lint` to ensure code quality standards
    21. **IMPORTANT**: Do NOT make any changes or fixes - only report issues found

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - Schema review results for all entities
    - Prisma generation review status
    - TypeScript type review status
    - Database integration readiness assessment
    - Any critical issues or warnings found

    **[IMPORTANT]** You MUST return the following review report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of review results'
    modifications: []  # no modifications - review only
    outputs:
      schemas_reviewed: true|false
      prisma_generation_reviewed: 'success|failed|warnings'
      typescript_types_reviewed: 'valid|errors|warnings'
      database_ready: true|false
      review_details:
        syntax_valid: pass|fail
        types_correct: pass|fail
        relationships_valid: pass|fail
        documentation_complete: pass|fail
        migration_ready: pass|fail
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    warnings: ['warning1', 'warning2', ...]  # non-critical issues
    ```
```

#### Step 2 - Phase 4: Decision (You)

**What You Do**:

1. **Analyze all reports** (execution + review)
2. **Apply decision criteria**:
   - Data controller successfully located → Check next
   - Entities successfully extracted → Check next
   - Specifications reviewed and validated → Check next
   - Prisma schemas written to files → Check next
   - TypeScript types generated → Check next
   - All review passed → COMPLETE
   - Any critical failures → FIX ISSUES or ROLLBACK
3. **Select next action**:
   - **PROCEED**: All review passed → Complete workflow
   - **FIX ISSUES**: Some failures → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
   - **ROLLBACK**: Critical failures → Revert changes → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
4. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark all items as 'completed' and workflow complete
   - If FIX ISSUES: Add new todo items for retry tasks with failed items
   - If ROLLBACK: Mark all items as 'failed' and add rollback todos
5. **Prepare final deliverables**: Package all outputs for workflow completion
6. **Decision Management**: In phase 4, you (the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues

### Workflow Completion

**Report the workflow output as specified:**

```yaml
prisma_schema_files: ["entity1.prisma", "entity2.prisma", "..."]
typescript_type_definitions: ["types/Entity1.ts", "types/Entity2.ts", "..."]
entity_documentation: ["entity1 documentation", "entity2 documentation", "..."]
code_updates: ["file1.ts updated", "file2.ts updated", "..."]
migration_files: ["migration1.sql", "migration2.sql", "..."]
implementation_report:
  controller_name: "controller-name-from-notion"
  entities_implemented: ["Entity1", "Entity2", "..."]
  notion_page_id: "notion-page-id"
  total_entity_count: 5
data_flow_validation:
  project_structure_validated: true|false
  prisma_generation_successful: true|false
  typescript_compilation: "success|errors|warnings"
  database_migration_ready: true|false
notion_specification_compliance:
  all_entities_implemented: true|false
  type_safety_maintained: true|false
  documentation_complete: true|false
  specification_gaps: ["gap1", "gap2", "..."]
workflow_status: "success|partial|failure"
summary: "Brief description of data schema implementation completion"
```
