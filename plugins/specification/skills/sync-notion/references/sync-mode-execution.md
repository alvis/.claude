# Sync Mode Execution Branches — Step 3

Load this reference during **Step 3 (Execute Sync Operations)** in `SKILL.md`. It contains the mode-specific execution recipes the sync subagent must follow based on the active `sync_mode`. Pick exactly one of the three branches below per pair.

## For sync_mode = 'local-to-notion'

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

## For sync_mode = 'notion-to-local'

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

## For sync_mode = 'two-way-merge'

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
