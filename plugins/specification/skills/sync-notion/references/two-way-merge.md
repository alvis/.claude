# Two-Way Merge — Step 2 (Conditional)

Load this reference **only when `sync_mode = 'two-way-merge'`**. For `sync_mode = 'local-to-notion'` or `sync_mode = 'notion-to-local'`, skip Step 2 entirely and proceed directly to Step 3 in `SKILL.md`.

This file contains the full body of **Step 2: Compare Content** — the conflict-detection and user-driven resolution step that produces a `resolved_content_map` consumed by Step 3.

## Step 2: Compare Content (Conditional)

**Step Configuration**:

- **Purpose**: Compare local and Notion content section-by-section and resolve conflicts with user confirmation
- **Input**: Receives from Step 1: validated file-page pairs array with both local and Notion content
- **Output**: Produces for Step 3: resolved_content_map with merged content for each pair, conflict_report
- **Sub-workflow**: None
- **Parallel Execution**: Yes - one subagent per file-page pair (conflicts resolved interactively)

**CONDITIONAL**: This step only executes if sync_mode = 'two-way-merge'. If sync_mode is 'local-to-notion' or 'notion-to-local', skip directly to Step 3.

### Phase 1: Planning (You)

**What You Do**:

1. **Check sync_mode**:
   - If sync_mode = 'two-way-merge': Continue with comparison
   - If sync_mode = 'local-to-notion' or 'notion-to-local': Skip to Step 3 immediately
2. **Receive validated pairs** from Step 1 output
3. **Filter pairs** that have both local and Notion content (skip pairs marked 'CREATE_NEW')
4. **Use TodoWrite** to create comparison task list with one todo per pair requiring comparison (status 'pending')
5. **Prepare comparison assignments** for parallel execution (one subagent per pair)
6. **Queue all pairs** for parallel comparison and conflict resolution

**OUTPUT from Planning**: Comparison task assignments queued for pairs with existing Notion pages

### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, you spin up comparison subagents to resolve conflicts in parallel, launching **N subagents** (one per file-page pair that needs comparison).

- **[IMPORTANT]** Each subagent handles one pair independently and interacts with user for conflict resolution
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each pair's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following comparison and conflict resolution:

    >>>
    **ultrathink: adopt the Content Comparison Specialist mindset**

    - You're a **Content Comparison Specialist** with deep expertise in diff analysis who follows these technical principles:
      - **Granular Comparison**: Compare content at section-level, not just file-level
      - **Clear Presentation**: Show both versions side-by-side with highlighted differences
      - **User Empowerment**: Provide clear options and respect user decisions
      - **Merge Intelligence**: When user selects "Keep Both", intelligently combine content

    **Assignment**
    You're assigned to compare and resolve conflicts for a single file-page pair:

    - **File Path**: [file_path]
    - **File Content**: [file_content from Step 1]
    - **Notion URL**: [notion_url from Step 1]
    - **Notion Content**: [notion_content from Step 1]

    **Steps**

    1. **Parse Content into Sections**:
       - Split local markdown into sections (by headers: #, ##, ###)
       - Split Notion content into sections (by headers)
       - Create section-level mapping for comparison
       - Handle frontmatter separately (not compared, preserved from local)

    2. **Identify Differences**:
       - Compare each section pair between local and Notion
       - Classify differences as:
         * **Addition**: Section exists in local but not in Notion
         * **Removal**: Section exists in Notion but not in local
         * **Modification**: Section exists in both but content differs
         * **Identical**: Section is the same in both (skip)
       - Record all differences with section identifiers

    3. **Resolve Each Conflict with User** (for each difference found):
       - Display the difference clearly:
         ```
         CONFLICT in [file_path] - Section: [section_name]

         LOCAL VERSION:
         [local section content]

         NOTION VERSION:
         [notion section content]

         DIFFERENCE: [specific diff description]
         ```
       - Use AskUserQuestion tool with options:
         * header: "Sync Conflict"
         * question: "How should this conflict be resolved for section '[section_name]'?"
         * options:
           - label: "Keep Local", description: "Use the local version, overwrite Notion"
           - label: "Keep Remote", description: "Use the Notion version, overwrite local"
           - label: "Keep Both", description: "Merge both versions intelligently"
           - label: "Skip", description: "Mark for manual resolution later"
         * multiSelect: false
       - Record user's decision for this conflict

    4. **Apply Decisions to Create Merged Content**:
       - For each conflict resolved:
         * Keep Local: Use local section content
         * Keep Remote: Use Notion section content
         * Keep Both: Combine both sections with clear markers:
           ```
           [section from local]

           --- Merged from Notion ---
           [section from Notion]
           ```
         * Skip: Add TODO marker in both versions:
           ```
           <!-- TODO: Resolve merge conflict manually - Section [name] -->
           ```
       - Assemble final merged content with resolved sections
       - Preserve original order and structure

    5. **Generate Conflict Report**:
       - Count total conflicts found
       - Count decisions by type (keep_local, keep_remote, keep_both, skipped)
       - List all skipped conflicts for user awareness

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of comparison and resolution'
    modifications: []  # no file modifications yet
    outputs:
      file_path: '[path]'
      notion_url: '[url]'
      conflicts_found: [number]
      conflicts_by_type:
        additions: [count]
        removals: [count]
        modifications: [count]
      decisions:
        keep_local: [count]
        keep_remote: [count]
        keep_both: [count]
        skipped: [count]
      resolved_content: '[complete merged content]'
      skipped_conflicts: ['section1: description', 'section2: description', ...]
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

### Phase 3: Review (Subagents)

**SKIPPED** - User already reviewed and confirmed each conflict resolution interactively.

### Phase 4: Decision (You)

**What You Do**:

1. **Collect all comparison reports** from parallel subagents
2. **Parse resolution status** from each report (success/failure/partial)
3. **Aggregate conflict statistics**:
   - Total conflicts across all pairs
   - Total decisions by type (keep_local, keep_remote, keep_both, skipped)
   - All skipped conflicts requiring manual resolution
4. **Apply decision criteria**:
   - All comparisons successful: PROCEED to Step 3 with resolved content
   - Some comparisons failed: ABORT with error details
5. **Select next action**:
   - **PROCEED**: All conflicts resolved or skipped → Move to Step 3 with resolved_content_map
   - **ABORT**: Comparison failures → Report errors and stop workflow
6. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark all comparison todos as 'completed'
   - If ABORT: Mark failed todos as 'failed' with abort reason
7. **Prepare transition**:
   - If PROCEED: Package resolved_content_map and conflict_report for Step 3
   - If ABORT: Generate error report with comparison failure details
