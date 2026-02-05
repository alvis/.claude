---
name: implement-data-controller
description: Implement complete data controller with schema and operations for business area. Use when creating new data controllers, implementing CRUD operations, or scaffolding backend services with validation.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Edit, MultiEdit, Read, Write, Grep, Glob, Task
argument-hint: <controller name> [--area=...]
---

# Implement Data Controller

Implements a complete data controller for a specified business area, including schema definitions, CRUD operations, validation logic, and integration with existing services. Follows established patterns and coding standards.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Create database migrations (use separate migration command)
- Implement authentication/authorization logic
- Create frontend components
- Deploy or configure infrastructure

**When to REJECT**:

- Controller name is invalid or missing
- Business area is not well-defined
- Request involves frontend work
- No existing service patterns to follow

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Analyze Requirements

1. **Parse Arguments**
   - Extract controller name from $ARGUMENTS
   - Parse --area flag if provided
   - Validate naming conventions

2. **Discover Project Context**
   - Read existing controllers for patterns
   - Identify service layer conventions
   - Check existing schemas and models
   - Review validation patterns in use

3. **Plan Implementation**
   - Identify required files
   - Map dependencies
   - Plan test coverage

### Step 2: Implement Schema

1. **Create Data Schema**
   - Define TypeScript interfaces
   - Add validation rules
   - Include JSDoc documentation
   - Follow existing patterns

2. **Create Validation Logic**
   - Implement input validation
   - Add business rule validation
   - Create error handling

### Step 3: Implement Controller

1. **Create Controller File**
   - Implement CRUD operations
   - Add proper error handling
   - Include logging
   - Follow DRY principles

2. **Implement Service Layer**
   - Create service functions
   - Add business logic
   - Implement transactions where needed

### Step 4: Create Tests

1. **Unit Tests**
   - Test schema validation
   - Test controller methods
   - Test service functions

2. **Integration Tests**
   - Test API endpoints
   - Test database operations
   - Test error scenarios

### Step 5: Reporting

**Output Format**:

```
[✅/❌] Command: implement-data-controller $ARGUMENTS

## Summary
- Controller: [name]
- Business area: [area]
- Files created: [count]
- Test coverage: [percentage]

## Actions Taken
1. Created schema at [path]
2. Implemented controller at [path]
3. Created service layer at [path]
4. Generated tests at [path]

## Files Created
- [path/to/schema.ts]
- [path/to/controller.ts]
- [path/to/service.ts]
- [path/to/tests/]

## Next Steps
1. Review implementation
2. Run tests
3. Create database migrations if needed
4. Add to API routes
```

## 📝 Examples

### Simple Usage

```bash
/implement-data-controller "user"
# Creates complete user data controller with CRUD operations
```

### With Business Area

```bash
/implement-data-controller "order" --area="e-commerce"
# Creates order controller following e-commerce domain patterns
```

### Error Case

```bash
/implement-data-controller
# Error: Controller name required
# Suggestion: Provide name like '/implement-data-controller "product"'
```
