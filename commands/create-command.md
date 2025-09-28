---
allowed-tools: Bash, Edit, Read, Write, WebSearch, WebFetch, Grep, Glob, Task
argument-hint: <command-name> [--purpose=...] [--workflow1=...]
description: Create a new slash command following best practices
# model: opus
---

# Create Custom Slash Command

Create a new slash command using $ARGUMENTS (format: <command-name> [--purpose=...] [--workflow1=...]) following the latest best practices and template structure. Generates new slash commands from templates, configures appropriate tools and permissions, creates clean comment-free command files, and follows latest template structure from @templates/command.md. Ultrathink mode.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Modify existing commands (use update-command)
- Create non-command files
- Override existing files without confirmation

**When to REJECT:**

- Empty or unclear purpose
- Command already exists
- Invalid command name format
- Updating existing commands
- Creating regular markdown documentation
- Modifying template files

## 📊 Dynamic Context

- **[IMPORTANT]** You must carefully remember all the context defined below

### System State

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- Working directory: !`pwd`

### Project Context

- Workflows: !`find ~/.claude/constitutions/workflows "$(git rev-parse --show-toplevel)/constitutions/workflows" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`
- Standards: !`find ~/.claude/constitutions/standards "$(git rev-parse --show-toplevel)/constitutions/standards" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`

## 🔄 Workflows

### Step 1: Follow Create Command Workflow

- Execute @constitutions/workflows/project/create-command.md

### Step 2: Reporting

**Output Format:**

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Command created: [name].md
- Location: .claude/commands/[path]
- Tools configured: [list]

## Actions Taken
1. Generated command from template
2. Configured tools and permissions
3. Created file at specified location

## Configuration Applied
- Allowed tools: [tools]
- Model: [if specified]
- Security restrictions: [if any]

## Next Steps
- Test command: /[command-name] "test-argument"
- Customize workflow if needed
- Add to documentation if public command
```

## 📝 Examples

### Basic Command Creation

```bash
/create-command fix-issue --purpose="fix bugs from issue tracker"
# Generates: fix-issue.md
# Tools: Bash, Edit, Read, Grep, Task
```

### Analysis Command

```bash
/create-command analyze-quality --purpose="analyze code quality and metrics"
# Generates: analyze-quality.md  
# Tools: Read, Grep, Glob, Task
# Pattern: Analysis workflow
```

### Build Command with Restrictions

```bash
/create-command build-deploy --purpose="build and deploy application"
# Generates: build-deploy.md
# Tools: Bash(npm:*), Bash(docker:*), Read
# Security: Restricted bash commands
```

### Namespaced Testing Command

```bash
/create-command test/unit-utilities --purpose="testing utilities for unit tests"
# Generates: test/unit-utilities.md
# Creates: .claude/commands/test/ directory
# Tools: Bash(npm test:*), Read, Edit
```

### Error Case Handling

```bash
/create-command
# Error: Missing command name
# Prompt: "What command name would you like?"
# Action: Wait for user input before proceeding
```

### With Workflow Override

```bash
/create-command custom-task --purpose="perform custom analysis" --workflow="analysis"
# Uses analysis workflow pattern
# Configures read-only tools
# Generates analytical workflow structure
```
