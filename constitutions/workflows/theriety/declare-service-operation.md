# Declare Service Operation

**Purpose**: Define a new operation for a service, creating the manifest schema definition with proper type safety and documentation.
**When to use**: When adding a new operation to an existing service or creating the first operation for a new service manifest project.
**Prerequisites**:

- Service requirements documented on Notion
- Understanding of the operation's input/output schema
- Familiarity with JSON Schema and TypeScript types
- Access to monorepo root and package manager

## Expert Role

You are a **Backend Service Architect** specializing in API design and type-safe service operations. Your expertise includes:

- **Schema-First Design**: Define clear contracts before implementation to ensure API consistency and type safety
- **Separation of Concerns**: Maintain clear boundaries between manifest definitions (API contracts) and service implementations (business logic)
- **Type Safety**: Leverage TypeScript's type system with JSON Schema to eliminate runtime type errors
- **Mock-Driven Development**: Create comprehensive mocks that facilitate testing and development parallelization
- **Documentation as Code**: Ensure schemas serve as both runtime validation and living documentation

## Steps

### 0. Workflow Preparation and Task Management

**Initialize workflow tracking and identify reusable components**:

- [ ] Identify available task tracking tools and use the most appropriate one
- [ ] Create initial todo items for all known major workflow steps
- [ ] Include estimated complexity for each task
- [ ] Set initial status to 'pending' for all tasks
- [ ] **IMPORTANT**: Be prepared to add more todo items as new tasks are discovered
- [ ] Mark this initialization task as 'completed' once done

**Identify existing workflows to reuse**:

- [ ] Search for applicable existing workflows (e.g., ensure-project, write-code-tdd)
- [ ] List workflows this workflow will reference
- [ ] Document workflow dependencies in a clear format
- [ ] Map which steps will use each referenced workflow
- [ ] Avoid recreating steps that existing workflows already handle

**Plan agent delegation strategy**:

- [ ] Identify available specialized agents in the system
- [ ] Determine which steps require specialized expertise
- [ ] Create a delegation plan mapping steps to appropriate agents
- [ ] Document parallel execution opportunities where dependencies allow
- [ ] Specify verification points for quality assurance

### 1. Gather Operation Requirements

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

Obtain the complete operation specification from documentation or requirements.

**Core actions**:

- [ ] Visit the Notion page for the service operation (if specified)
- [ ] Extract input schema requirements with field types and validation rules
- [ ] Extract output schema requirements (if operation returns data)

**Verification**:

- [ ] Subagent/workflow self-verification: Requirements fully understood and documented
- [ ] Primary agent verification: All requirements extracted and clear
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during requirements analysis

### 3. Ensure Project Structure Using ensure-project Workflow

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

Set up the manifest project if it doesn't exist yet.

**Core actions**:

Follow the [ensure-project workflow](@../project/ensure-project.md) with the following service manifest structure requirements:

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

**Structure Requirements for ensure-project:**

- [ ] Manifest directory under `manifests/[service-name]/`
- [ ] Package.json with service-specific configuration and exports
- [ ] Source directory with index.ts and operations subdirectory
- [ ] Spec directory for tests
- [ ] All dependencies aligned with existing manifest projects in monorepo

**Verification**:

- [ ] Subagent/workflow self-verification: Project structure validated and bootstrapped
- [ ] Primary agent verification: Dependencies installed and project functional
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during project setup

### 4. Create Operation Schema Structure

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

Build the schema definition files for the new operation.

**Core actions**:

```bash
manifests/[service-name]/source/operations/[operationName]/
├── index.ts        # Operation manifest definition
└── schema/
    ├── index.ts    # Schema exports and types
    ├── input.ts    # Input schema definition
    └── output.ts   # Output schema (skip for void operations)
```

- [ ] Create operation directory with camelCase naming
- [ ] Define input schema with proper JSON Schema format
- [ ] Define output schema (if operation returns data)
- [ ] Export TypeScript types using `FromSchema`
- [ ] Add schema validation rules (required fields, formats, patterns)

**Verification**:

- [ ] Subagent/workflow self-verification: Schema structure created with proper types
- [ ] Primary agent verification: All schemas match operation requirements
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during schema creation

**Input Schema Example:**

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

**Schema Export Pattern:**

```typescript
// schema/index.ts
import input from './input';
import output from './output'; // omit if the operation that doesn't return

import type { FromSchema } from '@theriety/manifest';

export type Input = FromSchema<typeof input>;
export type Output = FromSchema<typeof output>; // omit if the operation that doesn't return

export default { input, output };
```

### 5. Create Operation Manifest

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

Define the operation manifest with mock implementation.

**Core actions**:

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

- [ ] Import `createOperationManifest` from framework
- [ ] Set `path: import.meta.url` for operation identification
- [ ] Configure `async: true` for asynchronous operations
- [ ] Implement comprehensive mock with realistic data
- [ ] Ensure mock matches output schema exactly

**Verification**:

- [ ] Subagent/workflow self-verification: Manifest created with proper mock implementation
- [ ] Primary agent verification: Mock data matches schema requirements
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during manifest creation

### 6. Update Service Manifest Index

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

Register the new operation in the service manifest.

**Core actions**:

```typescript
// source/index.ts
import { createServiceManifest } from '@theriety/manifest';

import packageJson from '../package.json';
import storeSecret from '#operations/storeSecret';
import revealSecret from '#operations/revealSecret';
// add new operation import
import newOperation from '#operations/newOperation';

export default createServiceManifest({
  packageJson,
  operations: {
    storeSecret,
    revealSecret,
    // add new operation
    newOperation,
  },
});
```

- [ ] Import the new operation using path mapping
- [ ] Add operation to the operations object
- [ ] Maintain alphabetical ordering for consistency

**Verification**:

- [ ] Subagent/workflow self-verification: Service manifest updated with new operation
- [ ] Primary agent verification: All imports and exports working correctly
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during manifest update

### 7. Final Review and Comprehensive Validation

**Primary agent performs final review of all delegated work**:

**Task tracking review**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Verify all tracked tasks show 'completed' status
- [ ] Confirm no tasks remain in 'pending' or 'in_progress' state

**Subagent work review**:

- [ ] Review outputs from all delegated agents
- [ ] Verify each subagent's self-verification was performed
- [ ] Double-check work quality meets standards
- [ ] Confirm all referenced workflows were properly executed

**Requirements validation**:

- [ ] Operation manifest matches Notion specification exactly
- [ ] Schema definitions are type-safe and complete
- [ ] Mock implementation provides realistic test data
- [ ] Service manifest properly exports the new operation
- [ ] All TypeScript types compile without errors

**Final sign-off**:

- [ ] Primary agent approves all work
- [ ] Mark this final review task as 'completed' in task tracking tool
- [ ] Document any deviations or follow-up items

## Standards Applied

### 🔴 MANDATORY: All standards listed below MUST be followed without exception

- [TypeScript](@../../standards/code/typescript.md) - Type safety, strict mode, and coding conventions
- [Naming Conventions](@../../standards/code/naming.md) - Consistent naming for operations, schemas, and types
- [Documentation](@../../standards/code/documentation.md) - Schema descriptions and code comments

## Common Issues

- **Schema Mismatch**: Input/output types don't match between manifest and service → Ensure you import types from manifest schema in service implementation
- **Missing Mock Data**: Mock returns incomplete data → Always return complete objects matching the full output schema
- **Path Mapping Errors**: Cannot find module '#operations/...' → Check package.json imports configuration and tsconfig paths
- **Type Safety Lost**: Using `any` types in schemas → Always use `as const satisfies JsonSchema` pattern
- **Async/Await Issues**: Forgetting async in mock functions → All operation mocks must return promises
- **Access Control Missing**: No authorization checks → Always call `access.verify()` before executing business logic

## Output Template

### Expected Directory Structure

After completing this workflow, you should have:

```plaintext
manifests/[service-name]/
└── source/
    └── operations/
        └── [operationName]/
            ├── index.ts        # Manifest definition
            └── schema/
                ├── index.ts    # Type exports
                ├── input.ts    # Input schema
                └── output.ts   # Output schema (if applicable)
```
