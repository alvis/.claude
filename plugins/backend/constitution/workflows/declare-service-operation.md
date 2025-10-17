# Declare Service Operation

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Define a new operation for a service, creating the manifest schema definition with proper type safety and documentation
**When to use**: When adding a new operation to an existing service or creating the first operation for a new service manifest project
**Prerequisites**: Service requirements documented on Notion, understanding of the operation's input/output schema, familiarity with JSON Schema and TypeScript types, access to monorepo root and package manager

### Your Role

You are a **Service Orchestration Director** who coordinates the workflow like a project director overseeing API development. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break complex schema definition work into parallel tasks and assign to specialized subagents
- **Parallel Coordination**: Maximize efficiency by running multiple subagents simultaneously for independent tasks
- **Quality Oversight**: Review manifest definitions objectively without being involved in coding details
- **Decision Authority**: Make go/no-go decisions based on subagent reports and schema validation results

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Service Name**: Target service identifier for manifest creation
- **Operation Requirements**: Complete operation specification from documentation (typically Notion)
- **Operation Name**: Specific operation identifier (camelCase naming)

#### Optional Inputs

- **Existing Manifest Path**: Path to existing service manifest directory (default: auto-detect)
- **Schema Complexity**: Simple/Complex flag to determine batching strategy (default: auto-detect)

#### Expected Outputs

- **Operation Manifest**: Complete operation definition with schema and mock implementation
- **Schema Files**: TypeScript-compatible JSON schemas for input/output validation
- **Type Definitions**: Generated TypeScript types using FromSchema pattern
- **Service Integration**: Updated service manifest index with new operation registration
- **Validation Report**: Confirmation that all schemas compile and mock data validates

#### Data Flow Summary

The workflow takes service requirements and transforms them into type-safe manifest definitions by decomposing schema creation, implementing validation, and integrating with existing service structure through parallel subagent execution.

### Visual Overview

#### Main Workflow Flow

```plaintext
   YOU                        SUBAGENTS EXECUTE
(Orchestrates Only)                 (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Gather Requirements] ──→ (Subagent: Extract and validate operation specifications)
   |
   v
[Step 2: Ensure Project] ────────→ (Sub-workflow: plugin:coding:workflow:ensure-project for manifest structure)
   |                                 **Note**: Requires coding plugin to be enabled
   |
   v
[Step 3: Create Schemas] ────────→ (Subagents: Build input/output schemas in parallel)
   |               ├─ Schema Subagent A: Input schema definition
   |               └─ Schema Subagent B: Output schema definition (if needed)
   v
[Step 4: Build Manifest] ────────→ (Subagent: Create operation manifest with mock)
   |
   v
[Step 5: Integrate Service] ─────→ (Subagent: Update service manifest index)
   |
   v
[Step 6: Final Validation] ──────→ (Verification Subagent: Comprehensive validation)
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
• Workflow is LINEAR: Step 1 → 2 → 3 → 4 → 5 → 6
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Gather Operation Requirements
2. Ensure Project Structure  
3. Create Schema Definitions
4. Build Operation Manifest
5. Integrate with Service
6. Final Validation

### Step 1: Gather Operation Requirements

**Step Configuration**:

- **Purpose**: Extract and validate complete operation specifications from documentation
- **Input**: Service name, operation name, and documentation references (typically Notion URLs)
- **Output**: Structured operation requirements with input/output schema specifications
- **Sub-workflow**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from workflow invocation (service name, operation name, documentation sources)
2. **List all documentation sources** that need to be accessed
3. **Determine the standards** to send to subagents: TypeScript (plugin:coding:standard:typescript), Documentation (plugin:coding:standard:documentation)
4. **Create task assignment** for requirements gathering
5. **Use TodoWrite** to create task list: ['Requirements extraction - pending']
6. **Prepare task assignment** for subagent execution
7. **Queue requirements gathering** for execution by subagent

**OUTPUT from Planning**: Single task assignment for requirements extraction

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, You assign the requirements gathering task to a specialized subagent.

- **[IMPORTANT]** Claude MUST ask subagent to ultrathink hard about the operation requirements
- **[IMPORTANT]** Use TodoWrite to update task status from 'pending' to 'in_progress' when dispatched

Request the subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Backend Service Architect mindset**

    - You're a **Backend Service Architect** with deep expertise in API design and type-safe service operations who follows these technical principles:
      - **Schema-First Design**: Define clear contracts before implementation to ensure API consistency and type safety
      - **Type Safety**: Leverage TypeScript's type system with JSON Schema to eliminate runtime type errors
      - **Documentation as Code**: Ensure schemas serve as both runtime validation and living documentation

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively:

    - typescript.md
    - documentation.md
    - naming/files.md

    **Assignment**
    You're assigned to gather requirements for operation: [OPERATION_NAME] in service: [SERVICE_NAME]

    **Steps**

    1. Visit the Notion page for the service operation (if URL provided)
    2. Extract complete input schema requirements with field types, validation rules, and constraints
    3. Extract output schema requirements (if operation returns data) with proper typing
    4. Document any special validation rules or business logic constraints
    5. Identify required vs optional fields for both input and output

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - Complete input schema specification with types and validation
    - Complete output schema specification (if applicable) with types
    - List of validation rules and constraints
    - Operation behavior description (sync/async, side effects)

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of requirements gathered'
    modifications: []  # No files modified in this step
    outputs:
      input_schema_spec: 'Detailed input schema requirements'
      output_schema_spec: 'Detailed output schema requirements or null'
      validation_rules: ['rule1', 'rule2', ...]
      operation_type: 'sync|async'
    issues: []  # Any problems encountered during requirements gathering
    ```
    <<<

#### Phase 3: Review (You)

**What You Do**:

1. **Use TodoRead** to check current task status
2. **Collect execution report** from requirements subagent
3. **Parse report status** and validate completeness of requirements
4. **Use TodoWrite** to update task status based on success/failure
5. **Validate requirements completeness**:
   - Input schema specification present
   - Output schema specification (if operation returns data)
   - Validation rules documented
6. **Determine review needs**: Not typically required for requirements gathering
7. **Compile review summary** with any missing requirements

#### Phase 3: Review (Subagents) - Optional

**When Claude Triggers Review**: Complex operations with unclear requirements

**What You Send to Review Subagents**: Not typically needed for this step

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze requirements report** for completeness and clarity
2. **Apply decision criteria**:
   - All required schema specifications gathered
   - Operation behavior clearly understood
3. **Select next action**:
   - **PROCEED**: Complete requirements gathered → Move to Step 2
   - **FIX ISSUES**: Incomplete or unclear requirements → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
   - **ROLLBACK**: Critical documentation missing → Revert changes → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
4. **Use TodoWrite** to update task list based on decision
5. **Prepare transition**: Package requirements for project structure setup
6. **Decision Management**: In phase 4, you (the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues

### Step 2: Ensure Project Structure

**Step Configuration**:

- **Purpose**: Set up the manifest project structure if it doesn't exist yet
- **Input**: Receives from Step 1: service name and operation requirements
- **Output**: Provides to Step 3: validated project structure with proper manifest directory layout
- **Sub-workflow**: /ensure-project.md
- **Parallel Execution**: No

#### Execute ensure-project Workflow (You)

When Claude reaches this step and sees sub-workflow path:

1. Use Read tool to load the sub-workflow file: /ensure-project.md
2. Parse the sub-workflow to identify its steps
3. Dynamically expand step to 2.1, 2.2, 2.3... from the sub-workflow content with these service manifest structure requirements:

```plaintext
# Service manifest directory structure
manifests/[service-name]/
├── package.json
├── source/
│   ├── index.ts
│   └── operations/
└─ spec/
    └── index.spec.ts
```

4. Use TodoWrite to track the status of each ensure-project step
5. Executes each step as instructed in the ensure-project sub-workflow
6. Pass specific requirements:
   - Manifest directory under `manifests/[service-name]/`
   - Package.json with service-specific configuration and exports
   - Source directory with index.ts and operations subdirectory
   - Spec directory for tests
   - All dependencies aligned with existing manifest projects in monorepo
7. After all sub-workflow steps are complete, continue to Step 3

### Step 3: Create Schema Definitions

**Step Configuration**:

- **Purpose**: Build the schema definition files for the new operation with proper type safety
- **Input**: Receives from Step 2: validated project structure and from Step 1: operation requirements
- **Output**: Provides to Step 4: complete schema definitions with TypeScript types
- **Sub-workflow**: None
- **Parallel Execution**: Yes - input and output schemas can be created in parallel

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from Step 1 (requirements) and Step 2 (project structure)
2. **List schema creation tasks** based on operation requirements:
   - Input schema (always required)
   - Output schema (if operation returns data)
   - Schema exports and type definitions
3. **Determine the standards** to send to subagents: TypeScript (plugin:coding:standard:typescript), Naming Conventions (plugin:coding:standard:naming)
4. **Create dynamic batches** following these rules:
   - Batch 1: Input schema creation
   - Batch 2: Output schema creation (if needed)
   - Batch 3: Schema exports and type definitions
5. **Use TodoWrite** to create task list from all batches
6. **Prepare task assignments** with schema specifications
7. **Queue all batches** for parallel execution by subagents

**OUTPUT from Planning**: Task batch assignments for schema creation

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, You spin up subagents to create schemas in parallel, up to **3** subtasks at a time.

- **[IMPORTANT]** When there are any issues reported, Claude must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** Claude MUST ask all subagents to ultrathink hard about type safety and schema validation
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Schema Definition Specialist mindset**

    - You're a **Schema Definition Specialist** with deep expertise in JSON Schema and TypeScript integration who follows these technical principles:
      - **Type Safety First**: Ensure all schemas compile to strict TypeScript types
      - **Validation Completeness**: Include all necessary validation rules and constraints
      - **Documentation Integration**: Every schema field must have clear descriptions

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively:

    - typescript.md
    - naming/functions.md
    - naming/files.md

    **Assignment**
    You're assigned to create schema files for operation: [OPERATION_NAME]
    
    Target directory structure:
    ```
    manifests/[service-name]/source/operations/[operationName]/
    ├── index.ts        # Operation manifest definition (Step 4)
    └── schema/
        ├── index.ts    # Schema exports and types
        ├── input.ts    # Input schema definition
        └── output.ts   # Output schema (skip for void operations)
    ```

    **Steps**

    1. Create operation directory with camelCase naming
    2. Define input schema with proper JSON Schema format using requirements
    3. Define output schema (if operation returns data) with proper typing
    4. Export TypeScript types using `FromSchema` pattern
    5. Add comprehensive schema validation rules (required fields, formats, patterns)
    6. Ensure all schemas use `as const satisfies JsonSchema` pattern

    **Schema Examples to Follow**:

    Input Schema Pattern:
    ```typescript
    // schema/input.ts
    import type { JsonSchema } from '@theriety/manifest';

    export default {
      type: 'object',
      additionalProperties: false,
      required: ['profileId', 'secret'],
      properties: {
        profileId: {
          type: 'string',
          format: 'uuid',
          description: 'KMS profile identifier',
        },
        secret: {
          type: 'object',
          required: ['name', 'value'],
          properties: {
            name: { type: 'string', minLength: 1 },
            value: { type: 'string', minLength: 1 },
          },
        },
      },
    } as const satisfies JsonSchema;
    ```

    Schema Export Pattern:
    ```typescript
    // schema/index.ts
    import input from './input';
    import output from './output'; // omit if the operation that doesn't return

    import type { FromSchema } from '@theriety/manifest';

    export type Input = FromSchema<typeof input>;
    export type Output = FromSchema<typeof output>; // omit if the operation that doesn't return

    export default { input, output };
    ```

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - List of schema files created
    - TypeScript compilation status
    - Schema validation completeness

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of schemas created'
    modifications: ['schema/input.ts', 'schema/output.ts', 'schema/index.ts']
    outputs:
      input_schema_created: true|false
      output_schema_created: true|false|not_required
      type_exports_created: true|false
      typescript_compiles: true|false
    issues: []  # Any problems encountered during schema creation
    ```
    <<<

#### Phase 3: Review (You)

**What You Do**:

1. **Use TodoRead** to check current task statuses
2. **Collect all execution reports** from parallel schema subagents
3. **Parse report statuses** for each batch (input schema, output schema, exports)
4. **Use TodoWrite** to update batch statuses based on success/failure
5. **Identify any failed schema creation** and group by failure type
6. **Determine review needs**: Always review schema compilation and type safety
7. **Compile review summary** with schema creation status

#### Phase 3: Review (Subagents) - Required

**When Claude Triggers Review**: Always for schema creation to ensure type safety

**What You Send to Review Subagents**:

In a single message, You assign schema review to ensure compilation and type safety.

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources or fix issues
- **[IMPORTANT]** Review subagents ONLY report issues and provide recommendations - they do not implement fixes

Request review subagent to perform the following review with full scrutiny:

    >>>
    **ultrathink: adopt the TypeScript Review Expert mindset**

    - You're a **TypeScript Review Expert** with expertise in schema review and type safety who follows these principles:
      - **Compilation Review**: Review that all schemas compile without TypeScript errors
      - **Type Safety Review**: Review that generated types are properly typed and usable
      - **Schema Completeness**: Review that all required validation rules are present
      - **Review-Only Role**: Identify issues and provide recommendations without making any changes

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Review the standards recursively that were applied**:

    - typescript.md - Review TypeScript compliance
    - naming/functions.md - Check naming conventions

    **Review Assignment**
    You're assigned to review the following schema files that were created:

    - schema/input.ts: Input schema definition with proper JSON Schema format
    - schema/output.ts: Output schema definition (if applicable)
    - schema/index.ts: Type exports using FromSchema pattern

    **Review Steps**

    1. Read all created schema files to understand structure
    2. Review TypeScript compilation works without errors
    3. Check that all schemas use `as const satisfies JsonSchema` pattern
    4. Review that FromSchema types are properly generated
    5. Ensure validation rules match operation requirements
    6. **IMPORTANT**: Do NOT make any changes or fixes - only report issues found

    **Report**
    **[IMPORTANT]** You're requested to review and report:

    - TypeScript compilation status
    - Schema format compliance
    - Type generation accuracy
    - Requirements alignment

    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Brief schema review summary'
    checks:
      typescript_compiles: pass|fail
      schema_format_valid: pass|fail
      types_generated: pass|fail
      requirements_match: pass|fail
    fatals: []  # Only critical blockers
    warnings: []  # Non-blocking issues
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze all reports** (execution + verification)
2. **Apply decision criteria**:
   - All schemas created successfully
   - TypeScript compilation passes
   - Verification recommends proceed
3. **Select next action**:
   - **PROCEED**: All schemas validated → Move to Step 4
   - **FIX ISSUES**: Schema compilation or validation failures → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
   - **ROLLBACK**: Critical type safety issues → Revert changes → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
4. **Use TodoWrite** to update task list based on decision
5. **Prepare transition**: Package schema definitions for manifest creation
6. **Decision Management**: In phase 4, you (the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues

### Step 4: Build Operation Manifest

**Step Configuration**:

- **Purpose**: Create the operation manifest with comprehensive mock implementation
- **Input**: Receives from Step 3: validated schema definitions with TypeScript types
- **Output**: Provides to Step 5: complete operation manifest with realistic mock data
- **Sub-workflow**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from Step 3 (schema definitions and types)
2. **List manifest creation requirements**:
   - Operation manifest definition
   - Mock implementation with realistic data
   - Proper async/sync configuration
3. **Determine the standards** to send to subagents: TypeScript (plugin:coding:standard:typescript), Functions (plugin:coding:standard:functions)
4. **Create single task assignment** for manifest creation
5. **Use TodoWrite** to create task: ['Manifest creation - pending']
6. **Prepare task assignment** with schema imports and mock requirements
7. **Queue manifest creation** for execution by subagent

**OUTPUT from Planning**: Single task assignment for manifest creation

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, You assign the manifest creation task to a specialized subagent.

Request the subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Operation Manifest Builder mindset**

    - You're an **Operation Manifest Builder** with deep expertise in manifest framework and mock implementations who follows these technical principles:
      - **Mock-Driven Development**: Create comprehensive mocks that facilitate testing and development
      - **Type Safety**: Ensure all mock data matches schema types exactly
      - **Realistic Data**: Generate mock responses that represent real-world usage

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively:

    - typescript.md
    - functions.md
    - naming/files.md

    **Assignment**
    You're assigned to create the operation manifest for: [OPERATION_NAME]

    **Steps**

    1. Import `createOperationManifest` from '@theriety/manifest'
    2. Import schema and types from './schema'
    3. Set `path: import.meta.url` for operation identification
    4. Configure `async: true` for asynchronous operations (or `async: false` if sync)
    5. Implement comprehensive mock function with realistic data
    6. Ensure mock return data matches output schema exactly
    7. Add proper TypeScript typing for mock function parameters and return

    **Manifest Pattern to Follow**:
    ```typescript
    // operations/[operationName]/index.ts
    import { createOperationManifest } from '@theriety/manifest';

    import schema from './schema';
     
    import type { Input, Output } from './schema';

    export default createOperationManifest({
      path: import.meta.url,
      schema,
      async: true,
      mock: async (input: Input): Promise<Output> => {
        // return realistic mock data matching output schema
        return {
          id: 'mock-id-123',
          status: 'success',
          // ... complete mock response
        };
      },
    });
    ```

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - Operation manifest file path
    - Mock implementation completeness
    - TypeScript compilation status
    - Mock data schema validation

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of manifest creation'
    modifications: ['operations/[operationName]/index.ts']
    outputs:
      manifest_created: true|false
      mock_implemented: true|false
      typescript_compiles: true|false
      mock_validates: true|false
    issues: []  # Any problems encountered during manifest creation
    ```
    <<<

#### Phase 3: Review (You)

**What You Do**:

1. **Use TodoRead** to check current task status
2. **Collect execution report** from manifest subagent
3. **Parse report status** and validate manifest completeness
4. **Use TodoWrite** to update task status based on success/failure
5. **Validate manifest requirements**:
   - Operation manifest created
   - Mock implementation present
   - TypeScript compilation successful
6. **Determine review needs**: Review mock data matches schema
7. **Compile review summary** with manifest creation status

#### Phase 3: Review (Subagents) - Required

**When Claude Triggers Review**: Always for manifest creation to ensure mock data validity

**What You Send to Review Subagents**:

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources or fix issues
- **[IMPORTANT]** Review subagents ONLY report issues and provide recommendations - they do not implement fixes

Request review subagent to validate manifest and mock implementation:

    >>>
    **ultrathink: adopt the Manifest Review Expert mindset**

    - You're a **Manifest Review Expert** with expertise in operation manifests and mock data review who follows these principles:
      - **Mock Data Accuracy**: Review that mock responses exactly match output schema
      - **Type Safety Review**: Review that all manifest components are properly typed
      - **Framework Compliance**: Review that manifest follows framework patterns correctly
      - **Review-Only Role**: Identify issues and provide recommendations without making any changes

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Review Assignment**
    You're assigned to review the operation manifest that was created:

    - operations/[operationName]/index.ts: Complete operation manifest with mock

    **Review Steps**

    1. Read the created manifest file to understand implementation
    2. Review mock function returns data matching output schema
    3. Check that manifest uses proper framework patterns
    4. Review TypeScript types are correctly applied
    5. Ensure async/sync configuration matches operation requirements
    6. **IMPORTANT**: Do NOT make any changes or fixes - only report issues found

    **Report**
    **[IMPORTANT]** You're requested to review and report:

    - Mock data schema compliance
    - Framework pattern usage
    - TypeScript type safety
    - Operation configuration accuracy

    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Brief manifest review summary'
    checks:
      mock_data_valid: pass|fail
      framework_patterns: pass|fail
      typescript_safe: pass|fail
      config_correct: pass|fail
    fatals: []  # Only critical blockers
    warnings: []  # Non-blocking issues
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze all reports** (execution + verification)
2. **Apply decision criteria**:
   - Manifest created successfully
   - Mock data validates against schema
   - Verification recommends proceed
3. **Select next action**:
   - **PROCEED**: Manifest validated → Move to Step 5
   - **FIX ISSUES**: Mock data or manifest issues → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
   - **ROLLBACK**: Critical framework pattern issues → Revert changes → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
4. **Use TodoWrite** to update task list based on decision
5. **Prepare transition**: Package operation manifest for service integration
6. **Decision Management**: In phase 4, you (the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues

### Step 5: Integrate with Service

**Step Configuration**:

- **Purpose**: Register the new operation in the service manifest index
- **Input**: Receives from Step 4: completed operation manifest
- **Output**: Provides to Step 6: updated service manifest with new operation registered
- **Sub-workflow**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from Step 4 (completed operation manifest)
2. **List service integration requirements**:
   - Update service manifest index
   - Add operation import with path mapping
   - Maintain alphabetical ordering
3. **Determine the standards** to send to subagents: TypeScript (plugin:coding:standard:typescript), Naming Conventions (plugin:coding:standard:naming)
4. **Create single task assignment** for service integration
5. **Use TodoWrite** to create task: ['Service integration - pending']
6. **Prepare task assignment** with service manifest update requirements
7. **Queue service integration** for execution by subagent

**OUTPUT from Planning**: Single task assignment for service integration

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

Request the subagent to perform service integration with full detail:

    >>>
    **ultrathink: adopt the Service Integration Specialist mindset**

    - You're a **Service Integration Specialist** with deep expertise in service manifest management who follows these technical principles:
      - **Import Organization**: Maintain clean, alphabetical import organization
      - **Path Mapping**: Use proper TypeScript path mapping for operation imports
      - **Consistency**: Ensure integration follows existing service patterns

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively:

    - typescript.md
    - naming/functions.md
    - naming/files.md

    **Assignment**
    You're assigned to integrate operation [OPERATION_NAME] into the service manifest

    **Steps**

    1. Read the current service manifest (source/index.ts) to understand existing structure
    2. Import the new operation using path mapping: `#operations/[operationName]`
    3. Add the operation to the operations object in alphabetical order
    4. Ensure proper TypeScript typing throughout
    5. Maintain consistency with existing import and export patterns

    **Integration Pattern to Follow**:
    ```typescript
    // source/index.ts
    import { createServiceManifest } from '@theriety/manifest';

    import packageJson from '../package.json';
    import existingOp1 from '#operations/existingOp1';
    import newOperation from '#operations/newOperation';
    import existingOp2 from '#operations/existingOp2';

    export default createServiceManifest({
      packageJson,
      operations: {
        existingOp1,
        newOperation,  // Added in alphabetical order
        existingOp2,
      },
    });
    ```

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - Service manifest update status
    - Import organization compliance
    - TypeScript compilation status

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of service integration'
    modifications: ['source/index.ts']
    outputs:
      operation_imported: true|false
      operation_registered: true|false
      alphabetical_order: true|false
      typescript_compiles: true|false
    issues: []  # Any problems encountered during integration
    ```
    <<<

#### Phase 3: Review (Subagents) - Required

**When Claude Triggers Review**: Always for service integration to ensure exports work

**What You Send to Review Subagents**:

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources or fix issues
- **[IMPORTANT]** Review subagents ONLY report issues and provide recommendations - they do not implement fixes

Request review subagent to validate service manifest integration:

    >>>
    **ultrathink: adopt the Service Manifest Review Expert mindset**

    - You're a **Service Manifest Review Expert** with expertise in service exports and manifest review who follows these principles:
      - **Export Review**: Review that all operations are properly exported and accessible
      - **Import Correctness**: Review that all imports resolve correctly
      - **Service Completeness**: Review that service manifest includes all required operations
      - **Review-Only Role**: Identify issues and provide recommendations without making any changes

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Review Assignment**
    You're assigned to review the updated service manifest:

    - source/index.ts: Updated service manifest with new operation

    **Review Steps**

    1. Read the updated service manifest to understand changes
    2. Review new operation import resolves correctly
    3. Check that operation is properly included in operations object
    4. Review alphabetical ordering is maintained
    5. Ensure TypeScript compilation works without errors
    6. Test that service manifest exports the new operation
    7. **IMPORTANT**: Do NOT make any changes or fixes - only report issues found

    **Report**
    **[IMPORTANT]** You're requested to review and report:

    - Import resolution status
    - Operation registration completeness
    - Export functionality
    - Organization compliance

    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: 'Brief service integration review summary'
    checks:
      imports_resolve: pass|fail
      operation_registered: pass|fail
      exports_work: pass|fail
      organization_correct: pass|fail
    fatals: []  # Only critical blockers
    warnings: []  # Non-blocking issues
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze all reports** (execution + verification)
2. **Apply decision criteria**:
   - Service manifest updated successfully
   - All imports and exports work correctly
   - Verification recommends proceed
3. **Select next action**:
   - **PROCEED**: Integration validated → Move to Step 6
   - **FIX ISSUES**: Import or export issues → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
   - **ROLLBACK**: Critical service manifest issues → Revert changes → Create new batches for failed items and perform phase 2 again → Review following phase 3 again → ||repeat||
4. **Use TodoWrite** to update task list based on decision
5. **Prepare transition**: Service ready for final validation
6. **Decision Management**: In phase 4, you (the management) must decide whether it should reask the subagent in phase 2 to fix any issues found by the subagent in phase 3, and repeat until the subagent report no more issues

### Step 6: Final Validation

**Step Configuration**:

- **Purpose**: Confirm successful workflow completion with comprehensive validation
- **Input**: Receives from Step 5: integrated service manifest and all previous outputs
- **Output**: Final deliverables matching workflow Expected Outputs specification
- **Sub-workflow**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from all previous steps
2. **List comprehensive validation requirements**:
   - End-to-end TypeScript compilation
   - Schema validation completeness
   - Mock data accuracy
   - Service manifest functionality
3. **Determine the standards** for final validation: All previously applied standards
4. **Create single task assignment** for comprehensive validation
5. **Use TodoRead** to verify all previous tasks completed successfully
6. **Use TodoWrite** to create final validation task: ['Comprehensive validation - pending']
7. **Prepare comprehensive validation assignment**

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

Request the subagent to perform comprehensive validation:

    >>>
    **ultrathink: adopt the Comprehensive Validator mindset**

    - You're a **Comprehensive Validator** with expertise in end-to-end validation and quality assurance who follows these principles:
      - **Complete Testing**: Validate entire operation lifecycle from schema to service
      - **Type Safety Verification**: Ensure end-to-end type safety throughout
      - **Integration Testing**: Confirm all components work together seamlessly

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Assignment**
    You're assigned to perform final comprehensive validation for operation: [OPERATION_NAME]

    **Steps**

    1. Verify complete TypeScript compilation across all created files
    2. Test that schemas validate properly with mock data
    3. Confirm operation manifest loads and functions correctly
    4. Validate service manifest exports the new operation
    5. Test end-to-end operation invocation (if possible)
    6. Verify all requirements from Step 1 are satisfied

    **Comprehensive Validation Checklist**:
    - [ ] Operation manifest matches original requirements exactly
    - [ ] Schema definitions are type-safe and complete
    - [ ] Mock implementation provides realistic test data
    - [ ] Service manifest properly exports the new operation
    - [ ] All TypeScript types compile without errors
    - [ ] Directory structure follows manifest conventions

    **Report**
    **[IMPORTANT]** You're requested to return the following:

    - Complete validation status
    - Any remaining issues or deviations
    - Final deliverables confirmation

    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Comprehensive validation results'
    modifications: []  # No new modifications in validation
    outputs:
      requirements_satisfied: true|false
      typescript_compiles: true|false
      schemas_validate: true|false
      service_exports: true|false
      end_to_end_works: true|false
    issues: []  # Any remaining problems
    deliverables:
      - 'Operation manifest: manifests/[service]/source/operations/[op]/index.ts'
      - 'Input schema: manifests/[service]/source/operations/[op]/schema/input.ts'
      - 'Output schema: manifests/[service]/source/operations/[op]/schema/output.ts'
      - 'Schema exports: manifests/[service]/source/operations/[op]/schema/index.ts'
      - 'Service integration: manifests/[service]/source/index.ts'
    ```
    <<<

#### Phase 3: Review (Subagents) - Optional

**When Claude Triggers Review**: Only if comprehensive validation reports issues

- **[IMPORTANT]** Review is read-only - subagents must NOT modify any resources or fix issues
- **[IMPORTANT]** Review subagents ONLY report issues and provide recommendations - they do not implement fixes

#### Phase 4: Decision (You)

**What You Do**:

1. **Analyze comprehensive validation report**
2. **Apply completion criteria**:
   - All requirements satisfied
   - All deliverables present and functional
   - No critical issues remaining
3. **Select final action**:
   - **COMPLETE**: All validation passes → Workflow successful
   - **RETRY**: Minor issues found → Re-run failed validation
   - **ESCALATE**: Critical issues → Report to user for guidance
4. **Use TodoWrite** to mark workflow completion status
5. **Package final deliverables** and success confirmation

### Workflow Completion

**Report the workflow output as specified**:

```yaml
operation_manifest:
  service_name: "service-name"
  operation_name: "operationName"
  location: "manifests/[service-name]/source/operations/[operationName]/"
  status: "created|updated"
schema_files:
  input_schema: "manifests/[service-name]/source/operations/[operationName]/schema/input.ts"
  output_schema: "manifests/[service-name]/source/operations/[operationName]/schema/output.ts"
  type_definitions: "manifests/[service-name]/source/operations/[operationName]/schema/index.ts"
service_integration:
  service_manifest_updated: true|false
  operation_exported: true|false
  import_paths_configured: true|false
  alphabetical_ordering: true|false
validation_report:
  typescript_compilation: "success|errors|warnings"
  schema_validation: "pass|fail"
  mock_data_valid: true|false
  end_to_end_testing: "pass|fail"
  requirements_satisfied: true|false
project_structure:
  ensure_project_completed: true|false
  directories_created: ["dir1", "dir2", "..."]
  dependencies_aligned: true|false
  package_configuration: "valid|invalid"
workflow_status: "success|partial|failure"
summary: "Brief description of service operation declaration completion"
```

## Standards to Follow

**🔴 MANDATORY: All standards listed below MUST be followed without exception**

### Core Development Standards

- TypeScript Standards (plugin:coding:standard:typescript) - Type safety, strict mode, and coding conventions for manifest schemas
- Naming Conventions (plugin:coding:standard:naming) - Consistent naming for operations, schemas, and type definitions
- Documentation Guidelines (plugin:coding:standard:documentation) - Schema descriptions and comprehensive code comments
- Functions Standards (plugin:coding:standard:functions) - Mock function structure and implementation patterns

### Code Quality Standards

- General Principles (plugin:coding:standard:general-principles) - DRY, SRP, and other fundamental development principles

### Related Workflows

- Ensure Project (plugin:coding:workflow:ensure-project) - Project structure setup and validation workflow
- Review Code (plugin:coding:workflow:review-code) - Code review process for manifest operations

**Note**: This workflow requires the coding plugin to be enabled for referenced standards and workflows.

### Service Manifest Development Best Practices

#### Schema Definition Patterns

- Always use `as const satisfies JsonSchema` pattern for type safety
- Include comprehensive validation rules (required fields, formats, patterns)
- Provide clear descriptions for all schema properties
- Leverage TypeScript's FromSchema for type generation

#### Mock Implementation Requirements

- Generate realistic mock data that matches output schemas exactly
- Implement proper async/sync patterns based on operation type
- Include comprehensive error handling and edge cases
- Follow operation manifest framework patterns consistently

#### Common Issues to Avoid

- Schema mismatch between manifest and service implementations
- Missing mock data or incomplete object returns
- Path mapping errors in module imports
- Type safety loss through any/unknown types
- Missing async/await in operation mock functions
- Inadequate access control and authorization checks
