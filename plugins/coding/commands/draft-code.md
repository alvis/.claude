---
allowed-tools: "Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task"

argument-hint: "<instruction> - Specify the area of code and flow to draft"

description: "Draft TypeScript-compliant code skeleton with TODO placeholders"
---

# Draft Code Skeleton

Create a code skeleton with TypeScript-compliant function signatures and logical structure, using TODO placeholders for implementation details. This command follows test-driven development principles by creating both draft tests and implementation structure without execution.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Execute or run any tests (uses describe.todo/it.todo patterns)
- Create production-ready implementation code
- Perform actual business logic implementation
- Execute quality gates or validation tests
- Create fully functional, executable code

**When to REJECT**:

- When full implementation is required immediately
- When tests need to actually run and pass
- When production-ready code is requested
- When the request is for executable, working code
- When comprehensive testing execution is needed

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Follow Write-Code Workflow (Step 1 Only)

- Execute workflow:write-code with resume parameters:
  - **Resume From Step**: 1 (Draft Code Skeleton & Test Structure)
  - **Change Direction**: Include specific structural requirements from command arguments
  - **Skip Steps**: [2, 3, 4, 5] (only execute Steps 0-1)
- Focus on:
  - Step 0: Design Direction Discovery
  - Step 1: Draft Code Skeleton & Test Structure

**Resume Parameter Examples**:

**Example 1: Draft skeleton with specific patterns**
```
Resume From Step: 1
Change Direction: "Use factory pattern for object creation and builder pattern for configuration"
Skip Steps: [2, 3, 4, 5] (only draft, no implementation)
```

**Example 2: Draft skeleton and continue to implementation**
```
Resume From Step: 1
Change Direction: "Create service layer with dependency injection"
Skip Steps: [3, 4] (draft, implement, refactor - skip test fixing)
```

**Example 3: Draft with specific architecture**
```
Resume From Step: 0
Change Direction: "Follow hexagonal architecture with ports and adapters"
Skip Steps: [2, 3, 4, 5] (discover design, draft structure only)
```

### Step 2: Draft Implementation Creation

- Create skeleton implementation with proper TypeScript types
- Add comprehensive TODO comments for all implementation details
- Ensure function signatures match intended interfaces
- Apply documentation standards for JSDoc comments
- Structure code following general coding principles

### Step 3: Quality Structure Validation

- Verify TypeScript compliance of all function signatures
- Check adherence to coding standards for structure
- Validate proper TODO comment placement and clarity
- Ensure draft tests follow correct naming patterns
- Confirm documentation standards are applied

### Step 4: Reporting

**Output Format**:

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Files created: [count]
- Functions drafted: [count]
- TODO placeholders: [count]
- Standards compliance: [PASS/FAIL]

## Actions Taken
1. [Action with result]
2. [Action with result]

## Workflows Applied
- write-code (adapted for drafting): [Status]

## Draft Structure Created
- **Implementation**: [Description]
  **TODOs**: [List of TODO placeholders]

## Issues Found (if any)
- **Issue**: [Description]
  **Fix**: [Applied fix or suggestion]
```

## 📝 Examples

### Simple Usage

```bash
/draft-code "user authentication service with login and logout methods"
# Creates:
# - UserAuthService class with method signatures
# - TODO placeholders for implementation logic
# - Draft tests with describe.todo/it.todo patterns
# - TypeScript-compliant interfaces and types
```

### Complex Usage with Specific Flow

```bash
/draft-code "payment processing service with validation, external API integration, and error handling flow"
# Creates:
# - PaymentService class with complete method structure
# - Validation, API integration, and error handling method signatures  
# - Comprehensive TODO comments explaining each implementation step
# - Draft test suites covering all payment scenarios
# - TypeScript interfaces for payment data structures
```

### Component Draft Example

```bash
/draft-code "React component for user profile form with validation and submission"
# Creates:
# - UserProfileForm component with proper TypeScript props
# - Form state management structure with TODO implementations
# - Validation method signatures with TODO logic
# - Draft Storybook stories with story.todo patterns
# - Event handler method signatures with TODO implementations
```

### Error Case Handling

```bash
/draft-code "invalid-concept"
# Error: Instruction too vague for code structure creation
# Suggestion: Provide specific functionality and intended interfaces
# Alternative: Use '/draft-code "specific service/component with clear methods"'
```

### API Controller Draft

```bash
/draft-code "REST API controller for user management with CRUD operations and middleware integration"
# Creates:
# - UserController class with all CRUD method signatures
# - Middleware integration points with TODO implementations
# - Request/response type definitions
# - Error handling method signatures
# - Draft integration tests with describe.todo patterns
# - Comprehensive JSDoc documentation with parameter types
```
