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

### Step 0: Context Discovery & Integration

- **Review project context documents** (if available in project context):
  - Design/specification documents (DESIGN.md, REQUIREMENTS.md, API-SPECIFICATION.md, etc.)
  - Handover documents (CONTEXT.md, NOTES.md, PLAN.md)
  - Note: These are automatically discovered and available in the project context
- **Extract relevant context for drafting**:
  - **From design docs**: Architecture patterns, interface requirements, design decisions
  - **From CONTEXT.md**: Current state, file status (especially "need-draft" files), established patterns, gotchas
  - **From NOTES.md**: Proven approaches, what worked/didn't work, key insights, quick tips
  - **From PLAN.md**: Goals, success criteria, structural requirements, current phase
- **Prepare context for write-code workflow**:
  - Package all discovered context
  - Format as "Change Direction" parameter for workflow
  - Include specific structural requirements from command arguments
- **Note**: If no context files exist, proceed normally with command arguments only

### Step 1: Follow Write-Code Workflow (Step 1 Only)

- Execute workflow:write-code with resume parameters:
  - **Resume From Step**: 1 (Draft Code Skeleton & Test Structure)
  - **Change Direction**: Include context from Step 0 (design + handover) AND specific structural requirements from command arguments
  - **Skip Steps**: [2, 3, 4, 5] (only execute Steps 0-1)
- Focus on:
  - Step 0: Design Direction Discovery (discovers both design and handover docs)
  - Step 1: Draft Code Skeleton & Test Structure (uses discovered context)

**Resume Parameter Examples**:

**Example 1: Draft skeleton with specific patterns**

```
Resume From Step: 1
Change Direction: "Use factory pattern for object creation and builder pattern for configuration"
Skip Steps: [2, 3, 4, 5] (only draft, no implementation)
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
- Follow context from Step 0 (established patterns, design decisions, insights)

### Step 3: Quality Structure Validation

- Verify TypeScript compliance of all function signatures
- Check adherence to coding standards for structure
- Validate proper TODO comment placement and clarity
- Ensure draft tests follow correct naming patterns (describe.todo/it.todo)
- Confirm documentation standards are applied
- Verify skeleton is compilable without errors (tests marked as todo/pending, not passing/failing)

### Step 4: Reporting

**Output Format**:

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Context docs found: [DESIGN.md, CONTEXT.md, NOTES.md, PLAN.md - list which were found]
- Files created: [count]
- Functions drafted: [count]
- TODO placeholders: [count]
- Tests marked as todo/pending: [count]
- Standards compliance: [PASS/FAIL]
- Skeleton compilation: [PASS/FAIL]

## Context Discovery
- **Design docs**: [Found/Not found - list files if found]
- **Handover docs**: [Found/Not found - list files if found]
- **Key context used**: [List key patterns, decisions, or insights that guided drafting]

## Actions Taken
1. [Action with result]
2. [Action with result]

## Workflows Applied
- write-code (Steps 0-1 only, adapted for drafting): [Status]

## Draft Structure Created
- **Implementation**: [Description]
  **TODOs**: [List of TODO placeholders]
- **Tests**: [Description of test structure with describe.todo/it.todo patterns]

## Issues Found (if any)
- **Issue**: [Description]
  **Fix**: [Applied fix or suggestion]
```

## 📝 Examples

### Simple Usage

```bash
/draft-code "user authentication service with login and logout methods"
# Step 0: Discovers DESIGN.md (found), CONTEXT.md (found), NOTES.md (not found), PLAN.md (found)
# - Uses JWT pattern from DESIGN.md
# - Follows established error handling from CONTEXT.md
# - Aligns with security requirements from PLAN.md
# Creates:
# - UserAuthService class with method signatures following discovered patterns
# - TODO placeholders for implementation logic
# - Draft tests with describe.todo/it.todo patterns
# - TypeScript-compliant interfaces and types
# - Skeleton compiles without errors (tests marked as todo/pending)
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
