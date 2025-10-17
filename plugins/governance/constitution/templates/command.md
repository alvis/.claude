---
# INSTRUCTION: In the tool list below, you must proactively update the tool list based on currently available tools. Carefully select those that would have chance to be used to fulfil to the task
allowed-tools: <list of comma separated list of tools the agent can use, e.g. "Bash(git:*), Bash(npm test), Bash(npm run:*), Bash(docker:*), Edit, MultiEdit, Read, Write, WebSearch, WebFetch, Grep, Glob, Task, ...">

argument-hint: <argument description>

# INSTRUCTION: Tell what this command does
description: <brief description shown in /help (max 80 characters)>
---

# [Command Title]

<!-- INSTRUCTION: Describe an action this command will execute. Use $ARGUMENTS as a placeholder for injecting context -->

[Description of the command in <= 3 sentences]

## 🎯 Purpose & Scope

<!-- INSTRUCTION: Based on the command, adjust the content -->

**What this command does NOT do**:

- [Explicit boundaries]
- [Out-of-scope operations]
- [Unsupported features]

**When to REJECT**:

- [Anti-patterns]
- [Better alternatives exist]
- [Risky conditions]

## 🔄 Workflow

ultrathink: you'd perform the following steps

<!-- INSTRUCTION: Add or remove the following basic workflow based on the command, think carefully what's the best workflow for the command -->

### Step 1: Follow [Workflow Name] Workflow

- Execute workflow:[workflow name]

### Step N: Follow [Workflow Name] Workflow

- Execute workflow:[workflow name]

### Step N+1: Reporting

**Output Format**:

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
