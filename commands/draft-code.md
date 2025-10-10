---
allowed-tools: "Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task"

argument-hint: "<instruction> - Specify the area of code and flow to draft"

description: "Draft TypeScript-compliant code skeleton with TODO placeholders"
---

# Draft Code Skeleton

Create a code skeleton with TypeScript-compliant function signatures and logical structure, using TODO placeholders for implementation details. This command follows test-driven development principles by creating both draft tests and implementation structure without execution.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Execute or run any tests (uses describe.todo/it.todo patterns)
- Create production-ready implementation code
- Perform actual business logic implementation
- Execute quality gates or validation tests
- Create fully functional, executable code

**When to REJECT:**

- When full implementation is required immediately
- When tests need to actually run and pass
- When production-ready code is requested
- When the request is for executable, working code
- When comprehensive testing execution is needed

## 📊 Dynamic Context

- **[IMPORTANT]** At the start of the command, you MUST run the command to load all the context below

### System State

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- Working directory: !`pwd`
- Modified files: !`git diff --name-only`
- Staged files: !`git diff --cached --name-only`

### Project Context

- Workflows: !`find ~/.claude/constitutions/workflows "$(git rev-parse --show-toplevel)/constitutions/workflows" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`
- Standards: !`find ~/.claude/constitutions/standards "$(git rev-parse --show-toplevel)/constitutions/standards" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Follow Write-Code Workflow (Adapted for Drafting)

- Execute adapted version of @constitutions/workflows/coding/write-code.md
- Focus on structure creation rather than full implementation
- Create draft tests using describe.todo/it.todo patterns
- Generate TypeScript-compliant function signatures with TODO placeholders
- Ensure all code follows coding standards for structure and types

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

**Output Format:**

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
