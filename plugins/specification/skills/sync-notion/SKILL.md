---
name: sync-notion
description: Perform bidirectional synchronization between local markdown files and Notion pages via the `notion-sync` CLI, with conflict resolution and integrity verification. Use when syncing documentation to Notion, pulling Notion pages to local files, or resolving conflicts between local and remote versions.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task, TodoWrite, AskUserQuestion
argument-hint: <sync-mode> <file-paths...> [--database-id=ID] [--skip-verification]
---

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
- `notion-sync` CLI on PATH (verify via `Bash: notion-sync --help`)
- `NOTION_TOKEN` exported in the environment
- Local markdown files with valid frontmatter (`ref:` for existing pages, `parent:` for new pages)
- Understanding of sync modes and their implications

**CLI usage cheat sheet** (use these flag combinations exactly — the CLI walks subgraphs in one call so you never iterate per-page across tool turns):

- `notion-sync pull <ref> --follow-children --follow-links --out <dir>` — single-page + direct references (validation reads, notion→local sync)
- `notion-sync pull <ref> --follow --out <dir>` — full recursive mirror (children + database + links + files)
- `notion-sync push <file>` — uses frontmatter `ref:` (update) or `parent:` (create); CLI writes the new `ref:` back to the file on creation
- `notion-sync push <file> --follow` — also push other local files reachable via `parent:` chains
- `notion-sync diff <file> [-f json]` — block-level diff against the page identified by frontmatter `ref:`
- `notion-sync search "<query>" -j` — JSON search results for URL/id resolution

**Recursion principle (CRITICAL)**: every `notion-sync pull` MUST use the appropriate `--follow*` flag set so a single invocation walks the entire required subgraph. Never loop and pull each linked page individually across separate tool calls.

### Your Role

You are a **Synchronization Orchestrator** who coordinates the documentation sync process like a data pipeline manager overseeing bidirectional data flows, never executing sync operations directly but delegating and coordinating. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. Conflict resolution operates under that mandate: a merged file must read as one document, with remote changes folded into the local block they belong to — never preserved as a quarantined "Notion version" block sitting beside the local copy of the same section. Your management style emphasizes:

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
- **Notion Refs**: Array of Notion page refs (URL, 32-hex id, or title query) corresponding to the files. Resolved from frontmatter `ref:`, `Bash: notion-sync search "<title>" -j`, or provided manually.

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

1. **Receive inputs** from workflow invocation (sync_mode, file_paths, notion_refs, optional parameters)
2. **Extract Notion refs from frontmatter** if not provided:
   - Read each file's frontmatter to extract `ref:` (preferred) or legacy `notion_url`
   - If `ref:` missing and a search hint or `database_id` available: prepare for `notion-sync search`
   - If `ref:` missing and no hint: mark as "create new page" and confirm `parent:` exists in frontmatter (or stage one to be added before Step 3 push)
3. **Create file-page pair mappings**:
   - Pair each file_path with its corresponding notion_ref (or null if creating new)
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
    - **Notion Ref**: [notion_ref or 'SEARCH REQUIRED' or 'CREATE NEW']
    - **Database ID**: [database_id if provided]
    - **Search Hint**: [title from frontmatter / file name]
    - **Parent (CREATE_NEW only)**: [parent_id or parent_page_url if provided]

    **Steps**

    1. **Validate Local File**:
       - Use Read tool to load the file at [file_path]
       - Parse YAML frontmatter if exists (look for `ref:` (preferred), legacy `notion_url`, `parent:`, `last_synced_at`, etc.)
       - Extract file content (everything after frontmatter)
       - Verify file is readable and content is valid markdown
       - Record file size and section count for integrity tracking

    2. **Resolve Notion Ref** (if not provided or marked SEARCH REQUIRED):
       - For search-based resolution and `CREATE_NEW` fallback, see `references/database-resolution.md`.
       - In short: `Bash: notion-sync search "<title-or-hint>" -j -l 20` and pick the best match; otherwise mark `CREATE_NEW` and ensure `parent:` is in frontmatter.

    3. **Validate Notion Page** (if `ref:` exists):
       - **Single recursive pull** for the page + its direct references:
         `Bash: notion-sync pull <ref> --follow-children --follow-links --out <tmp_dir>`
       - Read the resulting `<tmp_dir>/{kebab-title}-{32hex-id}.md` to confirm the page is accessible and fetchable.
       - Extract page content (without frontmatter) for comparison and record approximate length.
       - Treat a non-zero CLI exit, missing output file, or an empty body as inaccessible/archived.
       - **Do not** loop per-linked-page across tool calls; the recursive flags cover them in one invocation.

    4. **Prepare Pair Data**:
       - Package all validated data for downstream steps:
         * file_path: [path]
         * file_content: [content without frontmatter]
         * file_frontmatter: [parsed YAML object, including `ref:` and/or `parent:`]
         * notion_ref: [ref or 'CREATE_NEW']
         * notion_content: [content if exists]
         * notion_pulled_path: [path to the pulled mirror file in tmp_dir, if any]
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
      file_frontmatter: {ref: '...', parent: '...', last_synced_at: '...'}
      notion_ref: '[ref or CREATE_NEW or SEARCH_FAILED]'
      notion_accessible: true|false|N/A
      notion_content_length: [number or 0]
      notion_pulled_path: '[tmp path or null]'
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

**CONDITIONAL**: This step only executes if `sync_mode = 'two-way-merge'`. If sync_mode is `local-to-notion` or `notion-to-local`, skip directly to Step 3.

For the full Step 2 body (planning, comparison subagent prompt, decision logic), see `references/two-way-merge.md`.

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
    - **Notion Ref**: [notion_ref or 'CREATE_NEW'] (already in file frontmatter as `ref:` or `parent:`)
    - **Sync Mode**: [sync_mode: local-to-notion|notion-to-local|two-way-merge]
    - **Source of Truth**: [determined by sync_mode]
      - If local-to-notion: local file is source; push it
      - If notion-to-local: remote ref is source; pull it
      - If two-way-merge: local file already contains Step 2's merged state; push it
    - **Parent (CREATE_NEW only)**: must already be set in file frontmatter as `parent: <database-or-page-id>` before push

    **Steps**

    Follow the mode-specific recipe in `references/sync-mode-execution.md` for the active `sync_mode` (`local-to-notion`, `notion-to-local`, or `two-way-merge`). Each recipe defines how to prepare content, perform the sync, record direction/timestamps, and handle skipped conflicts (two-way-merge only).

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of sync execution'
    modifications: ['[file_path]' and/or remote ref]
    outputs:
      file_path: '[path]'
      notion_ref: '[ref written or read]'
      sync_direction: 'local→notion|notion→local|merged→both'
      sync_timestamp: '[ISO timestamp]'
      new_page_created: true|false  # true when CLI wrote `ref:` back on push
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
    - **Notion Ref**: [notion_ref] (already in file frontmatter as `ref:`)
    - **Sync Direction**: [sync_direction from Step 3]
    - **Expected Sync**: [what should have happened based on sync_mode]

    **Steps**

    1. **Compute Drift via CLI**:
       - `Bash: notion-sync diff <file_path>` — single call. Empty output = no drift = pass.
       - For richer inspection on a fail, re-run `Bash: notion-sync diff <file_path> -f json` and walk the entries.
       - The diff command compares the file's local content against the remote page identified by frontmatter `ref:`. There is no need to separately fetch the Notion page first.

    2. **Verify Content Integrity** (only if diff is non-empty or you need extra confidence):
       - Use Read tool to fetch current local file content for length/section counts.
       - Length and section counts come from the local file; the diff tells you whether remote matches.
       - **Length Check**: Local content length is within ±5% of expected (use synced_pairs metadata).
       - **Completeness Check**: All major sections still present locally.
       - **No Truncation**: Content is not cut off mid-sentence or mid-section.
       - **Character Integrity**: No corrupted characters or encoding issues.

    3. **Verify Structure Integrity** (local-side):
       - **Headers Present**: All markdown headers are preserved
       - **Lists Intact**: Bullet points and numbered lists are correct
       - **Code Blocks**: Code blocks are properly formatted
       - **Links Valid**: Internal and external links are not broken

    4. **Verify Sync Direction**:
       - Based on sync_direction, an empty `notion-sync diff` confirms remote == local for either direction or for `merged→both`.
       - If diff is non-empty, classify which side is authoritative for the sync_direction and record the divergence as a critical issue.

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
      notion_ref: '[ref]'
      verification_status: 'pass|fail'
      diff_empty: true|false  # primary signal from `notion-sync diff`
      diff_entry_count: [number]
      checks:
        completeness_check: pass|fail
        no_truncation: pass|fail
        character_integrity: pass|fail
        structure_integrity: pass|fail
        sync_direction_correct: pass|fail
      local_content_length: [number]
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
        ║ Notion: [notion_ref]                                          ║
        ║ Issues: [list critical_issues]                                ║
        ╚═══════════════════════════════════════════════════════════════╝

        === CORRECTED CONTENT FOR NOTION (Copy below this line) ===

        [COMPLETE LOCAL CONTENT IN MARKDOWN]

        === END OF CORRECTED CONTENT ===

        INSTRUCTIONS:
        1. Copy the content above (from "===" to "=== END")
        2. Open Notion page: [notion_ref]
        3. Select all content in the page
        4. Paste the corrected content
        5. Save the page in Notion
        6. Return here and confirm completion
        ```

     c. **Ask User Confirmation**: Use AskUserQuestion tool:
        - question: "Have you manually fixed the Notion page at [notion_ref]?"
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
    - **Notion Ref**: [notion_ref from Step 3] (likely already written by `notion-sync push`)
    - **Sync Mode**: [sync_mode]
    - **Sync Timestamp**: [sync_timestamp from Step 3]
    - **Sync Status**: [success|partial from Step 3 and Step 4]

    **Steps**

    1. **Read Current File**:
       - Use Read tool to load the file completely
       - Parse existing YAML frontmatter (between --- markers)
       - Extract all existing fields (note: `ref:` may have already been written by `notion-sync push` for newly-created pages — preserve it)
       - Preserve file content (everything after frontmatter)

    2. **Update Frontmatter Fields**:
       - Confirm or set:
         ```yaml
         ref: '[notion_ref]'  # the CLI sets this on create; verify present on update
         last_edited_at: '[current ISO timestamp]'
         last_synced_at: '[sync_timestamp from Step 3]'
         sync_mode: '[sync_mode]'
         sync_status: 'success|partial'
         ```
       - Preserve all other existing fields (`parent:`, related_files, custom fields, etc.).
       - Maintain YAML formatting and structure.

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
      fields_updated: ['ref', 'last_edited_at', 'last_synced_at', 'sync_mode', 'sync_status']
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
      notion_ref: 'ref1',
      direction: 'local→notion|notion→local|merged→both',
      status: 'success|partial|failure'
    },
    {
      file: 'path2',
      notion_ref: 'ref2',
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
