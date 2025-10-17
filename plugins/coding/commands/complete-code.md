---
allowed-tools: "Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task"

argument-hint: "<area> [--test-only] - Specify area to complete; --test-only completes only test code"

description: "Complete all TODO-marked code in specified area with test-first approach"
---

# Complete Code

Complete all unfinished code marked by TODO placeholders in the specified area. This command follows test-driven development by completing test code first, then implementing the corresponding functionality. Acts as the completion stage after /draft-code command.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Create new code structure or architecture from scratch
- Replace existing functional code
- Complete code without existing TODO markers or draft tests
- Work on code that hasn't been drafted with proper structure
- Skip test completion when implementing functionality

**When to REJECT**:

- When no TODO markers or describe.todo/it.todo patterns exist
- When requesting to create entirely new features without drafts
- When tests don't exist for the functionality to implement
- When the area specification is too broad or undefined
- When requesting production deployment or release activities

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 0: Context Discovery & Integration

- **Review project context documents** (if available in project context):
  - Design/specification documents (DESIGN.md, REQUIREMENTS.md, API-SPECIFICATION.md, etc.)
  - Handover documents (CONTEXT.md, NOTES.md, PLAN.md)
  - Note: These are automatically discovered and available in the project context
- **Extract completion-specific context**:
  - **From design docs**: Architecture patterns, implementation requirements, design constraints
  - **From CONTEXT.md**:
    - File status (especially "need-completion" and "need-testing" files)
    - Which TODOs are intentional vs need completion
    - Known issues and workarounds from gotchas section
    - Established patterns to follow
  - **From NOTES.md**:
    - Previous exploration results (what worked/didn't work)
    - Problems already solved
    - Key insights and quick tips for implementation
  - **From PLAN.md**:
    - Goals to guide prioritization
    - Success criteria for completion
    - Current phase and priorities
- **Prepare context for TODO analysis**:
  - Package all discovered context
  - Identify files marked for completion in handover
  - Note which TODOs align with current goals
  - Format context for write-code workflow
- **Note**: If no context files exist, proceed with normal TODO discovery

### Step 1: TODO Discovery and Context Cross-Reference

- Use Grep tool to find all TODO markers in specified area
- Identify describe.todo, it.todo, and // TODO: patterns
- Analyze existing draft structure and understand intended logic flow
- **Cross-reference with context from Step 0**:
  - Match discovered TODOs with file status from CONTEXT.md
  - Prioritize TODOs marked as "need-completion" in handover
  - Identify which TODOs align with current goals from PLAN.md
  - Note any TODOs mentioned in gotchas or research insights
- Validate that tests exist for all functionality to be implemented
- Create comprehensive task list for test completion and implementation prioritized by context

### Step 2: Follow Write-Code Workflow for Test Completion

- Execute workflow:write-code for test implementation with context from Step 0
- Convert all describe.todo and it.todo into functioning test suites
- Implement test logic following TDD principles and testing standards
- **Apply context from Step 0**:
  - Follow established testing patterns from CONTEXT.md
  - Use proven approaches from NOTES.md
  - Avoid known issues documented in gotchas
- Ensure comprehensive test coverage for all TODO-marked functionality
- Validate tests run and properly validate intended behavior

### Step 3: Follow Write-Code Workflow for Implementation (Skip if --test-only)

- Execute workflow:write-code for implementation with context from Step 0
- Complete all // TODO: marked implementation following test requirements
- Implement business logic to satisfy all tests created in Step 2
- **Apply context from Step 0**:
  - Follow design patterns from DESIGN.md
  - Use established patterns from CONTEXT.md
  - Apply insights and quick tips from NOTES.md
  - Avoid workarounds documented in gotchas
- Apply refactoring and quality improvements per workflow standards
- Ensure all tests pass with proper implementation

### Step 4: Quality Validation and Testing

- Run complete test suite to verify all implementations work correctly
- Execute linting and type checking to ensure standards compliance
- Validate that no TODO markers remain in completed areas
- Confirm documentation standards are met for all completed code
- Perform comprehensive quality gates validation

### Step 5: Reporting

**Output Format**:

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Context docs found: [DESIGN.md, CONTEXT.md, NOTES.md, PLAN.md - list which were found]
- TODO items completed: [count]
- Tests implemented: [count]
- Functions completed: [count]
- Standards compliance: [PASS/FAIL]

## Context Discovery
- **Design docs**: [Found/Not found - list files if found]
- **Handover docs**: [Found/Not found - list files if found]
- **Key context used**: [List key patterns, insights, or gotchas that guided completion]
- **Files prioritized from handover**: [List files marked as "need-completion" in CONTEXT.md]

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
# Step 0: Discovers CONTEXT.md (found - shows UserAuthService in "need-completion"),
#         NOTES.md (found - notes JWT validation approach that worked),
#         PLAN.md (found - security is priority)
# - Prioritizes UserAuthService based on CONTEXT.md file status
# - Uses proven JWT validation from NOTES.md
# - Avoids password hashing gotcha documented in CONTEXT.md
# Completes:
# - All describe.todo/it.todo tests for authentication
# - All // TODO: implementation in UserAuthService following discovered patterns
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
