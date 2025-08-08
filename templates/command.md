---
# FRONTMATTER CONFIGURATION
# All available options for slash commands

# Available tools (comma-separated list)
# Restrict Bash commands for security (optional)
# Format: Bash(command:*) or Bash(exact-command)
# Examples: Bash(git:*), Bash(npm test), Bash(npm run:*), Bash(docker:*)
# Common tools: Bash, Edit, MultiEdit, Read, Write, WebSearch, WebFetch, Grep, Glob, Task
allowed-tools: Bash, Edit, MultiEdit, Read, Write, WebSearch, WebFetch, Grep, Glob, Task

# Hint shown when user types the command (for discoverability)
argument-hint: <argument description>

# Brief description shown in /help (max 80 characters)
description: One-line description of what this command does

# Model selection (optional, defaults to current model)
# Options: opus (complex reasoning), sonnet (standard), haiku (simple)
# model: opus

---

# Command Title

Describe an action this command will execute. Use $ARGUMENTS as a placeholder for injecting context.

## 🎯 Purpose & Scope

<!-- INSTRUCTION: Based on the command, adjust the content -->

**What this command does NOT do:**

- Explicit boundaries
- Out-of-scope operations
- Unsupported features

**When to REJECT:**

- Anti-patterns
- Better alternatives exist
- Risky conditions

## 📊 Dynamic Context

<!-- INSTRUCTION: Pick relevant context for purpose of achieving what the command intended to do, can be none -->

[[IMPORTANT] You must carefully remember all the context defined below]

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

<!-- INSTRUCTION: Add or remove the following basic workflow based on the command, think carefully what's the best workflow for the command -->

### Phase 1: Planning

1. **Analyze Requirements**
   - Break down the task into steps
   - Identify dependencies
   - Determine order of operations

2. **Identify Applicable Workflows & Standards**
   - Check `constitutions/workflows/` for relevant processes
   - Review `constitutions/standards/` for applicable standards
   - Note: MUST follow any matching workflows

3. **Delegation Decision**
   - Identify if specialized agents should handle subtasks
   - List tasks suitable for parallel execution
   - Plan handoff points between agents

4. **Risk Assessment**
   - Identify potential failure points
   - Plan rollback strategies
   - Note destructive operations

### Phase 2: Execution

1. **Workflow Compliance**
   - MUST follow workflows identified in Phase 1
   - If no workflow exists, follow project conventions
   - Reference specific workflow files when applicable

2. **Primary Implementation**
   - Execute main task following standards
   - Use parallel processing for independent tasks
   - Delegate to specialized agents when beneficial

3. **Standards Enforcement**
   - Apply standards from `constitutions/standards/`
   - Follow coding conventions for language/framework
   - Maintain consistency with existing codebase

4. **Edge Case Handling**
   - Check special conditions
   - Apply fallback strategies
   - Maintain data integrity

### Phase 3: Verification

1. **Workflow-Based Verification**
   - Run `constitutions/workflows/quality/review-code.md` if code modified
   - Follow `constitutions/workflows/quality/verify-*` patterns if applicable
   - Use validation checklists from relevant workflows

2. **Automated Testing**
   - Run test suites: `npm test` or project-specific commands
   - Verify expected outputs match requirements
   - Check for regressions in existing functionality

3. **Quality Assurance**
   - Run type checking: `npm run typecheck` if TypeScript
   - Execute linters: `npm run lint` or equivalent
   - Validate against applicable standards

4. **Side Effect Validation**
   - Confirm no unintended file changes
   - Verify system state consistency
   - Check cleanup of temporary resources

### Phase 4: Reporting

**Output Format:**

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Files modified: [count]
- Tests passed: [count/total]
- Standards compliance: [PASS/FAIL]

## Actions Taken
1. [Action with result]
2. [Action with result]

## Workflows Applied
- [Workflow name]: [Status]

## Issues Found (if any)
- **Issue**: [Description]
  **Fix**: [Applied fix or suggestion]

## Next Steps (if applicable)
- [Required manual action]
- [Recommended follow-up]
```

## 📝 Examples

### Simple Usage

```bash
/command-name "single-argument"
# Executes basic task with minimal configuration
```

### Complex Usage with Options

```bash
/command-name "primary-target" --scope="specific-area" --verify
# Executes with additional constraints and verification
```

### Delegation Example

```bash
/command-name "large-task"
# Automatically delegates to:
#   - Agent A: Handles component 1
#   - Agent B: Handles component 2 (parallel)
#   - Agent C: Verification (after A & B complete)
```

### Error Case Handling

```bash
/command-name "invalid-target"
# Error: Target not found
# Suggestion: Check available targets with 'ls targets/'
# Alternative: Use '/command-name --list' to see valid options
```

### With Workflow Override

```bash
/command-name "task" --workflow="custom-workflow.md"
# Uses specified workflow instead of auto-detected one
```
