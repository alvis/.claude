# Step 2B: Subagent Mode (fallback)

This reference is consulted when Step 1 (Mode Selection) does NOT detect Agent Teams in the session context. Otherwise use Team Mode (`references/team-mode.md`).

1. **Template Validation**
   - Verify all three tier templates exist and are readable: template:standard-meta, template:standard-scan, template:standard-write
   - Load template structures for reference
   - Identify mandatory sections that must be preserved in each tier

2. **Delegation**
   - Discover standard directories by finding directories containing `meta.md` under [plugin]/constitution/standards/
   - Create batches (max 3 standard directories per batch for subagent efficiency, since each directory = 3 tier files)
   - Create parallel specialized subagents (one per batch) with:
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

4. **Progress Monitoring**
   - Track completion status of each delegated standard directory
   - Handle any subagent failures or escalations
   - Ensure constitutional compliance in all updates
