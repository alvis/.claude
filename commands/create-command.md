---
allowed-tools: Bash, Edit, Read, Write, WebSearch, WebFetch, Grep, Glob, Task
argument-hint: <command-purpose>
description: Create a new slash command following best practices
# model: opus
---

# Create Custom Slash Command

Create a new slash command ($ARGUMENTS) following the latest best practices and template structure. Generates new slash commands from templates, configures appropriate tools and permissions, creates clean comment-free command files, and follows latest template structure from @templates/command.md. Ultrathink mode.

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

[[IMPORTANT] You must carefully remember all the context defined below]

### System State

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- Working directory: !`pwd`

### Project Context

- Workflows: !`find "$(git rev-parse --show-toplevel)/constitutions/workflows" "$HOME/.claude/constitutions/workflows" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`
- Standards: !`find "$(git rev-parse --show-toplevel)/constitutions/standards" "$HOME/.claude/constitutions/standards" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`

## 🔄 Workflow

### Phase 1: Planning

1. **Analyze Requirements**
   - Parse $ARGUMENTS to understand command purpose
   - If empty, ask: "What is the purpose of this command?"
   - Identify key operations and complexity level
   - Determine appropriate tools needed

2. **Generate Command Specification**
   - Create descriptive, action-oriented name
   - Format: lowercase, hyphen-separated (e.g., `fix-issue`, `analyze-code`)
   - For namespacing: suggest category (e.g., `dev/build`, `test/unit`)
   - Determine required tools based on purpose

3. **Identify Applicable Workflows & Standards**
   - Check `constitutions/workflows/` for relevant command patterns
   - Review `constitutions/standards/` for applicable standards
   - Identify if command fits standard patterns (build, test, analyze, etc.)

4. **Delegation Decision**
   - Determine if command will use specialized agents
   - Identify potential parallel execution opportunities
   - Plan tool restrictions needed for security

5. **Risk Assessment**
   - Check for name conflicts with existing commands
   - Identify potentially dangerous operations
   - Note any special permissions required

### Phase 2: Execution

1. **Workflow Compliance**
   - Load template from @templates/command.md
   - Apply identified command patterns from Phase 1
   - Ensure all template sections are included

2. **Primary Implementation**
   - Generate appropriate frontmatter configuration
   - Set allowed-tools based on command purpose
   - Add security restrictions (e.g., Bash(git:*) for git-only commands)
   - Create command structure with all required sections

3. **Standards Enforcement**
   - Follow template structure exactly
   - Ensure clean, comment-free output
   - Apply naming conventions
   - Include all required workflow phases

4. **Edge Case Handling**
   - Check if file already exists before writing
   - Handle empty or unclear arguments gracefully
   - Manage namespace directory creation if needed
   - Preserve any existing backups

### Phase 3: Verification

1. **Workflow-Based Verification**
   - Verify command follows template structure
   - Check all required sections are present
   - Validate frontmatter configuration

2. **Automated Testing**
   - Test command can be loaded successfully
   - Verify markdown syntax is valid
   - Check frontmatter parses correctly

3. **Quality Assurance**
   - Confirm NO comments in output
   - Validate tool restrictions are appropriate
   - Check examples are relevant and clear

4. **Side Effect Validation**
   - File saved to correct location (.claude/commands/)
   - No existing files overwritten without consent
   - Namespace directories created if needed

### Phase 4: Reporting

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
/create-command "fix bugs from issue tracker"
# Generates: fix-issue.md
# Tools: Bash, Edit, Read, Grep, Task
```

### Analysis Command

```bash
/create-command "analyze code quality and metrics"
# Generates: analyze-quality.md  
# Tools: Read, Grep, Glob, Task
# Pattern: Analysis workflow
```

### Build Command with Restrictions

```bash
/create-command "build and deploy application"
# Generates: build-deploy.md
# Tools: Bash(npm:*), Bash(docker:*), Read
# Security: Restricted bash commands
```

### Namespaced Testing Command

```bash
/create-command "testing utilities for unit tests"
# Generates: test/unit-utilities.md
# Creates: .claude/commands/test/ directory
# Tools: Bash(npm test:*), Read, Edit
```

### Error Case Handling

```bash
/create-command ""
# Error: Empty command purpose
# Prompt: "What is the purpose of this command?"
# Action: Wait for user input before proceeding
```

### With Workflow Override

```bash
/create-command "custom task" --pattern="analysis"
# Uses analysis pattern instead of auto-detected
# Configures read-only tools
# Generates analytical workflow structure
```
