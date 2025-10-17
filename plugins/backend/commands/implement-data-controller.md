---
allowed-tools: "Bash, Edit, MultiEdit, Read, Write, Grep, Glob, Task"

argument-hint: "<controller name> [--area=...]"

description: "implement complete data controller with schema and operations for business area"
---

# Implement Data Controller

Implement a complete data controller for a set of entities that are closely related to a feature or business area by executing data schema implementation and data operations implementation workflows.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Create business logic or service layer code
- Implement frontend components or UI elements
- Handle authentication or authorization logic
- Generate migration files for production deployment
- Create API endpoints or route handlers

**When to REJECT**:

- When the controller name doesn't exist in the Notion Data Controllers database
- When project structure is missing required Prisma configuration
- When requesting implementation of non-data operations (business logic)
- When the area filter specifies invalid operation types or entities



## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Follow Implement Data Schema Workflow

- Execute implement-data-schema.md

### Step 2: Follow Implement Data Operation Workflow

- Execute implement-data-operation.md

### Step 3: Reporting

**Output Format**:

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Schema files created: [count]
- Operation functions implemented: [count]
- Integration tests written: [count]
- TypeScript types generated: [pass/fail]
- All tests passing: [pass/fail]
- Standards compliance: [PASS/FAIL]

## Actions Taken
1. [Action with result]
2. [Action with result]

## Workflows Applied
- Implement Data Schema: [Success/Failed]
- Implement Data Operation: [Success/Failed]

## Data Controller Details
- Controller name: [name]
- Notion page ID: [id]
- Entities implemented: [count] ([entity1, entity2, ...])
- Operations implemented: [count] ([operation1, operation2, ...])

## Files Modified
- Schema files: [list of .prisma files]
- Operation files: [list of operations/*.ts files]
- Test files: [list of spec/*.spec.ts files]
- Controller files: [source/index.ts and related files]

## Issues Found (if any)
- **Issue**: [Description]
  **Fix**: [Applied fix or suggestion]
```

## 📝 Examples

### Simple Usage

```bash
/implement-data-controller "product-offering"
# implements complete data controller for product offering entities
# creates all schemas and operations found in notion specification
```

### Complex Usage with Operations Filter

```bash
/implement-data-controller "user-management" --area="get,set,list"
# implements only get, set, and list operations for user management
# excludes drop or other operations not specified
```

### Entity-Specific Implementation

```bash
/implement-data-controller "billing" --area="invoice,payment"
# implements only invoice and payment entities from billing controller
# skips other entities that may exist in the specification
```

### Complete Feature Implementation

```bash
/implement-data-controller "subscription-management"
# implements all entities and operations for subscription management
# includes schema generation, operation implementation, and full test coverage
```

### Error Case Handling

```bash
/implement-data-controller "non-existent-controller"
# Error: Controller 'non-existent-controller' not found in Notion database
# Suggestion: Check available controllers with notion search
# Alternative: Use '/implement-data-controller --list' to see valid options
```

### With Specific Operation Types

```bash
/implement-data-controller "analytics" --area="drop"
# implements only drop operations for analytics entities
# ensures proper status-based logic for data removal
```
