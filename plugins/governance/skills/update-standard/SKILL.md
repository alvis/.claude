---
name: update-standard
description: Update standard(s) to latest template and apply specified changes. Use when bulk updating standards, aligning with template changes, or applying consistent modifications across the standards library.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, MultiEdit, TodoWrite
argument-hint: [standard specifier] [--changes=...]
---

# Update Standard

Update standard files to align with the latest standard template and apply specified changes using intelligent delegation to subagents. Handles both single standard updates and bulk updates of all standards in parallel.

## Purpose & Scope

**What this skill does NOT do**:

- Create new standards (use create-standard)
- Modify non-standard files
- Update templates themselves
- Override constitutional requirements

**When to REJECT**:

- Invalid standard file paths
- Malformed change specifications
- Attempting to violate constitutional standards
- Template file is missing or corrupted

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Planning

1. **Analyze Requirements**
   - Parse $ARGUMENTS to extract standard name and change specifications
   - Standard: First argument (optional - if empty, update all standards)
   - --change[N]: Extract all change parameters (change1, change2, etc.)
   - Validate standard file exists if specified
   - Count total standards if updating all

2. **Load Template Reference**
   - Read template:standard for latest standard structure
   - Identify template sections and required elements
   - Note any template updates since last standard refresh

3. **Locate Standards**
   - Discover all relevant standard files using Glob
   - Filter by specifier if provided
   - Build list of standards to update

### Step 2: Execution with Parallel Subagents

1. **Template Validation**
   - Verify template:standard exists and is readable
   - Load template structure for reference
   - Identify mandatory sections that must be preserved

2. **Delegation**
   - Create parallel specialized subagents (one per standard file) with:
     - Standard file path
     - All change specifications
     - Detailed instructions
     - Request to ultrathink

3. **Subagent Task Specification**

   >>>
   **ultrathink: adopt the Standard Update Specialist mindset**

   - You're a **Standard Update Specialist** with deep expertise in technical documentation who follows these principles:
     - **Template-First Approach**: Always compare against template before modification
     - **Content Preservation**: Maintain existing guidelines and examples
     - **Structural Integrity**: Align with template structure while preserving content
     - **Professional Polish**: Deliver clean, consistent documentation

   <IMPORTANT>
     You've to perform the task yourself. You CANNOT further delegate the work to another subagent
   </IMPORTANT>

   **Assignment**
   You're assigned to update standard: [standard name]

   **Standard Specifications**:
   - **Standard File**: [standard file path]
   - **Template**: template:standard
   - **Changes to Apply**: [change specifications from inputs]

   **Steps**

   1. **Read Current Standard**:
      - Read the standard file completely
      - Identify existing guidelines, examples, and anti-patterns
      - Note any custom sections or unique content

   2. **Compare with Template**:
      - Read template:standard for current structure
      - Identify missing sections from template
      - Identify sections that need structural updates
      - Map changes to specific template sections

   3. **Apply Updates**:
      - Task 1: Align standard with template:standard structure
      - Task 2a, 2b, 2c...: Apply each change specification as subtask
      - Task 3: Review standard integrity and consistency throughout
      - Preserve all existing guidelines and examples
      - Add any missing required sections from template

   4. **Clean & Finalize**:
      - Remove any outdated or deprecated content
      - Ensure consistent formatting throughout
      - Verify all code examples are valid TypeScript

   **Report**
   **[IMPORTANT]** You MUST return the following execution report (<500 tokens):

   ```yaml
   status: success|failure|partial
   standard: '[standard-name]'
   summary: 'Brief description of changes applied'
   modifications:
     - section: '[section name]'
       change: '[what was changed]'
   template_compliance: true|false
   content_preserved: true|false
   issues: ['issue1', 'issue2', ...]  # only if problems encountered
   ```
   <<<

4. **Progress Monitoring**
   - Track completion status of each delegated standard
   - Handle any subagent failures or escalations
   - Ensure constitutional compliance in all updates

### Step 3: Verification

1. **Template Compliance Verification**
   - Verify each updated standard follows template:standard structure
   - Check all mandatory sections are present and properly formatted
   - Validate frontmatter and metadata consistency

2. **Change Application Verification**
   - Confirm all specified changes were applied correctly
   - Verify changes are reflected throughout the standard file
   - Check for any conflicting or contradictory specifications

3. **Constitutional Compliance**
   - Ensure updates don't violate constitutional standards
   - Verify standard still serves its intended purpose
   - Check integration with other standards

4. **Consistency Validation**
   - Run integrity checks on standard structure
   - Verify internal consistency and logical flow
   - Confirm no broken references or missing dependencies

### Step 4: Reporting

**Output Format**:

```plaintext
[✅/❌] Command: $ARGUMENTS

## Summary
- Standards updated: [count]
- Changes applied: [change specifications]
- Template alignment: [COMPLETE/PARTIAL/FAILED]

## Actions Taken
1. [Standard file]: [Status] - [Changes applied]
2. [Standard file]: [Status] - [Changes applied]

## Subagent Results
- Total agents deployed: [count]
- Successful updates: [count]
- Failed updates: [count] (if any)

## Template Alignment Applied
- Structure updates: [list]
- Section additions: [list]
- Format corrections: [list]

## Changes Applied
- --change1: [Status and details]
- --change2: [Status and details]

## Issues Found (if any)
- **Issue**: [Description]
  **Resolution**: [Applied fix or escalation]

## Next Steps (if applicable)
- Review updated standards for accuracy
- Test standard execution with sample scenarios
- Commit changes if satisfied with results
```

## Examples

### Single Standard Update

```bash
/update-standard "security.md" --change1="Add OAuth 2.1 requirements" --change2="Update encryption standards"
# Updates specific standard with template alignment and changes
# Agent applies changes as separate tasks (2a, 2b)
# Ultrathink review for integrity and consistency
```

### Bulk Standard Updates

```bash
/update-standard --change1="Update TypeScript to 5.0 requirements"
# Updates ALL standards in parallel
# Each agent handles one standard file
# Consistent change applied across entire standard library
```

### Template-Only Alignment

```bash
/update-standard "typescript.md"
# Aligns single standard with latest template
# No additional changes, just structure updates
# Preserves all existing content and requirements
```

### Multiple Complex Changes

```bash
/update-standard "react-components.md" --change1="Add React 18 concurrent features" --change2="Update testing requirements for RTL" --change3="Add accessibility compliance"
# Each change becomes separate task (2a, 2b, 2c)
# Agent ensures changes don't conflict
# Ultrathink mode verifies comprehensive integration
```

### Error Case Handling

```bash
/update-standard "nonexistent-standard.md"
# Error: Standard file not found
# Suggestion: Use 'find [plugin]/constitution/standards' to see available standards
# Alternative: Check if file was moved or renamed
```

### Bulk Update with Specific Changes

```bash
/update-standard --change1="Update Node.js to version 20" --change2="Add ESM import requirements"
# Spawns agents for all standard files
# Only applies changes where relevant (backend, code standards)
# Skips changes for standards where not applicable
```
