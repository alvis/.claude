---
name: declare-service-operation
description: Define service operations with manifest schema
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Edit, MultiEdit, Read, Write, Grep, Glob, Task
argument-hint: <service name> <operation name> [--notion-url=...]
---

# Declare Service Operation

Defines a new operation for a service, creating the manifest schema definition with proper type safety and documentation. Produces type-safe manifest definitions by decomposing schema creation, implementing validation, and integrating with existing service structure.

## Purpose & Scope

**When to use**: When adding a new operation to an existing service or creating the first operation for a new service manifest project.

**Prerequisites**: Service requirements documented on Notion, understanding of the operation's input/output schema, familiarity with JSON Schema and TypeScript types, access to monorepo root and package manager.

**What this command does NOT do**:

- Implement the actual operation business logic
- Create database migrations or schema changes
- Deploy the service or configure infrastructure
- Modify existing operations

**When to REJECT**:

- Service name or operation name is missing
- No operation requirements or documentation available
- Operation already exists in the service manifest
- Required dependencies are not available in the monorepo

## Role

You are a **Service Orchestration Director** who coordinates the workflow like a project director overseeing API development. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break complex schema definition work into parallel tasks and assign to specialized subagents
- **Parallel Coordination**: Maximize efficiency by running multiple subagents simultaneously for independent tasks
- **Quality Oversight**: Review manifest definitions objectively without being involved in coding details
- **Decision Authority**: Make go/no-go decisions based on subagent reports and schema validation results

## Inputs and Outputs

### Required Inputs

- **Service Name**: Target service identifier for manifest creation
- **Operation Requirements**: Complete operation specification from documentation (typically Notion)
- **Operation Name**: Specific operation identifier (camelCase naming)

### Optional Inputs

- **Existing Manifest Path**: Path to existing service manifest directory (default: auto-detect)
- **Schema Complexity**: Simple/Complex flag to determine batching strategy (default: auto-detect)

### Expected Outputs

- **Operation Manifest**: Complete operation definition with schema and mock implementation
- **Schema Files**: TypeScript-compatible JSON schemas for input/output validation
- **Type Definitions**: Generated TypeScript types using FromSchema pattern
- **Service Integration**: Updated service manifest index with new operation registration
- **Validation Report**: Confirmation that all schemas compile and mock data validates

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Gather Operation Requirements

Extract and validate complete operation specifications from documentation.

#### Phase 1: Planning (You)

1. **Receive inputs** from workflow invocation (service name, operation name, documentation sources)
2. **List all documentation sources** that need to be accessed
3. **Determine the standards** to send to subagents: TypeScript, Documentation, Naming
4. **Create task assignment** for requirements gathering
5. **Use TodoWrite** to create task list: ['Requirements extraction - pending']

#### Phase 2: Execution (Subagents)

Assign requirements gathering to a specialized subagent:

    >>>
    **ultrathink: adopt the Backend Service Architect mindset**

    - You're a **Backend Service Architect** with deep expertise in API design and type-safe service operations who follows these technical principles:
      - **Schema-First Design**: Define clear contracts before implementation
      - **Type Safety**: Leverage TypeScript's type system with JSON Schema
      - **Documentation as Code**: Ensure schemas serve as both runtime validation and living documentation

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Standards to follow**: TypeScript, Documentation, Naming conventions

    **Assignment**
    Gather requirements for operation: [OPERATION_NAME] in service: [SERVICE_NAME]

    **Steps**
    1. Visit the Notion page for the service operation (if URL provided)
    2. Extract complete input schema requirements with field types, validation rules, and constraints
    3. Extract output schema requirements (if operation returns data) with proper typing
    4. Document any special validation rules or business logic constraints
    5. Identify required vs optional fields for both input and output

    **Report** (<1000 tokens):
    ```yaml
    status: success|failure|partial
    summary: 'Brief description of requirements gathered'
    modifications: []
    outputs:
      input_schema_spec: 'Detailed input schema requirements'
      output_schema_spec: 'Detailed output schema requirements or null'
      validation_rules: ['rule1', 'rule2', ...]
      operation_type: 'sync|async'
    issues: []
    ```
    <<<

#### Phase 3: Decision (You)

1. Validate requirements completeness (input schema, output schema, validation rules)
2. **PROCEED** if complete, **FIX ISSUES** if incomplete, **ROLLBACK** if critical documentation missing

### Step 2: Ensure Project Structure

Set up the manifest project structure if it doesn't exist yet.

- **Sub-workflow**: plugin:coding:workflow:ensure-project
- Load and execute the ensure-project sub-workflow with these requirements:

```plaintext
# Service manifest directory structure
manifests/[service-name]/
+-- package.json
+-- source/
|   +-- index.ts
|   +-- operations/
+-- spec/
    +-- index.spec.ts
```

- Manifest directory under `manifests/[service-name]/`
- Package.json with service-specific configuration and exports
- Source directory with index.ts and operations subdirectory
- Spec directory for tests
- All dependencies aligned with existing manifest projects in monorepo

**Note**: This step requires the coding plugin to be enabled.

### Step 3: Create Schema Definitions

Build schema definition files for the new operation with proper type safety. Input and output schemas can be created in parallel.

#### Phase 1: Planning (You)

1. List schema creation tasks (input schema, output schema if needed, schema exports)
2. Create batches for parallel execution
3. Use TodoWrite to track tasks

#### Phase 2: Execution (Subagents)

Spin up subagents to create schemas in parallel, up to **3** subtasks at a time:

    >>>
    **ultrathink: adopt the Schema Definition Specialist mindset**

    - You're a **Schema Definition Specialist** with deep expertise in JSON Schema and TypeScript integration who follows these technical principles:
      - **Type Safety First**: Ensure all schemas compile to strict TypeScript types
      - **Validation Completeness**: Include all necessary validation rules and constraints
      - **Documentation Integration**: Every schema field must have clear descriptions

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Standards to follow**: TypeScript, Naming conventions

    **Assignment**
    Create schema files for operation: [OPERATION_NAME]

    Target directory structure:
    ```
    manifests/[service-name]/source/operations/[operationName]/
    +-- index.ts        # Operation manifest definition (Step 4)
    +-- schema/
        +-- index.ts    # Schema exports and types
        +-- input.ts    # Input schema definition
        +-- output.ts   # Output schema (skip for void operations)
    ```

    **Steps**
    1. Create operation directory with camelCase naming
    2. Define input schema with proper JSON Schema format using requirements
    3. Define output schema (if operation returns data) with proper typing
    4. Export TypeScript types using `FromSchema` pattern
    5. Add comprehensive schema validation rules (required fields, formats, patterns)
    6. Ensure all schemas use `as const satisfies JsonSchema` pattern

    **Schema Patterns to Follow**:

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
    import output from './output'; // omit if the operation doesn't return

    import type { FromSchema } from '@theriety/manifest';

    export type Input = FromSchema<typeof input>;
    export type Output = FromSchema<typeof output>; // omit if void

    export default { input, output };
    ```

    **Report** (<1000 tokens):
    ```yaml
    status: success|failure|partial
    summary: 'Brief description of schemas created'
    modifications: ['schema/input.ts', 'schema/output.ts', 'schema/index.ts']
    outputs:
      input_schema_created: true|false
      output_schema_created: true|false|not_required
      type_exports_created: true|false
      typescript_compiles: true|false
    issues: []
    ```
    <<<

#### Phase 3: Review (Subagents) - Required

Always review schema compilation and type safety:

    >>>
    **ultrathink: adopt the TypeScript Review Expert mindset**

    - Review is read-only - do NOT modify any resources or fix issues
    - Review TypeScript compilation, schema format (`as const satisfies JsonSchema`), FromSchema types, and requirements alignment

    **Report** (<500 tokens):
    ```yaml
    status: pass|fail
    checks:
      typescript_compiles: pass|fail
      schema_format_valid: pass|fail
      types_generated: pass|fail
      requirements_match: pass|fail
    fatals: []
    warnings: []
    recommendation: proceed|retry|rollback
    ```
    <<<

#### Phase 4: Decision (You)

- **PROCEED** if schemas validated, **FIX ISSUES** if compilation or validation failures, **ROLLBACK** if critical type safety issues

### Step 4: Build Operation Manifest

Create the operation manifest with comprehensive mock implementation.

#### Execution (Subagents)

    >>>
    **ultrathink: adopt the Operation Manifest Builder mindset**

    - You're an **Operation Manifest Builder** with deep expertise in manifest framework and mock implementations

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Standards to follow**: TypeScript, Functions, Naming conventions

    **Assignment**
    Create the operation manifest for: [OPERATION_NAME]

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

    **Report** (<1000 tokens):
    ```yaml
    status: success|failure|partial
    summary: 'Brief description of manifest creation'
    modifications: ['operations/[operationName]/index.ts']
    outputs:
      manifest_created: true|false
      mock_implemented: true|false
      typescript_compiles: true|false
      mock_validates: true|false
    issues: []
    ```
    <<<

#### Review (Subagents) - Required

- Review mock data matches output schema, framework patterns used correctly, TypeScript type safety, async/sync configuration
- Review is read-only - do NOT modify any resources

### Step 5: Integrate with Service

Register the new operation in the service manifest index.

#### Execution (Subagents)

    >>>
    **ultrathink: adopt the Service Integration Specialist mindset**

    - You're a **Service Integration Specialist** with deep expertise in service manifest management

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Standards to follow**: TypeScript, Naming conventions

    **Assignment**
    Integrate operation [OPERATION_NAME] into the service manifest

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

    **Report** (<1000 tokens):
    ```yaml
    status: success|failure|partial
    modifications: ['source/index.ts']
    outputs:
      operation_imported: true|false
      operation_registered: true|false
      alphabetical_order: true|false
      typescript_compiles: true|false
    issues: []
    ```
    <<<

#### Review (Subagents) - Required

- Review import resolution, operation registration, export functionality, alphabetical ordering
- Review is read-only - do NOT modify any resources

### Step 6: Final Validation

Comprehensive end-to-end validation of the entire operation declaration.

#### Execution (Subagents)

    >>>
    **ultrathink: adopt the Comprehensive Validator mindset**

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Assignment**
    Perform final comprehensive validation for operation: [OPERATION_NAME]

    **Validation Checklist**:
    - [ ] Operation manifest matches original requirements exactly
    - [ ] Schema definitions are type-safe and complete
    - [ ] Mock implementation provides realistic test data
    - [ ] Service manifest properly exports the new operation
    - [ ] All TypeScript types compile without errors
    - [ ] Directory structure follows manifest conventions

    **Steps**
    1. Verify complete TypeScript compilation across all created files
    2. Test that schemas validate properly with mock data
    3. Confirm operation manifest loads and functions correctly
    4. Validate service manifest exports the new operation
    5. Test end-to-end operation invocation (if possible)
    6. Verify all requirements from Step 1 are satisfied

    **Report** (<1000 tokens):
    ```yaml
    status: success|failure|partial
    summary: 'Comprehensive validation results'
    modifications: []
    outputs:
      requirements_satisfied: true|false
      typescript_compiles: true|false
      schemas_validate: true|false
      service_exports: true|false
      end_to_end_works: true|false
    issues: []
    deliverables:
      - 'Operation manifest: manifests/[service]/source/operations/[op]/index.ts'
      - 'Input schema: manifests/[service]/source/operations/[op]/schema/input.ts'
      - 'Output schema: manifests/[service]/source/operations/[op]/schema/output.ts'
      - 'Schema exports: manifests/[service]/source/operations/[op]/schema/index.ts'
      - 'Service integration: manifests/[service]/source/index.ts'
    ```
    <<<

### Step 7: Reporting

**Output Format**:

```
[pass/fail] Command: declare-service-operation $ARGUMENTS

## Summary
- Service: [service-name]
- Operation: [operationName]
- Schema files: [count]
- TypeScript compilation: [status]

## Outputs
operation_manifest:
  service_name: "service-name"
  operation_name: "operationName"
  location: "manifests/[service-name]/source/operations/[operationName]/"
schema_files:
  input_schema: "manifests/.../schema/input.ts"
  output_schema: "manifests/.../schema/output.ts"
  type_definitions: "manifests/.../schema/index.ts"
service_integration:
  service_manifest_updated: true|false
  operation_exported: true|false
validation_report:
  typescript_compilation: "success|errors|warnings"
  schema_validation: "pass|fail"
  mock_data_valid: true|false
  requirements_satisfied: true|false

## Next Steps
1. Implement operation business logic
2. Run integration tests
3. Deploy service update
```

## Standards

The following standards MUST be followed without exception:

- **TypeScript Standards** (plugin:coding:standard:typescript) - Type safety, strict mode, and coding conventions for manifest schemas
- **Naming Conventions** (plugin:coding:standard:naming) - Consistent naming for operations, schemas, and type definitions
- **Documentation Guidelines** (plugin:coding:standard:documentation) - Schema descriptions and comprehensive code comments
- **Functions Standards** (plugin:coding:standard:function) - Mock function structure and implementation patterns
- **General Principles** (plugin:coding:standard:universal) - DRY, SRP, and other fundamental development principles

### Service Manifest Best Practices

- Always use `as const satisfies JsonSchema` pattern for type safety
- Include comprehensive validation rules (required fields, formats, patterns)
- Provide clear descriptions for all schema properties
- Leverage TypeScript's FromSchema for type generation
- Generate realistic mock data that matches output schemas exactly
- Implement proper async/sync patterns based on operation type
- Avoid schema mismatch between manifest and service implementations
- Avoid missing mock data or incomplete object returns
- Avoid path mapping errors in module imports

**Note**: This workflow requires the coding plugin to be enabled for referenced standards and workflows.

## Examples

### Declare New Operation

```bash
/declare-service-operation "auth" "verifyToken" --notion-url="https://notion.so/..."
# Creates complete operation manifest with schema, types, and mock for auth service
```

### Simple Void Operation

```bash
/declare-service-operation "notification" "sendAlert"
# Creates operation manifest for a void (no return) operation
```

### Error Case

```bash
/declare-service-operation
# Error: Service name and operation name required
# Suggestion: Provide names like '/declare-service-operation "auth" "verifyToken"'
```
