---
name: draft-code
description: Draft TypeScript-compliant code skeleton with TODO placeholders. Use when starting new implementations, creating code scaffolds, or preparing test structure for TDD.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task
argument-hint: <instruction>
---

# Draft Code Skeleton

Creates TypeScript-compliant code skeletons with TODO placeholders. Drafts type definitions, function signatures, and test structure while leaving implementation details as TODOs for later completion. Corresponds to Steps 0-1 (Design Discovery + Skeleton Creation) of the TDD lifecycle.

## Purpose & Scope

**What this command does NOT do**:

- Implement actual business logic
- Create production-ready code
- Write complete tests with assertions
- Modify existing implementations

**When to REJECT**:

- Instructions are too vague to create meaningful types
- Request is for implementation rather than skeleton
- Target directory does not exist
- Conflicting with existing code structure

## Applicable Standards

When executing this skill, the following standards apply:

| Standard | Purpose |
|---|---|
| `documentation/write` | JSDoc structure and placeholder comments |
| `file-structure` | Project directory layout and organization |
| `function/write` | Function signatures, parameter types, return types |
| `naming/write` | Naming conventions for files, types, functions |
| `testing/write` | Test file structure, describe/it patterns |
| `typescript/write` | Type definitions, interfaces, generics |
| `universal/write` | General code authoring conventions |

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Design Direction Discovery

1. **Parse Instructions**
   - Extract feature requirements from $ARGUMENTS
   - Identify types, interfaces, and functions needed
   - Determine file structure
   - Determine if running as standalone or as part of composite (`--from-composite`)

2. **Discover Design Documentation**
   - Look for `DESIGN.md` in project root using Glob (NEVER use `find` in bash)
   - Search for `**/*.md` files that might contain design specifications
   - Look for architecture documentation files

3. **Discover Handover Documentation**
   - Look for `CONTEXT.md`, `NOTES.md`, `PLAN.md` in project root using Glob
   - If handover files exist, extract:
     - **From CONTEXT.md**: Current state, key decisions, gotchas, established patterns
     - **From NOTES.md**: Problems already solved, what worked/didn't, key insights
     - **From PLAN.md**: Goals, success criteria, current phase, task breakdown

4. **Research Context**
   - Read existing patterns in codebase
   - Identify related modules
   - Check coding standards
   - Merge design specifications with handover context

5. **Plan Structure**
   - Map out file organization
   - Define type hierarchy
   - Plan test structure

### Step 2: Draft Types and Interfaces

1. **Create Type Definitions**
   - Draft interfaces with JSDoc
   - Create type aliases
   - Define enums where appropriate
   - Add TODO comments for validation logic

2. **Draft Function Signatures**
   - Create function stubs with proper parameter and return types
   - Mark bodies with TODO using the CODE DRAFTING PATTERNS below
   - Follow function design standards

**CODE DRAFTING PATTERNS**: When drafting incomplete implementations:
- Use `describe.todo`, `it.todo` for test placeholders that need implementation
- Use `// TODO:` comments to mark incomplete code sections
- For incomplete code where a return is expected or return type is void:
  - Throw `new Error('IMPLEMENTATION: <description of what is missing>, requiring <parameters required as JSON object>')`
  - This prevents TypeScript type errors and unused variable complaints
  - Example: `throw new Error(\`IMPLEMENTATION: user authentication logic needed, requiring \${JSON.stringify({ userId, token })}\`)`

### Step 3: Draft Test Structure

1. **Create Test Files**
   - Set up test suites with describe blocks
   - If no interface provided: Use `describe.todo()` and `it.todo()` syntax
   - If interface provided: Create actual test cases with assertions (tests will fail until implementation)
   - Structure tests following AAA pattern preparation
   - Plan test cases covering all functionality

2. **Add Test Utilities**
   - Draft mock factories
   - Create fixture templates
   - Set up test helpers

### Step 4: Validation

1. **TypeScript Check**
   - Verify types compile with no errors
   - Check for type errors
   - Ensure imports resolve

2. **Standards Check**
   - Run linter to ensure standards compliance
   - Verify file organization
   - Check naming conventions
   - Validate TODO format

3. **Run Scripts**
   - Execute `npm run test` or equivalent
   - Execute `npm run lint` or equivalent
   - Report any issues found

### Step 5: Reporting

**Output Format**:

```
[OK/FAIL] Command: draft-code $ARGUMENTS

## Summary
- Instruction: [parsed instruction]
- Files created: [count]
- Types defined: [count]
- Functions drafted: [count]
- TODOs placed: [count]

## Actions Taken
1. Discovered design context from [sources]
2. Created type definitions at [path]
3. Drafted function signatures at [path]
4. Set up test structure at [path]
5. Verified TypeScript compilation

## Files Created
- [path] - [description]
- [path] - [description]

## TODOs Summary
- Implementation: [count]
- Tests: [count]
- Documentation: [count]

## Next Steps
1. Review type definitions
2. Complete implementations with /coding:complete-code
3. Add test assertions
```

## Examples

### Draft New Service

```bash
/draft-code "Create user authentication service with login, logout, and token refresh"
# Creates:
# - src/services/auth/types.ts (interfaces)
# - src/services/auth/auth.service.ts (stubs)
# - src/services/auth/auth.test.ts (test structure)
```

### Draft API Endpoint

```bash
/draft-code "REST endpoint for product CRUD operations"
# Creates skeleton for controller, service, and tests
```

### Draft Utility Module

```bash
/draft-code "Date formatting utilities with timezone support"
# Creates type-safe utility functions with TODOs
```

### Error Case

```bash
/draft-code "thing"
# Error: Instruction too vague
# Suggestion: Provide specific requirements like "Create validation helpers for user input"
```
