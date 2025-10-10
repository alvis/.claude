---
allowed-tools: Bash, Read, Write, Glob, Task
argument-hint: <name> [--detail=...]
description: Create a new technical standard from template
---

# Create Standard

Create a new technical standard document in the constitutions/standards directory following the template structure. $ARGUMENTS

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Modify existing standards (use update-standard)
- Create workflows (use create-workflow)
- Override existing files without confirmation
- Create non-standard documentation

**When to REJECT:**

- Empty or unclear standard name
- Standard already exists
- Invalid name format
- Updating existing standards
- Creating non-standard files

## 📊 Dynamic Context

- **[IMPORTANT]** You must carefully remember all the context defined below

### System State

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- Working directory: !`pwd`

### Project Context

- Workflows: !`find "$(git rev-parse --show-toplevel)/constitutions/workflows" "$HOME/.claude/constitutions/workflows" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`
- Standards: !`find "$(git rev-parse --show-toplevel)/constitutions/standards" "$HOME/.claude/constitutions/standards" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No standards found"`

## 🔄 Workflow

### Phase 1: Planning

1. **Analyze Requirements**
   - Parse $ARGUMENTS to extract standard name and details
   - Determine appropriate category (code, frontend, backend, security, quality, project)
   - Identify related existing standards
   - Plan standard structure and content

2. **Identify Applicable Workflows & Standards**
   - Check `constitutions/workflows/project/create-standard.md` for creation process
   - Review existing standards in target category for patterns
   - Note related standards to reference

3. **Delegation Decision**
   - Use sam-taylor-documentation agent for comprehensive documentation
   - Consider specialized agents based on category:
     - Frontend: lily-wong-ui-implementation
     - Backend: james-mitchell-service-implementation
     - Security: nina-petrov-security-champion
     - Quality: marcus-williams-code-quality

4. **Risk Assessment**
   - Check for name conflicts with existing standards
   - Verify category directory exists
   - Ensure no duplicate standards

### Phase 2: Execution

1. **Workflow Compliance**
   - Follow `constitutions/workflows/project/create-standard.md`
   - Load template from templates/standard.md
   - Apply standard naming conventions

2. **Primary Implementation**
   - Generate standard title from arguments
   - Determine category placement
   - Populate template sections with relevant content
   - Include practical code examples
   - Add decision matrices and quick references

3. **Standards Enforcement**
   - Use lowercase, hyphen-separated naming
   - Follow template structure exactly
   - Include both good and bad examples
   - Add related standards references

4. **Edge Case Handling**
   - Check if file already exists before writing
   - Create category directory if needed
   - Handle complex multi-word names properly
   - Preserve any existing backups

### Phase 3: Verification

1. **Workflow-Based Verification**
   - Verify follows template structure
   - Check all required sections present
   - Validate code examples are TypeScript

2. **Automated Testing**
   - Verify markdown syntax is valid
   - Check file saved to correct location
   - Ensure proper formatting

3. **Quality Assurance**
   - Confirm examples include ✅ and ❌ patterns
   - Validate related standards links
   - Check decision trees are complete

4. **Side Effect Validation**
   - File saved to constitutions/standards/[category]/
   - No existing files overwritten
   - Category directory created if needed

### Phase 4: Reporting

**Output Format:**

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Standard created: [name].md
- Location: constitutions/standards/[category]/[name].md
- Category: [category]

## Actions Taken
1. Generated standard from template
2. Populated with relevant guidelines
3. Created file at specified location

## Content Structure
- Core Principles: [count]
- Main Topics: [list]
- Code Examples: [count]
- Anti-patterns: [count]

## Related Standards
- [Related standard 1]
- [Related standard 2]

## Next Steps
- Review generated standard for completeness
- Add specific code examples if needed
- Link from related documentation
```

## 📝 Examples

### Basic Standard Creation

```bash
/create-standard "error-handling"
# Generates: constitutions/standards/code/error-handling.md
# Category: Automatically determined as 'code'
```

### Frontend Standard with Detail

```bash
/create-standard "component-testing" --detail="React component testing patterns"
# Generates: constitutions/standards/frontend/component-testing.md
# Includes: React-specific testing examples
```

### Security Standard

```bash
/create-standard "api-authentication" --category=security
# Generates: constitutions/standards/security/api-authentication.md
# Category: Explicitly set to 'security'
```

### Backend Standard with Context

```bash
/create-standard "database-migrations" --detail="PostgreSQL migration patterns" --category=backend
# Generates: constitutions/standards/backend/database-migrations.md
# Includes: PostgreSQL-specific examples
```

### Quality Standard

```bash
/create-standard "code-coverage" --category=quality
# Generates: constitutions/standards/quality/code-coverage.md
# Includes: Coverage metrics and thresholds
```

### Error Case Handling

```bash
/create-standard ""
# Error: Empty standard name
# Prompt: "What is the name of the standard you want to create?"
# Action: Wait for user input before proceeding
```

### With Existing File

```bash
/create-standard "naming"
# Warning: constitutions/standards/code/naming.md already exists
# Prompt: "Standard 'naming' already exists. Create with different name?"
# Alternative: Use /update-standard to modify existing
```