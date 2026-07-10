---
name: update-standard
description: Update standard(s) to latest template and apply specified changes. Use when bulk updating standards, aligning with template changes, or applying consistent modifications across the standards library.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, MultiEdit, TodoWrite
argument-hint: "[standard specifier] [--changes=...]"
---

# Update Standard

Update standard directories to align with the latest three-tier standard templates and apply specified changes using intelligent delegation to subagents — each standard is a directory containing `meta.md`, `scan.md`, `write.md`, and a `rules/` subdirectory, and the skill handles both single standard updates and bulk updates of all standards in parallel. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. Standards are read as authoritative single voices, so updates must be folded into the existing meta/scan/write tiers — not deposited as "Update YYYY-MM" trailers or parallel "newer rule" blocks beside the original wording they supersede.

## Purpose & Scope

**What this skill does NOT do**:

- Create new standards (use create-standard)
- Modify non-standard files
- Update templates themselves
- Override constitutional requirements

**When to REJECT**:

- Invalid standard directory paths
- Malformed change specifications
- Attempting to violate constitutional standards
- Template files (template:standard-meta, template:standard-scan, template:standard-write) are missing or corrupted

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Subagent Orchestration

Spawn parallel specialized subagents (max 3 standard directories per batch, max 8 parallel `Task` calls per dispatch) — each ultrathinks, reads three tier templates + standard tier files, and applies changes.

1. **Template Validation**
   - Verify all three tier templates exist and are readable: template:standard-meta, template:standard-scan, template:standard-write
   - Load template structures for reference
   - Identify mandatory sections that must be preserved in each tier

2. **Delegation**
   - Discover standard directories by finding directories containing `meta.md` under [plugin]/constitution/standards/
   - Create batches (max 3 standard directories per batch for subagent efficiency, since each directory = 3 tier files)
   - Create parallel specialized subagents (one per batch, max 8 parallel `Task` calls per dispatch) with:
     - Standard directory paths (each containing meta.md, scan.md, write.md)
     - All three tier template paths (template:standard-meta, template:standard-scan, template:standard-write)
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
   You're assigned to update standard directory: [standard name]

   **Standard Specifications**:
   - **Standard Directory**: [standard directory path] (contains meta.md, scan.md, write.md)
   - **Templates**:
     - template:standard-meta (for meta.md)
     - template:standard-scan (for scan.md)
     - template:standard-write (for write.md)
   - **Changes to Apply**: [change specifications from inputs]

   **Steps**

   1. **Read Current Standard**:
      - Read all three tier files: meta.md, scan.md, write.md
      - Identify existing guidelines, examples, and anti-patterns in each tier
      - Note any custom sections or unique content

   2. **Compare with Templates**:
      - Compare meta.md against template:standard-meta
      - Compare scan.md against template:standard-scan
      - Compare write.md against template:standard-write
      - Identify missing sections from each respective template
      - Identify sections that need structural updates in each tier
      - Map changes to the correct tier file based on what's changing

   3. **Apply Updates**:
      - Task 1: Align each tier file with its corresponding template structure
      - Task 2a, 2b, 2c...: Apply each change specification to the appropriate tier file
      - Task 3: Review standard integrity and consistency across all three tiers
      - Preserve all existing guidelines and examples
      - Add any missing required sections from each template

   4. **Clean & Finalize**:
      - Remove any outdated or deprecated content
      - Ensure consistent formatting throughout all three tier files
      - Verify all code examples are valid TypeScript

   **Report**
   **[IMPORTANT]** You MUST return the following execution report (<500 tokens):

   ```yaml
   status: success|failure|partial
   standard: '[standard-name]'
   summary: 'Brief description of changes applied'
   modifications:
     meta:
       - section: '[section name]'
         change: '[what was changed]'
     scan:
       - section: '[section name]'
         change: '[what was changed]'
     write:
       - section: '[section name]'
         change: '[what was changed]'
   tier_compliance:
     meta: true|false   # compliance with template:standard-meta
     scan: true|false   # compliance with template:standard-scan
     write: true|false  # compliance with template:standard-write
   content_preserved: true|false
   issues: ['issue1', 'issue2', ...]  # only if problems encountered
   ```

   <<<

4. **Progress Monitoring & Aggregation**
   - Track completion status of each delegated standard directory
   - Handle any subagent failures or escalations
   - Ensure constitutional compliance in all updates
   - Aggregate per-subagent YAML reports into the final Step 2 report

### Step 2: Reporting

**Output Format**:

```plaintext
[✅/❌] Command: $ARGUMENTS

## Summary
- Standards updated: [count]
- Changes applied: [change specifications]
- Template alignment: [COMPLETE/PARTIAL/FAILED]

## Actions Taken
1. [Standard directory] (meta.md, scan.md, write.md): [Status] - [Changes applied]
2. [Standard directory] (meta.md, scan.md, write.md): [Status] - [Changes applied]

## Subagent Results
- Total subagents deployed: [count]
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
/update-standard "typescript" --change1="Add OAuth 2.1 requirements" --change2="Update encryption standards"
# Updates typescript/ directory: meta.md, scan.md, write.md
# Compares meta.md vs template:standard-meta, scan.md vs template:standard-scan, write.md vs template:standard-write
# Agent applies changes to the appropriate tier file as separate tasks (2a, 2b)
# Ultrathink review for integrity and consistency across all three tiers
```

### Bulk Standard Updates

```bash
/update-standard --change1="Update TypeScript to 5.0 requirements"
# Discovers all standard directories (those containing meta.md)
# Spawns parallel subagents (max 3 standard directories per batch, max 8 parallel Task calls)
# Each subagent handles one standard directory (meta.md, scan.md, write.md)
# Consistent change applied across entire standard library
```

### Template-Only Alignment

```bash
/update-standard "typescript"
# Aligns typescript/ directory with latest three-tier templates
# Checks meta.md vs template:standard-meta, scan.md vs template:standard-scan, write.md vs template:standard-write
# No additional changes, just structure updates
# Preserves all existing content and requirements
```

### Multiple Complex Changes

```bash
/update-standard "components" --change1="Add React 18 concurrent features" --change2="Update testing requirements for RTL" --change3="Add accessibility compliance"
# Each change applied to the appropriate tier file (2a, 2b, 2c)
# Agent ensures changes don't conflict across meta.md, scan.md, write.md
# Ultrathink mode verifies comprehensive integration
```

### Error Case Handling

```bash
/update-standard "nonexistent-standard"
# Error: Standard directory not found (no meta.md in the directory)
# Suggestion: Use Glob to find directories with meta.md under [plugin]/constitution/standards/
# Alternative: Check if directory was moved or renamed
```

### Bulk Update with Specific Changes

```bash
/update-standard --change1="Update Node.js to version 20" --change2="Add ESM import requirements"
# Spawns agents for all standard directories
# Only applies changes where relevant (backend, code standards)
# Skips changes for standard directories where not applicable
```
