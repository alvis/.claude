# Sync Notion Documents

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Perform bidirectional synchronization between local markdown documentation files and Notion pages with intelligent conflict resolution and integrity verification.

**When to use**:

- When local markdown documentation needs to be synced to Notion workspace
- When Notion pages need to be pulled down to local markdown files
- When resolving conflicts between local and remote documentation versions
- After significant documentation updates that need to be reflected in both locations

**Prerequisites**:

- Access to Notion workspace with appropriate permissions
- Notion MCP server configured and available
- Local markdown files with valid frontmatter (if updating existing synced files)
- Understanding of sync modes and their implications

### Your Role

You are a **Synchronization Orchestrator** who coordinates the documentation sync process like a data pipeline manager overseeing bidirectional data flows. You never execute sync operations directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Assign sync operations to specialist subagents, one file-page pair at a time for precise control
- **Parallel Coordination**: Launch multiple sync operations simultaneously for efficiency while maintaining clear tracking
- **Quality Oversight**: Verify sync integrity through independent verification subagents
- **Decision Authority**: Make critical decisions on conflict resolution, verification failures, and manual intervention needs
- **Zero Tolerance for Data Loss**: Stop immediately on integrity issues and escalate to human for manual resolution

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Sync Mode**: The synchronization direction and strategy
  - `local-to-notion`: Overwrite Notion pages with local content (no conflict detection)
  - `notion-to-local`: Overwrite local files with Notion content (no conflict detection)
  - `two-way-merge`: Compare content and ask user to resolve conflicts
- **File Paths**: Array of absolute paths to local markdown files to be synced
- **Notion URLs**: Array of Notion page URLs corresponding to the files (extracted from frontmatter, searched, or provided manually)

#### Optional Inputs

- **Database ID**: Notion database ID for creating new pages when URLs are not found (e.g., `292b2572-f788-803f-84f5-000b9b51b8b6`)
- **Fuzzy Search**: Enable fuzzy matching for finding existing pages when URLs missing (default: true)
- **Skip Verification**: Skip post-sync integrity verification (default: false, not recommended)
- **Parent Page URL**: Parent Notion page URL for creating new pages outside of database context

#### Expected Outputs

- **Sync Status**: Overall success/partial/failure status for the sync operation
- **Synced Files**: Array of local file paths that were successfully synced
- **Synced Pages**: Array of Notion page URLs that were successfully synced
- **Sync Pairs**: Detailed mapping of file-to-page pairs with sync direction and individual status
- **Conflict Report**: Number and details of conflicts resolved (two-way-merge only)
- **Verification Report**: Post-sync integrity check results for each synced pair
- **Frontmatter Updated**: Boolean indicating whether tracking metadata was updated in local files
- **New Pages Created**: Array of Notion URLs for newly created pages

#### Data Flow Summary

The workflow takes local file paths and Notion URLs along with a sync mode, validates that all resources are accessible, optionally compares content for conflicts (two-way-merge mode), executes the sync operations in the specified direction, verifies sync integrity to catch any data loss or corruption, and updates local frontmatter with sync metadata for future tracking.

### Visual Overview

#### Main Workflow Flow

```plaintext
   YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Load & Validate] ──→ (Parallel: N subagents, 1 file-page pair each)
   |                           ├─ Subagent 1: Validate file1 + fetch notion1  ─┐
   |                           ├─ Subagent 2: Validate file2 + fetch notion2  ─┤
   |                           └─ Subagent N: Validate fileN + fetch notionN  ─┴→ [Decision: All valid?]
   v
[Step 2: Compare Content] ───→ (Conditional: only if sync_mode = two-way-merge)
   |                           ├─ Subagent 1: Compare file1 vs notion1, resolve conflicts  ─┐
   |                           ├─ Subagent 2: Compare file2 vs notion2, resolve conflicts  ─┤
   |                           └─ Subagent N: Compare fileN vs notionN, resolve conflicts  ─┴→ [Decision: Conflicts resolved?]
   v
[Step 3: Execute Sync] ──────→ (Parallel: N sync subagents, 1 pair each)
   |                           ├─ Subagent 1: Sync file1 ↔ notion1 per mode  ─┐
   |                           ├─ Subagent 2: Sync file2 ↔ notion2 per mode  ─┤
   |                           └─ Subagent N: Sync fileN ↔ notionN per mode  ─┴→ [Decision: All synced?]
   v
[Step 4: Verify Integrity] ──→ (Parallel: N verification subagents, 1 pair each)
   |                           ├─ Subagent 1: Verify file1 = notion1  ─┐
   |                           ├─ Subagent 2: Verify file2 = notion2  ─┤
   |                           └─ Subagent N: Verify fileN = notionN  ─┴→ [Decision: All verified?]
   |                                                                         ├─ PASS → Continue
   |                                                                         └─ FAIL → STOP & Print Content → Ask Human
   v
[Step 5: Update Metadata] ───→ (Parallel: N metadata subagents, 1 file each)
   |                           ├─ Subagent 1: Update file1 frontmatter  ─┐
   |                           ├─ Subagent 2: Update file2 frontmatter  ─┤
   |                           └─ Subagent N: Update fileN frontmatter  ─┴→ [Decision: Complete?]
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute tasks (1 file-page pair per subagent)
• ARROWS (───→): You assign work to subagents
• DECISIONS: You decide based on subagent reports
• PARALLEL: Multiple subagents run simultaneously (no batching)
═══════════════════════════════════════════════════════════════════

Note:
• You: Validate inputs, assign tasks (1-to-1 mapping), make decisions
• Execution Subagents: Handle 1 file-page pair, report back (<1k tokens)
• Verification Subagents: Check 1 pair integrity (<500 tokens)
• On Verification Failure: STOP immediately, print content, ask human
• Workflow is LINEAR: Step 1 → 2 (conditional) → 3 → 4 → 5
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Load and Validate Resources
2. Compare Content (Conditional - only for two-way-merge)
3. Execute Sync Operations
4. Verify Sync Integrity
5. Update Tracking Metadata

### Step 1: Load and Validate Resources

**Step Configuration**:

- **Purpose**: Validate all input files and Notion pages are accessible and prepare file-page pair mappings
- **Input**: sync_mode, file_paths, notion_urls (optional: database_id, fuzzy_search, parent_page_url)
- **Output**: Validated file-page pairs array with content loaded and ready for sync
- **Sub-workflow**: None
- **Parallel Execution**: Yes - one subagent per file-page pair

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from workflow invocation (sync_mode, file_paths, notion_urls, optional parameters)
2. **Extract Notion URLs from frontmatter** if not provided:
   - Read each file's frontmatter to extract `notion_url` field
   - If notion_url missing and database_id provided: prepare for fuzzy search
   - If notion_url missing and no database_id: mark as "create new page"
3. **Create file-page pair mappings**:
   - Pair each file_path with its corresponding notion_url (or null if creating new)
   - Generate unique identifiers for each pair (e.g., pair_1, pair_2, ...)
4. **Use TodoWrite** to create task list with one todo per file-page pair (status 'pending')
5. **Prepare validation assignments** for parallel execution (one subagent per pair)
6. **Queue all pairs** for parallel validation by subagents

**OUTPUT from Planning**: File-page pair assignments with validation tasks queued

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, you spin up validation subagents to validate file-page pairs in parallel, launching **N subagents** (one per file-page pair).

- **[IMPORTANT]** When there are any validation issues reported, you must stop and address the issue before proceeding
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each pair's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following validation:

    >>>
    **ultrathink: adopt the Resource Validation Specialist mindset**

    - You're a **Resource Validation Specialist** with deep expertise in data integrity who follows these technical principles:
      - **Accessibility First**: Verify all resources exist and are accessible before proceeding
      - **Content Integrity**: Ensure file content is parseable and Notion pages are fetchable
      - **Smart Discovery**: Use fuzzy matching to find existing pages when URLs are missing
      - **Clear Reporting**: Provide detailed status on what was validated and what was found

    **Assignment**
    You're assigned to validate a single file-page pair:

    - **File Path**: [file_path]
    - **Notion URL**: [notion_url or 'SEARCH REQUIRED' or 'CREATE NEW']
    - **Database ID**: [database_id if provided]
    - **Fuzzy Search**: [true/false]
    - **Parent Page URL**: [parent_page_url if provided]

    **Steps**

    1. **Validate Local File**:
       - Use Read tool to load the file at [file_path]
       - Parse YAML frontmatter if exists (look for notion_url, last_synced_at, etc.)
       - Extract file content (everything after frontmatter)
       - Verify file is readable and content is valid markdown
       - Record file size and section count for integrity tracking

    2. **Resolve Notion URL** (if not provided or marked SEARCH REQUIRED):
       - If database_id provided:
         * Use notion-search to find existing page
         * Apply fuzzy matching: strip special chars (@, /), lowercase, partial match
         * Search by file name or title from frontmatter
       - If found: Record the discovered notion_url
       - If not found: Mark as 'CREATE_NEW' for Step 3

    3. **Validate Notion Page** (if notion_url exists):
       - Use notion-fetch to retrieve page content
       - Verify page is accessible and fetchable
       - Extract page content for comparison
       - Record page last_edited_time from Notion metadata
       - Verify page is not archived or deleted

    4. **Prepare Pair Data**:
       - Package all validated data for downstream steps:
         * file_path: [path]
         * file_content: [content without frontmatter]
         * file_frontmatter: [parsed YAML object]
         * notion_url: [url or 'CREATE_NEW']
         * notion_content: [content if exists]
         * notion_last_edited: [timestamp if exists]
         * validation_status: valid|invalid
         * validation_notes: [any issues found]

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of validation results'
    modifications: []  # no modifications in validation phase
    outputs:
      file_path: '[path]'
      file_accessible: true|false
      file_content_length: [number]
      file_frontmatter: {notion_url: '...', last_synced_at: '...'}
      notion_url: '[url or CREATE_NEW or SEARCH_FAILED]'
      notion_accessible: true|false|N/A
      notion_content_length: [number or 0]
      notion_last_edited: '[ISO timestamp or null]'
      pair_status: 'valid|invalid|needs_creation'
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Review (Subagents)

**SKIPPED** - Validation is deterministic and doesn't require subjective review.

#### Phase 4: Decision (You)

**What You Do**:

1. **Collect all validation reports** from parallel subagents
2. **Parse validation status** from each report (success/failure/partial)
3. **Check pair_status** for each pair (valid/invalid/needs_creation)
4. **Apply decision criteria**:
   - All pairs valid or needs_creation: PROCEED to Step 2
   - Any pair invalid or search_failed with strict requirements: ABORT with error message
   - Partial success with recoverable issues: ASK USER whether to proceed with valid pairs only
5. **Select next action**:
   - **PROCEED**: All validations successful → Move to Step 2 with validated pairs
   - **PROCEED PARTIAL**: Some valid, some failed → Ask user, then move to Step 2 with valid subset
   - **ABORT**: Critical validation failures → Report errors and stop workflow
6. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark all validation todos as 'completed'
   - If PROCEED PARTIAL: Mark valid todos as 'completed', failed as 'failed'
   - If ABORT: Mark all todos as 'failed' with abort reason
7. **Prepare transition**:
   - If PROCEED: Package validated pairs array for Step 2
   - If ABORT: Generate error report with validation failure details

### Step 2: Compare Content (Conditional)

**Step Configuration**:

- **Purpose**: Compare local and Notion content section-by-section and resolve conflicts with user confirmation
- **Input**: Receives from Step 1: validated file-page pairs array with both local and Notion content
- **Output**: Produces for Step 3: resolved_content_map with merged content for each pair, conflict_report
- **Sub-workflow**: None
- **Parallel Execution**: Yes - one subagent per file-page pair (conflicts resolved interactively)

**CONDITIONAL**: This step only executes if sync_mode = 'two-way-merge'. If sync_mode is 'local-to-notion' or 'notion-to-local', skip directly to Step 3.

#### Phase 1: Planning (You)

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

#### Phase 2: Execution (Subagents)

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

#### Phase 3: Review (Subagents)

**SKIPPED** - User already reviewed and confirmed each conflict resolution interactively.

#### Phase 4: Decision (You)

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

### Step 3: Execute Sync Operations

**Step Configuration**:

- **Purpose**: Execute the actual synchronization between local files and Notion pages based on sync_mode
- **Input**: Receives from Step 1: validated file-page pairs; Receives from Step 2: resolved_content_map (if two-way-merge)
- **Output**: Produces for Step 4: synced_pairs array with sync status per pair, new_pages_created array
- **Sub-workflow**: None
- **Parallel Execution**: Yes - one subagent per file-page pair

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs**:
   - Validated file-page pairs from Step 1
   - Resolved content map from Step 2 (if two-way-merge mode)
   - Sync mode parameter (local-to-notion, notion-to-local, two-way-merge)
2. **Determine sync strategy per pair** based on sync_mode:
   - `local-to-notion`: Local content → Notion (create or update)
   - `notion-to-local`: Notion content → Local (overwrite)
   - `two-way-merge`: Resolved content → Both local and Notion
3. **Use TodoWrite** to create sync task list with one todo per pair (status 'pending')
4. **Prepare sync assignments** for parallel execution (one subagent per pair)
5. **Queue all pairs** for parallel sync execution

**OUTPUT from Planning**: Sync task assignments queued for all pairs

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, you spin up sync subagents to execute sync operations in parallel, launching **N subagents** (one per file-page pair).

- **[IMPORTANT]** Each subagent handles one pair independently
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each pair's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following sync operation:

    >>>
    **ultrathink: adopt the Sync Execution Specialist mindset**

    - You're a **Sync Execution Specialist** with deep expertise in data synchronization who follows these technical principles:
      - **Atomic Operations**: Each sync operation is self-contained and complete
      - **Idempotency**: Sync can be safely retried without side effects
      - **Metadata Preservation**: Maintain tracking data for future syncs
      - **Error Reporting**: Provide clear details on any sync failures

    **Assignment**
    You're assigned to sync a single file-page pair:

    - **File Path**: [file_path]
    - **Notion URL**: [notion_url or 'CREATE_NEW']
    - **Sync Mode**: [sync_mode: local-to-notion|notion-to-local|two-way-merge]
    - **Source Content**: [determined by sync_mode]
      - If local-to-notion: Use local file content
      - If notion-to-local: Use Notion page content
      - If two-way-merge: Use resolved_content from Step 2
    - **Database ID**: [database_id if creating new page]
    - **Parent Page URL**: [parent_page_url if creating new page]

    **Steps**

    **For sync_mode = 'local-to-notion':**

    1. **Prepare Local Content**:
       - Read local file using Read tool
       - Extract content (without frontmatter)
       - Verify content is ready for Notion

    2. **Sync to Notion**:
       - If notion_url exists:
         * Use notion-update-page to overwrite Notion page
         * Pass complete local content
         * No comparison, direct overwrite
       - If notion_url is 'CREATE_NEW':
         * Use notion-create-pages to create new page
         * Set parent as database_id or parent_page_url
         * Set title from file name or frontmatter
         * Store returned notion_url for frontmatter update
       - Capture Notion's response with last_edited_time

    3. **Record Sync Result**:
       - Sync direction: 'local→notion'
       - Sync timestamp: current ISO timestamp
       - Notion URL (new or existing)

    **For sync_mode = 'notion-to-local':**

    1. **Fetch Notion Content**:
       - Use notion-fetch to get complete page content
       - Verify content is valid markdown
       - Preserve Notion's last_edited_time

    2. **Sync to Local**:
       - Use Write tool to overwrite local file
       - Preserve existing frontmatter structure
       - Write Notion content as main content
       - No comparison, direct overwrite

    3. **Record Sync Result**:
       - Sync direction: 'notion→local'
       - Sync timestamp: current ISO timestamp

    **For sync_mode = 'two-way-merge':**

    1. **Get Resolved Content**:
       - Use resolved_content from Step 2 for this pair
       - This content already has conflicts resolved

    2. **Sync to Both Destinations**:
       - **To Local**:
         * Use Write tool to update local file
         * Write resolved_content
         * Preserve frontmatter structure
       - **To Notion**:
         * If notion_url exists: Use notion-update-page
         * If notion_url is 'CREATE_NEW': Use notion-create-pages
         * Write resolved_content
         * Store returned notion_url if new

    3. **Record Sync Result**:
       - Sync direction: 'merged→both'
       - Sync timestamp: current ISO timestamp
       - Notion URL (new or existing)

    **Handle Skipped Conflicts** (only for two-way-merge):
    - If resolved_content contains TODO markers for skipped conflicts:
      * Document these in sync notes
      * Mark sync as 'partial' success
      * User must manually resolve later

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of sync execution'
    modifications: ['[file_path]' or '[notion_url]' or both]
    outputs:
      file_path: '[path]'
      notion_url: '[url]'
      sync_direction: 'local→notion|notion→local|merged→both'
      sync_timestamp: '[ISO timestamp]'
      new_page_created: true|false
      skipped_conflicts_count: [number, 0 if none]
      bytes_synced: [approximate size]
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Review (Subagents)

**SKIPPED** - Sync execution success is deterministic and will be verified in Step 4.

#### Phase 4: Decision (You)

**What You Do**:

1. **Collect all sync reports** from parallel subagents
2. **Parse sync status** from each report (success/failure/partial)
3. **Aggregate sync results**:
   - Total pairs synced successfully
   - Total pairs failed
   - Total new pages created
   - Total bytes synced
4. **Apply decision criteria**:
   - All syncs successful: PROCEED to Step 4 for verification
   - Some syncs partial (skipped conflicts): PROCEED with warnings
   - Any sync failed: Analyze failures, decide RETRY or ABORT
5. **Select next action**:
   - **PROCEED**: All syncs successful or partial → Move to Step 4 for verification
   - **RETRY**: Transient failures (network, rate limits) → Retry failed pairs
   - **ABORT**: Permanent failures (permissions, invalid content) → Report errors and stop
6. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark all sync todos as 'completed'
   - If RETRY: Add new todos for retry attempts with backoff
   - If ABORT: Mark failed todos as 'failed' with abort reason
7. **Prepare transition**:
   - If PROCEED: Package synced_pairs array and new_pages_created for Step 4
   - If RETRY: Generate retry batches with same assignments
   - If ABORT: Generate error report with sync failure details

### Step 4: Verify Sync Integrity

**Step Configuration**:

- **Purpose**: Verify that sync operations completed successfully without data loss or corruption
- **Input**: Receives from Step 3: synced_pairs array with file paths and Notion URLs
- **Output**: Produces for Step 5: verification_report with pass/fail per pair, failed_pairs array if any issues
- **Sub-workflow**: None
- **Parallel Execution**: Yes - one subagent per synced pair

**CRITICAL**: This step implements zero-tolerance error handling. Any verification failure immediately stops the workflow and asks human for manual intervention.

#### Phase 1: Planning (You)

**What You Do**:

1. **Check skip_verification flag**:
   - If skip_verification = true: Skip to Step 5 immediately (not recommended)
   - If skip_verification = false: Continue with verification
2. **Receive synced pairs** from Step 3 output
3. **Use TodoWrite** to create verification task list with one todo per synced pair (status 'pending')
4. **Prepare verification assignments** for parallel execution (one subagent per pair)
5. **Queue all pairs** for parallel integrity verification

**OUTPUT from Planning**: Verification task assignments queued for all synced pairs

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, you spin up verification subagents to check sync integrity in parallel, launching **N subagents** (one per synced pair).

- **[IMPORTANT]** Each subagent handles one pair independently with read-only access
- **[IMPORTANT]** Verification is thorough and checks multiple integrity criteria
- **[IMPORTANT]** Use TodoWrite to update each pair's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following verification:

    >>>
    **ultrathink: adopt the Integrity Verification Specialist mindset**

    - You're an **Integrity Verification Specialist** with deep expertise in data validation who follows these technical principles:
      - **Zero Tolerance**: Any data loss or corruption is unacceptable
      - **Comprehensive Checks**: Verify content, structure, and metadata integrity
      - **Read-Only**: Never modify resources during verification
      - **Clear Evidence**: Provide specific details on what passed or failed

    **Assignment**
    You're assigned to verify integrity for a single synced pair:

    - **File Path**: [file_path]
    - **Notion URL**: [notion_url]
    - **Sync Direction**: [sync_direction from Step 3]
    - **Expected Sync**: [what should have happened based on sync_mode]

    **Steps**

    1. **Read Current State**:
       - Use Read tool to fetch current local file content
       - Use notion-fetch to retrieve current Notion page content
       - Extract content from both sources (without frontmatter for local)

    2. **Verify Content Integrity**:
       - **Length Check**: Compare content lengths (should be similar, allow ±5% for formatting)
       - **Completeness Check**: Verify all major sections are present in both
       - **No Truncation**: Check that content is not cut off mid-sentence or mid-section
       - **Character Integrity**: Verify no corrupted characters or encoding issues

    3. **Verify Structure Integrity**:
       - **Headers Present**: All markdown headers are preserved
       - **Lists Intact**: Bullet points and numbered lists are correct
       - **Code Blocks**: Code blocks are properly formatted
       - **Links Valid**: Internal and external links are not broken

    4. **Verify Sync Direction**:
       - Based on sync_direction, verify the expected source matches destination:
         * If 'local→notion': Notion content should match local
         * If 'notion→local': Local content should match Notion
         * If 'merged→both': Both should have the resolved content

    5. **Identify Any Issues**:
       - Classify severity:
         * **CRITICAL**: Data loss, significant content missing, corruption
         * **WARNING**: Minor formatting differences, whitespace variations
         * **INFO**: Expected differences (Notion rendering differences)
       - Document specific issues found with line numbers or section names

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of verification results'
    modifications: []  # no modifications during verification
    outputs:
      file_path: '[path]'
      notion_url: '[url]'
      verification_status: 'pass|fail'
      checks:
        content_length_match: pass|fail
        completeness_check: pass|fail
        no_truncation: pass|fail
        character_integrity: pass|fail
        structure_integrity: pass|fail
        sync_direction_correct: pass|fail
      local_content_length: [number]
      notion_content_length: [number]
      critical_issues: ['issue1', 'issue2', ...]  # MUST stop workflow
      warnings: ['warning1', 'warning2', ...]  # Non-blocking
    issues: ['issue1', 'issue2', ...]  # same as critical_issues if any
    ```
    <<<

#### Phase 3: Review (Subagents)

**SKIPPED** - Verification results are objective and deterministic.

#### Phase 4: Decision (You)

**What You Do**:

1. **Collect all verification reports** from parallel subagents
2. **Parse verification status** from each report (pass/fail)
3. **Identify any critical issues**:
   - Check each report for critical_issues array
   - If ANY critical issue found: Enter MANUAL FIX mode immediately
4. **Apply ZERO-TOLERANCE decision logic**:
   - **ALL PASS**: All verifications successful → PROCEED to Step 5
   - **ANY FAIL**: At least one verification failed → STOP IMMEDIATELY → MANUAL FIX
5. **Select next action**:
   - **PROCEED**: All verifications passed → Move to Step 5 for metadata update
   - **STOP & MANUAL FIX**: Any verification failed → Execute manual fix protocol
6. **If MANUAL FIX Required**:
   - **Identify Failed Pairs**: Extract all pairs with verification_status = 'fail'
   - **For Each Failed Pair**:
     a. **Read Local Content**: Use Read tool to get current local file content
     b. **Print to Console**: Display content in markdown format ready for copy-paste:

        ```
        ╔═══════════════════════════════════════════════════════════════╗
        ║ SYNC INTEGRITY FAILURE - MANUAL FIX REQUIRED                  ║
        ╠═══════════════════════════════════════════════════════════════╣
        ║ File: [file_path]                                             ║
        ║ Notion: [notion_url]                                          ║
        ║ Issues: [list critical_issues]                                ║
        ╚═══════════════════════════════════════════════════════════════╝

        === CORRECTED CONTENT FOR NOTION (Copy below this line) ===

        [COMPLETE LOCAL CONTENT IN MARKDOWN]

        === END OF CORRECTED CONTENT ===

        INSTRUCTIONS:
        1. Copy the content above (from "===" to "=== END")
        2. Open Notion page: [notion_url]
        3. Select all content in the page
        4. Paste the corrected content
        5. Save the page in Notion
        6. Return here and confirm completion
        ```

     c. **Ask User Confirmation**: Use AskUserQuestion tool:
        - question: "Have you manually fixed the Notion page at [notion_url]?"
        - options:
          - label: "Fixed", description: "I've manually updated the Notion page"
          - label: "Skip", description: "Skip this pair for now"
          - label: "Abort", description: "Stop the entire workflow"
        - multiSelect: false
     d. **Record User Decision**: Track which pairs were fixed, skipped, or caused abort
   - **After All Failed Pairs Processed**:
     - If any marked "Fixed": Optionally re-run verification for those pairs
     - If any marked "Skip": Continue workflow but mark as partial success
     - If any marked "Abort": Stop workflow immediately with abort status
7. **Use TodoWrite** to update task list based on decision:
   - If PROCEED: Mark all verification todos as 'completed'
   - If MANUAL FIX then PROCEED: Mark fixed as 'completed', skipped as 'partial'
   - If ABORT: Mark all todos as 'failed' with abort reason
8. **Prepare transition**:
   - If PROCEED: Package verification_report (all pass) for Step 5
   - If MANUAL FIX then PROCEED: Package partial verification_report with manual fix notes
   - If ABORT: Generate final workflow output with failure status

### Step 5: Update Tracking Metadata

**Step Configuration**:

- **Purpose**: Update local file frontmatter with sync metadata for future tracking and sync operations
- **Input**: Receives from Step 3: synced_pairs with notion_urls and sync_timestamps; Receives from Step 4: verification_report
- **Output**: Produces for Workflow Output: updated_files array, frontmatter_updated boolean
- **Sub-workflow**: None
- **Parallel Execution**: Yes - one subagent per file

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive synced pairs and verification results** from previous steps
2. **Filter successful pairs**: Only update metadata for pairs that synced and verified successfully
3. **Use TodoWrite** to create metadata update task list with one todo per file (status 'pending')
4. **Prepare metadata update assignments** for parallel execution (one subagent per file)
5. **Queue all files** for parallel metadata update

**OUTPUT from Planning**: Metadata update task assignments queued for all successfully synced files

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

In a single message, you spin up metadata update subagents to update frontmatter in parallel, launching **N subagents** (one per file).

- **[IMPORTANT]** Each subagent handles one file independently
- **[IMPORTANT]** Frontmatter update must preserve all existing fields
- **[IMPORTANT]** Use TodoWrite to update each file's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following metadata update:

    >>>
    **ultrathink: adopt the Metadata Management Specialist mindset**

    - You're a **Metadata Management Specialist** with deep expertise in YAML frontmatter who follows these technical principles:
      - **Preservation First**: Never lose existing frontmatter fields
      - **Structured Updates**: Follow consistent YAML formatting
      - **Timestamp Accuracy**: Use ISO 8601 format for all timestamps
      - **Idempotency**: Updates can be safely repeated

    **Assignment**
    You're assigned to update frontmatter for a single file:

    - **File Path**: [file_path]
    - **Notion URL**: [notion_url from Step 3]
    - **Sync Mode**: [sync_mode]
    - **Sync Timestamp**: [sync_timestamp from Step 3]
    - **Sync Status**: [success|partial from Step 3 and Step 4]

    **Steps**

    1. **Read Current File**:
       - Use Read tool to load the file completely
       - Parse existing YAML frontmatter (between --- markers)
       - Extract all existing fields
       - Preserve file content (everything after frontmatter)

    2. **Update Frontmatter Fields**:
       - Create or update these fields:
         ```yaml
         notion_url: '[notion_url]'
         last_edited_at: '[current ISO timestamp]'
         last_synced_at: '[sync_timestamp from Step 3]'
         sync_mode: '[sync_mode]'
         sync_status: 'success|partial'
         ```
       - Preserve all other existing fields (related_files, custom fields, etc.)
       - Maintain YAML formatting and structure

    3. **Write Updated File**:
       - Use Edit tool to update the frontmatter section
       - Replace old frontmatter with updated version
       - Preserve all file content unchanged
       - Ensure proper YAML syntax

    4. **Verify Update**:
       - Read file again to confirm frontmatter was updated correctly
       - Verify no content was lost or corrupted

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of metadata update'
    modifications: ['[file_path]']
    outputs:
      file_path: '[path]'
      frontmatter_updated: true|false
      fields_updated: ['notion_url', 'last_edited_at', 'last_synced_at', 'sync_mode', 'sync_status']
      preserved_fields: [list of other fields kept]
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Review (Subagents)

**SKIPPED** - Metadata update is deterministic and straightforward.

#### Phase 4: Decision (You)

**What You Do**:

1. **Collect all metadata update reports** from parallel subagents
2. **Parse update status** from each report (success/failure)
3. **Aggregate update results**:
   - Total files updated successfully
   - Total files failed to update
4. **Apply decision criteria**:
   - All updates successful: COMPLETE WORKFLOW with success
   - Some updates failed: COMPLETE WORKFLOW with partial success
   - All updates failed: COMPLETE WORKFLOW with failure (but sync already happened)
5. **Select workflow completion**:
   - **SUCCESS**: All metadata updated → Complete with full success status
   - **PARTIAL**: Some metadata updates failed → Complete with warnings
   - **NOTE**: Even if metadata updates fail, sync itself already completed, so this is non-critical
6. **Use TodoWrite** to update task list:
   - Mark completed updates as 'completed'
   - Mark failed updates as 'partial' (non-critical failure)
7. **Prepare final workflow output**:
   - Aggregate all results from Steps 1-5
   - Generate comprehensive workflow completion report
   - Include sync statistics, verification results, metadata status

### Workflow Completion

**Report the workflow output as specified**:

```yaml
workflow: sync-notion
status: success|partial|failure
sync_mode: local-to-notion|notion-to-local|two-way-merge
outputs:
  synced_files: ['path1', 'path2', ...]
  synced_pages: ['url1', 'url2', ...]
  sync_pairs: [
    {
      file: 'path1',
      notion_url: 'url1',
      direction: 'local→notion|notion→local|merged→both',
      status: 'success|partial|failure'
    },
    {
      file: 'path2',
      notion_url: 'url2',
      direction: 'local→notion|notion→local|merged→both',
      status: 'success|partial|failure'
    }
  ]
  conflicts_resolved: 15  # Only populated for two-way-merge mode
  conflict_decisions:  # Only populated for two-way-merge mode
    keep_local: 5
    keep_remote: 3
    keep_both: 4
    skipped: 3
  skipped_conflicts: ['file1: section X', 'file2: section Y']  # Requires manual resolution
  verification_report:
    verified: 10
    passed: 9
    failed: 1
    manually_fixed: 1
  frontmatter_updated: true|false
  files_with_updated_metadata: ['path1', 'path2', ...]
  new_pages_created: ['url3', 'url4']
  total_bytes_synced: 52480
summary: |
  Successfully synced 10 file-page pairs using two-way-merge mode.
  Resolved 12 conflicts with user confirmation. 3 conflicts require manual resolution.
  Verification found 1 integrity issue which was manually fixed by user.
  All frontmatter metadata updated with sync timestamps.
notes: |
  - Skipped conflicts are marked with TODO comments in both local and Notion
  - Manual fix was required for file3 due to content truncation
  - Next sync should check skipped conflicts for resolution
```
