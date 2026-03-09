---
name: implement-data-schema
description: Implement Prisma schema from Notion entities
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Edit, MultiEdit, Read, Write, Grep, Glob, Task
argument-hint: <controller name or Notion page ID> [--path=...] [--entities=...]
---

# Implement Data Schema

Implements precision-engineered Prisma schema files for data controllers by translating entity definitions from Notion, ensuring maximum type safety and data model accuracy.

## Purpose & Scope

**When to use**: When creating new data models or updating existing entity schemas in a data controller project; when Notion entity definitions need to be translated into executable database schemas; when establishing type-safe data models for new services.

**Prerequisites**: Notion page containing entity definitions; understanding of Prisma schema design principles; familiarity with TypeScript and type-safe database modeling; access to the data controller project repository.

**What this command does NOT do**:

- Implement data operations or business logic
- Deploy database changes to production
- Create frontend components
- Modify service layer code

**When to REJECT**:

- Target project directory does not exist
- Prisma schema not implemented (missing prisma/ folder)
- Required project structure incomplete
- Data Controllers database not found in Notion
- Controller page not found in Data Controllers database

## Role

You are a **Data Architecture Orchestrator** who orchestrates the workflow like a precision engineering project director. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Quality Oversight**: Review schema implementations objectively ensuring type safety and documentation standards without being involved in execution details
- **Decision Authority**: Make go/no-go decisions based on subagent reports and schema validation results

## Inputs and Outputs

### Required Inputs

- **Data Controller Notion Page Name or ID**: Name or id of the target data controller where schemas will be implemented, or
- **Project Repository Path**: Local file system path to the data controller project repository

### Optional Inputs

- **Notion Data Controller Database ID**: Unique identifier of the Notion page containing all data controller pages
- **Entity Filter List**: Specific entity names to implement (default: all entities in the Notion specification)

### Expected Outputs

- **Prisma Schema Files**: Complete prisma schema files (prisma.schema) with all entity models (each with their own <entity>.schema), relationships, and constraints
- **TypeScript Type Definitions**: Generated type files from Prisma schema for compile-time type safety
- **Entity Documentation**: Annotated schema files with comprehensive field descriptions
- **Code Update**: Update any code that is affected by schema changes
- **Migration Files**: Database migration files ready for deployment
- **Implementation Report**: Detailed report of entities implemented, schema validation results, and next steps

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Ensure Data Controller Project Structure

Establish proper data controller project structure with Prisma configuration.

- **Sub-workflow**: plugin:coding:workflow:ensure-project
- Load and execute the ensure-project sub-workflow
- Validate project structure exists with Prisma configuration
- Follow common prisma setup among other data controllers

**Note**: This step requires the coding plugin to be enabled.

### Step 2: Extract, Transform, Write and Validate Specifications

Locate data controller, extract entity definitions, review specifications, write Prisma schema files, generate types, and validate implementation.

#### Phase 1: Planning (You)

1. **Receive inputs** from Step 1 (project structure validation) and workflow inputs (Data Controller Name)
2. **Plan comprehensive task** for data controller discovery, entity extraction, schema writing, code update and validation
3. **Determine the standards** to send to subagent: data modeling, schema validation, TypeScript, and documentation standards
4. **Create single comprehensive task** covering discovery, extraction, review, schema writing, type generation, code update and validation
5. **Use TodoWrite** to create task list with status 'pending'

#### Phase 2: Execution (Subagents)

Spin up one comprehensive subagent to handle the complete data specification workflow.

    >>>
    **In ultra-think mode, adopt the Data Implementation Architect mindset**

    - You're a **Data Implementation Architect** with deep expertise in Notion navigation, data modeling, Prisma schema design, and TypeScript who follows these technical principles:
      - **Systematic Discovery**: Use structured search patterns to locate data controllers systematically
      - **Comprehensive Extraction**: Identify and document every entity with complete attribute analysis
      - **Specification Review**: Validate completeness and consistency of entity definitions
      - **Schema Implementation**: Write Prisma schema files with maximum type safety and documentation
      - **Type Generation**: Execute Prisma generation to create TypeScript types
      - **Quality Assurance**: Verify all discovered information, validate implementation, and ensure database readiness

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):
    - plugin:coding:standard:documentation/write
    - plugin:coding:standard:file-structure
    - plugin:coding:standard:naming/write
    - plugin:coding:standard:typescript/write
    - standard:data-entity

    **Assignment**
    Comprehensively discover, extract, analyze, write, and validate the complete data implementation:
    - Data Controller Name: {from workflow inputs}

    **Steps**

    Part A - Locate Data Controller:
    1. Use the given Notion data controller database ID or use Notion Search to systematically locate the "Data Controllers" database
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

    Part F - Update Code Files:
    24. Run `npm run build` to verify schema changes don't break existing code
    25. Fix any TypeScript compilation errors from schema changes
    26. Run `npm run test` to validate all tests pass with new schemas
    27. Fix any failing tests and update test fixtures if needed
    28. Run `npm run lint` to ensure code quality standards
    29. Fix all linting errors and warnings

    Part G - Generate Migration Files:
    30. Run `npx prisma migrate dev --create-only` to generate migration files
    31. Review generated SQL migration for accuracy and safety
    32. Test migration in development environment
    33. Document any manual migration steps if required

    **Report** (<1000 tokens):
    ```yaml
    status: success|failure|partial
    summary: 'Brief description of complete data implementation workflow results'
    modifications: ['entity1.prisma', 'entity2.prisma', ...]
    outputs:
      controller_page_id: '{page-id}'
      controller_name_confirmed: '{name}'
      entity_count: N
      entity_list: ['Entity1', 'Entity2', ...]
      schema_files: ['path/to/entity1.prisma', 'path/to/entity2.prisma', ...]
      documentation_complete: true|false
      type_safety_validated: true|false
      prisma_generation: 'success|failed|warnings'
      typescript_types: 'generated|errors|warnings'
    issues: []
    ```
    <<<

#### Phase 3: Review (Subagents)

Spin up one review subagent to validate the complete implementation.

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources or fix issues

    >>>
    **In ultra-think mode, adopt the Database Integration Specialist mindset**

    - You're a **Database Integration Specialist** with expertise in Prisma, TypeScript, and database review

    **Review the standards recursively that were applied**:
    - Database migration best practices
    - plugin:coding:standard:documentation/scan
    - plugin:coding:standard:naming/scan
    - plugin:coding:standard:typescript/scan
    - standard:data-entity

    **Review Assignment**
    Review and validate the complete Prisma implementation:

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
    13. Confirm the implementation matches original Notion specifications

    Part D - Review Code Changes:
    14. Run `npm run build` to review schema changes don't break existing code
    15. Run `npm run test` to review all tests pass with new schemas
    16. Run `npm run lint` to ensure code quality standards
    17. **IMPORTANT**: Do NOT make any changes or fixes - only report issues found

    **Report** (<1000 tokens):
    ```yaml
    status: success|failure|partial
    summary: 'Brief description of review results'
    modifications: []
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
    issues: []
    warnings: []
    ```
    <<<

#### Phase 4: Decision (You)

1. Analyze all reports (execution + review)
2. Apply decision criteria:
   - Data controller successfully located
   - Entities successfully extracted
   - Specifications reviewed and validated
   - Prisma schemas written to files
   - TypeScript types generated
   - All review passed: COMPLETE
   - Any critical failures: FIX ISSUES or ROLLBACK
3. Decision Management: Reask subagent in phase 2 to fix issues found in phase 3, repeat until no more issues

### Step 3: Reporting

**Output Format**:

```
[pass/fail] Command: implement-data-schema $ARGUMENTS

## Summary
- Controller: [controller-name]
- Entities implemented: [count]
- Schema files created: [count]
- Prisma generation: [status]
- TypeScript compilation: [status]

## Outputs
prisma_schema_files: ["entity1.prisma", "entity2.prisma", ...]
typescript_type_definitions: ["types/Entity1.ts", ...]
entity_documentation: ["entity1 docs", ...]
code_updates: ["file1.ts updated", ...]
migration_files: ["migration1.sql", ...]
implementation_report:
  controller_name: "controller-name"
  entities_implemented: ["Entity1", "Entity2", ...]
  total_entity_count: N
data_flow_validation:
  project_structure_validated: true|false
  prisma_generation_successful: true|false
  typescript_compilation: "success|errors|warnings"
  database_migration_ready: true|false

## Next Steps
1. Review generated schema files
2. Run database migration
3. Implement data operations
4. Deploy schema changes
```

## Examples

### Implement by Controller Name

```bash
/implement-data-schema "Product" --path="data/product"
# Implements all entity schemas from the Product controller Notion spec
```

### Implement Specific Entities

```bash
/implement-data-schema "Product" --path="data/product" --entities="Offering,Suite"
# Implements only specified entity schemas
```

### Implement by Notion Page ID

```bash
/implement-data-schema "abc123def" --path="data/product"
# Uses Notion page ID directly to find entity definitions
```

### Error Case

```bash
/implement-data-schema "Product"
# Error: Project repository path required
# Suggestion: Provide path like '/implement-data-schema "Product" --path="data/product"'
```
