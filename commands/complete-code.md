---
allowed-tools: "Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task"

argument-hint: "<area> [--test-only] - Specify area to complete; --test-only completes only test code"

description: "Complete all TODO-marked code in specified area with test-first approach"
---

# Complete Code

Complete all unfinished code marked by TODO placeholders in the specified area. This command follows test-driven development by completing test code first, then implementing the corresponding functionality. Acts as the completion stage after /draft-code command.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Create new code structure or architecture from scratch
- Replace existing functional code
- Complete code without existing TODO markers or draft tests
- Work on code that hasn't been drafted with proper structure
- Skip test completion when implementing functionality

**When to REJECT:**

- When no TODO markers or describe.todo/it.todo patterns exist
- When requesting to create entirely new features without drafts
- When tests don't exist for the functionality to implement
- When the area specification is too broad or undefined
- When requesting production deployment or release activities

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

- Workflows: !`find "$(git rev-parse --show-toplevel)/constitutions/workflows" "$HOME/.claude/constitutions/workflows" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`
- Standards: !`find "$(git rev-parse --show-toplevel)/constitutions/standards" "$HOME/.claude/constitutions/standards" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: TODO Discovery and Analysis

- Use Grep tool to find all TODO markers in specified area
- Identify describe.todo, it.todo, and // TODO: patterns  
- Analyze existing draft structure and understand intended logic flow
- Validate that tests exist for all functionality to be implemented
- Create comprehensive task list for test completion and implementation

### Step 2: Follow Write-Code Workflow for Test Completion

- Execute @constitutions/workflows/coding/write-code.md for test implementation
- Convert all describe.todo and it.todo into functioning test suites
- Implement test logic following TDD principles and testing standards
- Ensure comprehensive test coverage for all TODO-marked functionality
- Validate tests run and properly validate intended behavior

### Step 3: Follow Write-Code Workflow for Implementation (Skip if --test-only)

- Execute @constitutions/workflows/coding/write-code.md for implementation
- Complete all // TODO: marked implementation following test requirements
- Implement business logic to satisfy all tests created in Step 2
- Apply refactoring and quality improvements per workflow standards
- Ensure all tests pass with proper implementation

### Step 4: Quality Validation and Testing

- Run complete test suite to verify all implementations work correctly
- Execute linting and type checking to ensure standards compliance
- Validate that no TODO markers remain in completed areas
- Confirm documentation standards are met for all completed code
- Perform comprehensive quality gates validation

### Step 5: Reporting

**Output Format:**

```
[✅/❌] Command: $ARGUMENTS

## Summary
- TODO items completed: [count]
- Tests implemented: [count]
- Functions completed: [count]
- Standards compliance: [PASS/FAIL]

## Actions Taken
1. [Action with result]
2. [Action with result]

## Workflows Applied
- write-code (test implementation): [Status]
- write-code (functionality implementation): [Status] (skipped if --test-only)

## Code Completion Results
- **Tests**: [describe.todo/it.todo converted to functional tests]
- **Implementation**: [TODO placeholders replaced with working code]
- **Quality**: [All quality gates and standards validation results]

## Issues Found (if any)
- **Issue**: [Description]
  **Fix**: [Applied fix or suggestion]
```

## 📝 Examples

### Simple Usage

```bash
/complete-code "user authentication service"
# Completes:
# - All describe.todo/it.todo tests for authentication
# - All // TODO: implementation in UserAuthService
# - Validates login, logout, and validation logic work correctly
```

### Test-Only Completion

```bash
/complete-code "payment processing" --test-only
# Completes only:
# - describe.todo/it.todo tests for payment processing
# - Test implementation without touching source code
# - Validates test structure and coverage
```

### Specific Component Area

```bash
/complete-code "user profile form validation"
# Completes:
# - Form validation test implementations
# - Input validation logic and error handling
# - State management TODO implementations
# - Event handler implementations
# - Component lifecycle TODO items
```

### Complex Service Implementation

```bash
/complete-code "api controller middleware integration"
# Completes:
# - Integration test implementations for middleware
# - Request/response handling TODO implementations
# - Error handling and logging TODO items
# - Authentication middleware integration logic
# - Complete CRUD operation implementations
```

### Error Case Handling

```bash
/complete-code "non-existent-area"
# Error: No TODO markers found in specified area
# Suggestion: Use 'grep -r "TODO\|describe\.todo\|it\.todo" .' to find available areas
# Alternative: Use '/draft-code' first to create structure with TODO markers
```

### Area with No Draft Structure

```bash
/complete-code "feature-without-drafts"
# Error: No draft structure or TODO markers found
# Suggestion: Run '/draft-code "feature description"' first to create structure
# Alternative: Specify area that contains existing TODO markers
```