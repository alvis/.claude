---
name: create-standard
description: Create a new technical standard directory with three-tier structure (meta.md, scan.md, write.md, rules/) from templates. Use when establishing new coding standards, documenting technical requirements, or creating compliance guidelines.
model: opus
allowed-tools: Bash, Read, Write, Glob, Task
argument-hint: <name> [--detail=...]
---

# Create Standard

Create a new technical standard directory in the [plugin]/constitution/standards directory following the three-tier structure (meta.md, scan.md, write.md, and rules/). $ARGUMENTS

## Purpose & Scope

**What this command does NOT do**:

- Modify existing standards (use update-standard)
- Create workflows (use create-workflow)
- Override existing directories without confirmation
- Create non-standard documentation

**When to REJECT**:

- Empty or unclear standard name
- Standard directory already exists
- Invalid name format
- Updating existing standards
- Creating non-standard files

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Planning

1. **Analyze Requirements**
   - Parse $ARGUMENTS to extract standard name and details
   - Determine appropriate category (code, frontend, backend, security, quality, project)
   - Identify related existing standards
   - Plan three-tier directory structure: meta.md, scan.md, write.md, and rules/

2. **Identify Applicable Workflows & Standards**
   - Check `/create-standard.md` for creation process
   - Review existing standards in target category for patterns
   - Note related standards to reference

3. **Risk Assessment**
   - Check for existing directory with the same name
   - Verify category directory exists
   - Ensure no duplicate standards

### Step 2: Execution

1. **Workflow Compliance**
   - Follow `/create-standard.md`
   - Load templates from template:standard-meta, template:standard-scan, and template:standard-write
   - Apply standard naming conventions

2. **Primary Implementation**
   - Generate standard title from arguments
   - Determine category placement
   - Create standard directory and rules/ subdirectory using `mkdir -p <name>/rules/`
   - Populate `<name>/meta.md` from template:standard-meta with metadata, principles, and overview
   - Populate `<name>/scan.md` from template:standard-scan with scanning/review rules
   - Populate `<name>/write.md` from template:standard-write with writing/implementation guidance
   - Include practical code examples across all three files
   - Add decision matrices and quick references

3. **Standards Enforcement**
   - Use lowercase, hyphen-separated naming for the directory
   - Follow each template structure exactly for its corresponding file
   - Include both good and bad examples
   - Add related standards references

4. **Edge Case Handling**
   - Check if directory already exists before creating
   - Create category directory if needed
   - Handle complex multi-word names properly
   - Preserve any existing backups

### Step 3: Verification

1. **Workflow-Based Verification**
   - Verify meta.md follows template:standard-meta structure
   - Verify scan.md follows template:standard-scan structure
   - Verify write.md follows template:standard-write structure
   - Check all required sections present in each file
   - Validate code examples are TypeScript
   - Verify rules/ subdirectory exists

2. **Automated Testing**
   - Verify markdown syntax is valid in all three files
   - Check all files saved to correct locations within the standard directory
   - Ensure proper formatting

3. **Quality Assurance**
   - Confirm examples include good and bad patterns
   - Validate related standards links
   - Check decision trees are complete
   - Ensure content is distributed correctly across the three tier files

4. **Side Effect Validation**
   - Directory and all three files saved to correct locations
   - No existing files or directories overwritten
   - Category directory created if needed

### Step 4: Reporting

**Output Format**:

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Standard created: [name]/
- Files: meta.md, scan.md, write.md, rules/
- Location: [plugin]/constitution/standards/[name]/
- Category: [category]

## Actions Taken
1. Created standard directory and rules/ subdirectory
2. Generated meta.md from template:standard-meta
3. Generated scan.md from template:standard-scan
4. Generated write.md from template:standard-write
5. Populated all files with relevant guidelines

## Content Structure
- Core Principles: [count]
- Main Topics: [list]
- Code Examples: [count]
- Anti-patterns: [count]

## Related Standards
- [Related standard 1]
- [Related standard 2]

## Next Steps
- Review generated standard files for completeness
- Add specific code examples if needed
- Add individual rule files to rules/ subdirectory
- Link from related documentation
```

## Examples

### Basic Standard Creation

```bash
/create-standard "error-handling"
# Generates: error-handling/meta.md, error-handling/scan.md, error-handling/write.md, error-handling/rules/
# Category: Automatically determined as 'code'
```

### Frontend Standard with Detail

```bash
/create-standard "component-testing" --detail="React component testing patterns"
# Generates: component-testing/meta.md, component-testing/scan.md, component-testing/write.md, component-testing/rules/
# Includes: React-specific testing examples
```

### Security Standard

```bash
/create-standard "api-authentication" --category=security
# Generates: api-authentication/meta.md, api-authentication/scan.md, api-authentication/write.md, api-authentication/rules/
# Category: Explicitly set to 'security'
```

### Backend Standard with Context

```bash
/create-standard "database-migrations" --detail="PostgreSQL migration patterns" --category=backend
# Generates: database-migrations/meta.md, database-migrations/scan.md, database-migrations/write.md, database-migrations/rules/
# Includes: PostgreSQL-specific examples
```

### Quality Standard

```bash
/create-standard "code-coverage" --category=quality
# Generates: code-coverage/meta.md, code-coverage/scan.md, code-coverage/write.md, code-coverage/rules/
# Includes: Coverage metrics and thresholds
```

### Error Case Handling

```bash
/create-standard ""
# Error: Empty standard name
# Prompt: "What is the name of the standard you want to create?"
# Action: Wait for user input before proceeding
```

### With Existing Directory

```bash
/create-standard "naming"
# Warning: naming/ directory already exists
# Prompt: "Standard 'naming' already exists. Create with different name?"
# Alternative: Use /update-standard to modify existing
```
