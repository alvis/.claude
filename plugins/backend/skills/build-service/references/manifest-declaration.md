# Manifest Declaration — Schema & Operation Patterns

This reference is consulted by **Step 2 (Declare Operations)** when a new manifest package needs to be created or new operations added to an existing manifest. Skip if all operations already have manifests (extend mode with existing ops).

## Phase 2: Execution (Subagents)

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

## Phase 3: Review (Subagents)

Review TypeScript compilation, schema format, FromSchema types, and requirements alignment (read-only).

## Phase 4: Decision (You)

- **PROCEED** if schemas validated → Step 3
- **FIX ISSUES** if compilation failures → retry Phase 2

## Manifest Project Structure (when creating a new manifest package)

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
