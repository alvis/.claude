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

Creates TypeScript-compliant code skeletons with TODO placeholders. Drafts type definitions, function signatures, and test structure while leaving implementation details as TODOs for later completion.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Implement actual business logic
- Create production-ready code
- Write complete tests with assertions
- Modify existing implementations

**When to REJECT**:

- Instructions are too vague to create meaningful types
- Request is for implementation rather than skeleton
- Target directory doesn't exist
- Conflicting with existing code structure

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Analyze Requirements

1. **Parse Instructions**
   - Extract feature requirements from $ARGUMENTS
   - Identify types, interfaces, and functions needed
   - Determine file structure

2. **Research Context**
   - Read existing patterns in codebase
   - Identify related modules
   - Check coding standards

3. **Plan Structure**
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
   - Create function stubs
   - Add parameter types
   - Define return types
   - Mark bodies with TODO

### Step 3: Draft Test Structure

1. **Create Test Files**
   - Set up test suites
   - Add describe blocks
   - Create test case placeholders
   - Mark assertions with TODO

2. **Add Test Utilities**
   - Draft mock factories
   - Create fixture templates
   - Set up test helpers

### Step 4: Validation

1. **TypeScript Check**
   - Verify types compile
   - Check for type errors
   - Ensure imports resolve

2. **Structure Check**
   - Verify file organization
   - Check naming conventions
   - Validate TODO format

### Step 5: Reporting

**Output Format**:

```
[✅/❌] Command: draft-code $ARGUMENTS

## Summary
- Instruction: [parsed instruction]
- Files created: [count]
- Types defined: [count]
- Functions drafted: [count]
- TODOs placed: [count]

## Actions Taken
1. Created type definitions at [path]
2. Drafted function signatures at [path]
3. Set up test structure at [path]
4. Verified TypeScript compilation

## Files Created
- [path] - [description]
- [path] - [description]

## TODOs Summary
- Implementation: [count]
- Tests: [count]
- Documentation: [count]

## Next Steps
1. Review type definitions
2. Complete implementations with /complete-code
3. Add test assertions
```

## 📝 Examples

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
