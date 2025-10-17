---
allowed-tools: Bash, Write, Read, Edit, Task, WebSearch, WebFetch, Glob, Grep, TodoWrite, AskUserQuestion, mcp__plugin_coding_context7__resolve-library-id, mcp__plugin_coding_context7__get-library-docs, mcp__plugin_specification_notion__notion-search, mcp__plugin_specification_notion__notion-fetch, mcp__plugin_specification_notion__notion-create-pages, mcp__plugin_specification_notion__notion-update-page

argument-hint: <instruction> [--type=api|web-app|mobile|library|fullstack] [--stack=tech-hints] [--reference=docs] [--output=path] [--sync-template] [--skip-notion-sync]

description: Design/document specifications following strict template structure (syncs to Notion)
---

# Spec Code

Design new project specifications OR retrospectively document existing implementations in DESIGN.md format, following strict Notion template structure. Works in three modes: CREATE (greenfield design), UPDATE (modify existing specs), or DOCUMENT (analyze and document existing code). Performs 2-way merge with Notion by default, comparing local and remote content and requiring user confirmation for each discrepancy before syncing. All files maintain 1:1 mapping with Notion pages and include frontmatter metadata. Automatically syncs to Notion unless --skip-notion-sync is specified.

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Generate implementation code (specification only)
- Make technology decisions without analysis
- Add features not in the template structure
- Create custom sections outside template

**When to REJECT**:

- Vague instructions without clear context
- Requests for code implementation instead of specs
- Instructions requiring undecided implementation details
- Requests to add sections not in template

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Detect Mode and Load Materials

**Actions**:

1. **Determine Operation Mode and Extract Package Name**:
   - Parse --output argument (default: DESIGN.md in current directory)
   - Check if DESIGN.md exists using Read tool
   - Extract project name from instruction
   - Look for package.json in the project directory and read it to extract the package name from the "name" field, which will be used as the Notion page title. If package.json doesn't exist, use the project name from instruction. If neither is available, use the current directory name as fallback.
   - Check if codebase exists (for DOCUMENT mode detection)
   - Store the package name for later use in Notion sync
   - **Set Mode**:
     - **CREATE mode**: No DESIGN.md AND no Notion page AND no codebase
     - **UPDATE mode**: DESIGN.md exists OR Notion page found
     - **DOCUMENT mode**: Codebase exists but no DESIGN.md OR instruction explicitly requests documentation
   - Display mode to user along with the package name that will be used

2. **Load Existing Design** (if UPDATE mode):
   - Read DESIGN.md if exists and check frontmatter for notion_url
   - If notion_url exists in frontmatter, fetch that specific Notion page using `mcp__plugin_specification_notion__notion-fetch`
   - Use most recent version between local and Notion
   - Parse existing structure and content
   - Identify sections for updates

3. **Analyze Existing Codebase** (if DOCUMENT mode):
   - Scan project structure using Glob
   - Read package.json to identify dependencies and extract package name
   - Analyze file organization and architecture
   - Identify key components from imports and exports
   - Extract tech stack from dependencies
   - Map actual implementation to specification structure

4. **Fetch Notion Template and Search Database**:
   - Use `mcp__plugin_specification_notion__notion-fetch` to access template at: <https://www.notion.so/2cc0248cba33432faba65985a2c65047>
   - Extract complete template structure
   - Identify all child pages:
     - Use `mcp__plugin_specification_notion__notion-fetch` for each child
     - Map to local filename: Main word only in UPPERCASE.md format (omit OPTIONAL prefix)
     - Examples: "Components & APIs" → REFERENCE.md, "Requirements" → REQUIREMENTS.md, "Dev Notes" → NOTES.md, "Persistent Data" → DATA.md, "[ Optional ] UI Designs" → UI.md, "[ Optional ] Deployment" → DEPLOYMENT.md
   - Store template metadata for strict adherence
   - Search the Design Specification database (<https://www.notion.so/292b2572f78880fe95b9fdc8daeb862f>) for existing pages matching the package name using `mcp__plugin_specification_notion__notion-search`. Use fuzzy matching to find pages even if the Notion title doesn't exactly match the package name (account for case differences, special characters like @ or /, and partial matches). If an existing page is found in the database and the local frontmatter doesn't have a notion_url, store the found page URL for use in UPDATE mode during sync.

5. **Load Reference Documentation** (if --reference provided):
   - Parse --reference argument:
     - Notion URLs: Use `mcp__plugin_specification_notion__notion-fetch`
     - Local files: Use Read tool
     - External URLs: Use WebFetch tool
   - Extract key information for design decisions

6. **Parse --sync-template Flag** (if provided):
   - Note that template synchronization is requested
   - Will update all local files to match latest template structure
   - Preserve content, reorganize structure only

7. **Validate Setup**:
   - Confirm mode (CREATE, UPDATE, or DOCUMENT)
   - Confirm package name extracted successfully
   - Confirm template fetch success
   - Ensure reference docs accessible
   - Note if existing page was found in database

### Step 2: Resolve Merge Conflicts

**[Conditional]**: Only runs if existing Notion pages were found in Step 1

**Actions**:

1. **Check Merge Requirement**:
   - If no Notion pages exist (new project in CREATE mode): Skip to Step 3
   - If Notion pages exist (UPDATE/DOCUMENT mode or existing pages found): Proceed with merge resolution

2. **Spawn Merge Resolution Subagent**:
   - Use Task tool to delegate merge conflict resolution
   - **Input to subagent**:
     - All local file paths (DESIGN.md + child page files if they exist)
     - All Notion URLs (from frontmatter or Step 1 database search)
     - Operation mode (UPDATE or DOCUMENT)
     - Package name
   - **Subagent responsibilities**:
     - Fetch full content from all Notion pages using `mcp__plugin_specification_notion__notion-fetch`
     - Read all local files using Read tool
     - Compare local vs Notion content section-by-section
     - Identify ALL differences (ignore any ):
       - **Additions**: Content in local but not in Notion
       - **Removals**: Content in Notion but not in local
       - **Modifications**: Content exists in both but differs
     - For EACH difference found:
       - Display LOCAL version clearly
       - Display NOTION version clearly
       - Highlight the specific difference
       - Use AskUserQuestion tool with options:
         - "Keep Local" - use local version
         - "Keep Remote" - use Notion version
         - "Keep Both" - merge both versions
         - "Skip" - leave unresolved for manual fix
       - Record user's decision
     - Apply user decisions to create merged content:
       - Keep Local: Use local content
       - Keep Remote: Use Notion content
       - Keep Both: Intelligently combine both
       - Skip: Mark as TODO in content
     - Write merged content back to local files using Write/Edit tools
     - Return comprehensive merge report:
       - Total conflicts detected
       - Decisions breakdown (Keep Local: X, Keep Remote: Y, Keep Both: Z, Skipped: W)
       - Files modified with change summary
       - List of skipped conflicts needing manual resolution
   - **Required tools**: Read, Write, Edit, AskUserQuestion, mcp__plugin_specification_notion__notion-fetch
   - **Execution mode**: Blocking (must complete before Step 3)

3. **Wait for Merge Completion**:
   - Block and wait for subagent completion
   - Receive merge report from subagent
   - Verify local files have been updated with merged content
   - Store merge statistics for final reporting

4. **Update Todo List**:
   - Mark merge resolution completed
   - Note number of conflicts resolved
   - List files modified

5. **Proceed with Agreed State**:
   - Local files now represent the agreed-upon state (merge of local + Notion)
   - Continue to Step 3 using merged files as the source of truth
   - All subsequent steps work with the merged content

### Step 3: Gather Requirements

**Actions**:

1. **Parse Arguments**:
   - Extract instruction
   - Parse flags: --type, --stack, --reference, --output, --sync-template, --skip-notion-sync
   - Validate output path

2. **Clarify Scope** (mode-dependent):

   **If CREATE mode**:
   - Ask clarifying questions if instruction vague:
     - Primary problem being solved?
     - Target users?
     - Key features?
   - Infer or ask for --type if not specified

   **If UPDATE mode**:
   - Parse instruction for changes needed
   - Identify impacted sections
   - Ask clarifying questions if ambiguous

   **If DOCUMENT mode (NEW)**:
   - Confirm scope of documentation
   - Identify which parts of codebase to document
   - Ask if full system or specific subsystem
   - Clarify documentation depth needed

3. **Create Todo List**:
   - Use TodoWrite to track sections
   - CREATE/DOCUMENT mode: All template sections
   - UPDATE mode: Only impacted sections

### Step 4: Research Tech Stack

**[Mode-Dependent]**: CREATE mode researches new stack. UPDATE mode researches only changed technologies. DOCUMENT mode extracts from existing code.

**Actions**:

1. **Delegate Research**:

   **If CREATE mode**:
   - Use Task tool to spawn research agent
   - Research appropriate stack for project type
   - Evaluate alternatives and trade-offs
   - Get current best practices via WebSearch
   - Check library docs using mcp__context7 tools

   **If UPDATE mode**:
   - Research only technologies mentioned in instruction
   - Check compatibility with existing stack
   - Assess migration path if replacing tech

   **If DOCUMENT mode (NEW)**:
   - Extract tech stack from codebase analysis (Step 1.3)
   - Identify versions from package.json
   - Document actual technologies in use
   - Note framework and library choices made
   - No research needed, document reality

2. **Process Results**:
   - Receive recommendations with justifications
   - Document versions and compatibility
   - Include official documentation links
   - DOCUMENT mode: Document existing stack with actual versions

### Step 5: Design Architecture

**[Mode-Dependent]**: CREATE designs from scratch. UPDATE modifies aspects. DOCUMENT extracts from code.

**Actions**:

1. **Define System Architecture**:

   **If CREATE mode**:
   - Identify architectural layers
   - Choose architectural pattern
   - Design data and control flow
   - Plan for scalability and security

   **If UPDATE mode**:
   - Identify aspects needing modification
   - Preserve unaffected architecture
   - Assess change impact
   - Update affected layers

   **If DOCUMENT mode (NEW)**:
   - Extract architecture from code structure
   - Identify layers from file organization
   - Document actual patterns in use
   - Map component relationships from imports
   - Describe data flow from code analysis

2. **Create Architecture Diagram**:
   - Use mermaid code blocks for all diagrams unless explicitly specified otherwise
   - Create text-based component relationships diagrams
   - Note key decisions and trade-offs
   - Identify external dependencies

### Step 6: Specify Components

**[Mode-Dependent]**: CREATE specifies all. UPDATE modifies affected. DOCUMENT extracts from code.

**Actions**:

1. **Identify Components**:
   - CREATE: Identify all major components/modules
   - UPDATE: Identify affected components
   - DOCUMENT (NEW): Extract components from codebase structure
     - Analyze directory structure
     - Read key files to understand boundaries
     - Map component responsibilities from code
   - Define component interfaces

2. **Detail Component Specifications**:
   - Purpose and responsibilities
   - Key classes/modules/functions
   - Data structures and models
   - Error handling approach
   - DOCUMENT mode: Document actual implementation

### Step 7: Design APIs (if applicable)

**Actions**:

1. **Define API Contracts**:
   - CREATE: List all endpoints
   - UPDATE: Add/modify affected endpoints
   - DOCUMENT (NEW): Extract endpoints from route files
     - Read routing files
     - Document actual endpoints
     - Extract request/response from code
   - Specify authentication/authorization
   - Document error responses

2. **Design Data Models**:
   - CREATE: Define all entity schemas
   - UPDATE: Modify affected schemas
   - DOCUMENT (NEW): Extract schemas from code
     - Read model/schema files
     - Document actual database structure
     - Extract validation rules from code
   - Document relationships and constraints

### Step 8: Design UI (if applicable)

**Actions**:

1. **Define User Interface Structure**:
   - CREATE: List all screens/pages
   - UPDATE: Add/modify affected screens
   - DOCUMENT (NEW): Extract UI structure from code
     - Analyze component files
     - Map screen/page organization
     - Document actual routing from code
   - Describe navigation flow

2. **Specify UI Components**:
   - CREATE: List reusable components
   - UPDATE: Add/modify affected components
   - DOCUMENT (NEW): Extract components from code
     - Read component files
     - Document props and state from TypeScript types
     - Note actual styling approach used
   - Specify styling approach

### Step 9: Generate or Update Files with Frontmatter

**Actions**:

1. **Prepare Frontmatter Metadata**:
   - Initialize frontmatter for all files:

     ```yaml
     ---
     notion_url: https://www.notion.so/... (if synced, else empty)
     last_edited_at: 2025-10-25T10:30:00Z
     last_synced_at: 2025-10-25T10:32:00Z (if synced, else empty)
     related_files: [REFERENCE.md, ...] (for DESIGN.md) or [DESIGN.md] (for child files)
     ---
     ```

   - Use current ISO timestamp for last_edited_at
   - Leave notion_url and last_synced_at empty until Step 10
   - For DESIGN.md: related_files includes all child page files
   - For child files: related_files includes only DESIGN.md

2. **Compile Design Document Following Template**:
   - **STRICT ADHERENCE**: Use exact Notion template structure

   <IMPORTANT>
   You MUST follow the exact same format as the template. This means:
   - If the template uses bullet points, your output MUST use bullet points (not tables, not numbered lists, not other formats)
   - If the template uses tables, your output MUST use tables
   - If the template uses numbered lists, your output MUST use numbered lists
   - If the template uses specific heading levels (e.g., ###), your output MUST use the same heading levels
   - Preserve the exact formatting structure, not just the content structure
   </IMPORTANT>

   - Follow section organization from template
   - Do NOT add sections not in template
   - Do NOT remove sections that are in template

   **If CREATE mode**:
   - Generate complete document from scratch
   - Populate each template section
   - Maintain template formatting
   - Include all subsections from template

   **If UPDATE mode**:
   - Load existing DESIGN.md
   - Update affected sections only
   - Preserve unaffected sections
   - Maintain template structure

   **If DOCUMENT mode (NEW)**:
   - Generate specification based on code analysis
   - Document actual implementation under template sections
   - Fill all template sections with discovered info
   - Note where implementation differs from best practices

3. **Apply --sync-template if Provided**:
   - Fetch latest template structure (already done in Step 1.4)
   - Compare current DESIGN.md with latest template
   - Add any missing sections from template
   - Remove any sections not in current template
   - Reorganize content to match template hierarchy
   - Preserve all content, update structure only
   - Apply same process to all child page files

4. **Write Main File with Frontmatter**:
   - Add frontmatter at top of file
   - Use Write tool for DESIGN.md
   - Ensure proper markdown formatting
   - Use mermaid code blocks for all diagrams unless explicitly specified otherwise
   - Include table of contents if in template
   - Follow template structure exactly

5. **Write Child Page Files with Frontmatter**:
   - For each template child page:
     - Convert title to first word only in UPPERCASE.md (omit OPTIONAL prefix):
       - "Components & APIs" → REFERENCE.md
       - "Requirements" → REQUIREMENTS.md
       - "Dev Notes" → NOTES.md
       - "[ Optional ] UI Designs" → UI.md
       - "[ Optional ] Deployment" → DEPLOYMENT.md
     - Add frontmatter to each file
     - Generate content following child page template
     - CREATE: Generate new content
     - UPDATE: Update existing if exists
     - DOCUMENT: Extract from codebase analysis
     - Add cross-references to main and child files
     - Use Write tool for each file

6. **Update Todo List**:
   - Mark sections completed
   - Note mode and sections affected
   - List all files created (main + children)

### Step 10: Sync to Notion (DEFAULT - unless --skip-notion-sync)

**Only skip if --skip-notion-sync flag provided.**

**Actions**:

1. **Prepare Sync Payload**:
   - Collect all local file paths (DESIGN.md + all child page files created in Step 9)
   - Collect all Notion URLs (from frontmatter or Step 1 database search)
   - Prepare merge report from Step 2 (if merge was performed)
   - Package name from Step 1
   - Operation mode (CREATE/UPDATE/DOCUMENT)
   - Database ID: 292b2572-f788-803f-84f5-000b9b51b8b6

2. **Spawn Notion Sync Subagent**:
   - Use Task tool to delegate all Notion sync operations
   - **Input to subagent**:
     - All local file paths
     - All Notion URLs (if exist)
     - Operation mode
     - Package name
     - Database ID
     - Child page metadata from Step 1
   - **Subagent responsibilities**:
     - Read all local files (DESIGN.md + child pages)
     - Determine create vs update:
       - Check if Notion URL exists from Step 1 search or frontmatter
       - If no URL: Search database with fuzzy matching (strip @, /, lowercase, partial match)
       - If found: Update existing page
       - If not found: Create new page in database
     - For main page:
       - Create/update using `notion-create-pages` or `notion-update-page`
       - Set properties: Name = package name, Status = "Drafting" (CREATE) or "Implemented" (DOCUMENT)
     - For child pages:
       - Check if child pages exist as sub-pages
       - Create/update each child page under main page
       - Title according to metadata (e.g., "Requirements", "Components & APIs")
       - Position child pages at TOP of main page
     - Collect and return all Notion URLs (main + all children)
   - **Required tools**: Read, notion-search, notion-fetch, notion-create-pages, notion-update-page
   - **Execution mode**: Blocking (must complete for verification)

3. **Spawn Verification Subagent**:
   - **Input to subagent**:
     - All local file paths
     - All Notion URLs from sync agent
   - **Subagent responsibilities**:
     - Fetch all Notion pages using `notion-fetch`
     - Compare Notion content vs local files
     - Check for sync bugs: truncated content, broken formatting, missing sections, corrupted chars, missing child pages
     - Return verification status per page (pass/fail)
     - Count total verified pages
   - **Required tools**: Read, notion-fetch
   - If all pass: Proceed to step 4
   - If any fail: Proceed to step 3a

4. **Spawn Patching Subagent** (if verification failed):
   - Maximum 3 retry attempts
   - **Input to subagent**:
     - Verification report (failed pages/sections)
     - Local file paths
     - Notion URLs needing patches
     - Current attempt number
   - **Subagent responsibilities**:
     - Focus only on failed pages/sections
     - Apply targeted fixes using `notion-update-page`
     - Make minimal changes to fix specific issues
     - Return patching report
   - **Required tools**: Read, notion-update-page
   - After patching: Spawn new verification subagent to re-check
   - If still fails after 3 attempts: Log issues, report to user, mark as partially completed

5. **Update Frontmatter** (after successful sync):
   - Update DESIGN.md frontmatter:

     ```yaml
     ---
     notion_url: https://www.notion.so/main-page-id
     last_edited_at: 2025-10-25T10:30:00Z
     last_synced_at: 2025-10-25T10:32:00Z
     related_files: [REFERENCE.md, ...]
     ---
     ```

   - Update each child page file frontmatter:

     ```yaml
     ---
     notion_url: https://www.notion.so/child-page-id
     last_edited_at: 2025-10-25T10:30:00Z
     last_synced_at: 2025-10-25T10:32:00Z
     related_files: [DESIGN.md]
     ---
     ```

   - Use Edit tool for each file
   - Verify all files have non-empty notion_url
   - Count files updated (should match: 1 main + N children)

6. **Update Todo List**:
   - Mark Notion sync completed
   - Include verification status
   - List all Notion URLs (main + children)
   - Note sync mode and database used

### Step 11: Reporting

**Output Format**:

```
[✅/❌] Command: spec-code "$ARGUMENTS"

## Summary
- Mode: [CREATE / UPDATE / DOCUMENT]
- Package name: [name from package.json]
- Design document: [path]
- Child documents: [count and filenames]
- Template: Notion (https://www.notion.so/2cc0248cba33432faba65985a2c65047)
- Template sync: [Yes (--sync-template) / No]
- Project type: [type]
- Tech stack: [technologies or "Documented from code" if DOCUMENT mode]
- Sections [created/updated/documented]: [count]
- Frontmatter: Added to [count] files
- Notion database: Design Specification (https://www.notion.so/292b2572f78880fe95b9fdc8daeb862f)
- Notion sync: [Created in database / Updated existing page / Skipped]
- Database search: [Found existing page / No match found / Skipped]
- Sync verification: [✅ Verified / ⚠️ Partial / Skipped]
- Child pages synced: [count and URLs]
- All frontmatter populated: [Yes / No - missing: list]
- Merge performed: [Yes - Step 2 / No - new files]
- Conflicts detected: [count or N/A]
- Conflicts resolved: [count or N/A]
- User decisions: [Keep Local: X, Keep Remote: Y, Keep Both: Z, Skipped: W or N/A]
- Files merged: [list or N/A]

## Actions Taken

**If CREATE mode**:
1. Detected CREATE mode - greenfield design
2. Extracted package name from package.json: [package-name]
3. Loaded Notion template with [N] child pages
4. Searched Design Specification database - no existing page found
5. Researched tech stack: [technologies]
6. Designed architecture: [pattern]
7. Specified [N] components
8. [Designed API with N endpoints]
9. [Designed UI with N screens]
10. Generated DESIGN.md with frontmatter following template
11. Created [N] child files with frontmatter: [filenames]
12. [Synced to Notion database - created new page titled "[package-name]" with N child pages]
13. [Verified sync - ✅/⚠️]
14. Updated frontmatter in ALL files (main + N children) with Notion URLs and timestamps

**If UPDATE mode**:
1. Detected UPDATE mode - loaded existing design
2. Extracted package name from package.json: [package-name]
3. Loaded Notion template with [N] child pages
4. [Searched database - found existing page / used frontmatter URL]
5. [Performed 2-way merge - resolved X conflicts (Keep Local: Y, Keep Remote: Z, Keep Both: W, Skipped: V)]
6. Identified affected sections: [list]
7. [Updated architecture: changes]
8. [Modified components: list]
9. Merged changes preserving unaffected sections
10. Updated frontmatter timestamps
11. [Updated child files: list]
12. [Applied --sync-template: reorganized to match latest template]
13. [Synced to Notion database - updated existing page and N child pages]
14. [Verified sync - ✅/⚠️]
15. Updated frontmatter in ALL files (main + N children) with sync timestamps

**If DOCUMENT mode (NEW)**:
1. Detected DOCUMENT mode - analyzing existing codebase
2. Extracted package name from package.json: [package-name]
3. Loaded Notion template with [N] child pages
4. Searched Design Specification database - [found/not found] existing page
5. [Performed 2-way merge if existing page - resolved X conflicts]
6. Analyzed codebase structure in [directory]
7. Extracted tech stack from package.json: [technologies]
8. Documented architecture from file organization
9. Identified [N] components from code structure
10. [Extracted API endpoints from route files]
11. [Documented UI components from code]
12. Generated DESIGN.md with frontmatter documenting implementation
13. Created [N] child files with frontmatter: [filenames]
14. [Synced to Notion database - created/updated page titled "[package-name]" with N child pages]
15. [Verified sync - ✅/⚠️]
16. Updated frontmatter in ALL files (main + N children) with Notion URLs and timestamps

## Files Created/Updated
- DESIGN.md (with frontmatter)
- [Child page 1].md (with frontmatter)
- [Child page 2].md (with frontmatter)
- ...

## Frontmatter Details
All files include:
- notion_url: Notion page URL (1:1 mapping)
- last_edited_at: ISO timestamp of last edit
- last_synced_at: ISO timestamp of last Notion sync
- related_files: Array of related MD files ([child files] for DESIGN.md, [DESIGN.md] for child files)

## Template Adherence
- Structure: Follows template exactly
- Sections: Only template sections included
- Hierarchy: Matches template organization
- Diagrams: All in mermaid code blocks
- [Template sync applied: Yes/No]

## Notion Sync Details
- **Database**: Design Specification (https://www.notion.so/292b2572f78880fe95b9fdc8daeb862f)
- **Page title**: [package-name]
- **Main page**: [URL] - [✅/⚠️/❌]
- **Child pages**:
  - [Page 1]: [URL] - [✅/⚠️]
  - [Page 2]: [URL] - [✅/⚠️]
- **Fuzzy match applied**: [Yes - matched "X" to "Y" / No - exact match / No - new page]
- **1:1 Mapping**: Verified - all [N] files have notion_url populated

## Next Steps
1. Review DESIGN.md and child files
2. [Review Notion pages]
3. [Manually fix verification issues if needed]
4. Share with team for feedback
5. [Begin implementation following specs] (CREATE/UPDATE)
6. [Keep specs synchronized with code changes] (DOCUMENT)
```

## 📝 Examples

### CREATE Mode - New API

```bash
/spec-code "Create REST API for task management with user auth"
# Mode: CREATE
# Extracts package name from package.json (e.g., "task-api")
# Creates DESIGN.md with frontmatter
# Creates child page files (REFERENCE.md, NOTES.md, UI.md, DATA.md)
# All files have frontmatter with timestamps and related_files
# Follows template structure exactly
# All diagrams created as mermaid code blocks
# Searches Design Specification database - no existing page found
# Creates new page in database titled "task-api"
# Creates child pages under main page
# Updates frontmatter in ALL files with notion_urls after sync
```

### UPDATE Mode - Add Feature

```bash
/spec-code "Add caching layer using Redis"
# Mode: UPDATE
# Extracts package name from package.json
# Checks frontmatter for existing notion_url
# If notion_url exists: Uses that page
# If not: Searches database for existing page
# Updates Architecture section only
# Updates frontmatter last_edited_at
# Preserves all other sections
# Syncs changes to Notion database
# Updates frontmatter in ALL files with last_synced_at
```

### UPDATE Mode - Database Search with Fuzzy Match

```bash
/spec-code "Update authentication flow"
# package.json has: "@company/auth-service"
# Local frontmatter has no notion_url
# Searches Design Specification database
# Finds existing page titled "Auth Service" via fuzzy matching
# (strips @, /, converts to lowercase, matches "auth-service" to "Auth Service")
# Updates that existing page in database
# Updates child pages
# Populates frontmatter in ALL files with notion_urls
```

### UPDATE Mode - 2-Way Merge with Conflicts (NEW)

```bash
/spec-code "Update architecture section"
# Step 1: Detects existing Notion pages
# Step 2: Spawn merge resolution subagent
#   - Fetch Notion content
#   - Compare with local files
#   - Find 3 conflicts in DESIGN.md, 1 in REFERENCE.md
#   - For each conflict:
#     Conflict 1/4: Architecture Overview
#       LOCAL: "Uses microservices architecture"
#       NOTION: "Uses monolithic architecture"
#       User selects: "Keep Local"
#     Conflict 2/4: Tech Stack
#       LOCAL: "Node.js 20, Express 5"
#       NOTION: "Node.js 18, Express 4"
#       User selects: "Keep Both"
#     Conflict 3/4: New section in local
#       LOCAL: "## Caching Strategy"
#       NOTION: (missing)
#       User selects: "Keep Local"
#     Conflict 4/4: Removed section from local
#       LOCAL: (missing)
#       NOTION: "## Legacy API Support"
#       User selects: "Keep Remote"
#   - Apply decisions and update local files
#   - Return merge report: 4 conflicts resolved
# Step 3-9: Continue with merged files as source of truth
# Step 10: Sync merged content to Notion
# Step 11: Report shows:
#   - Merge performed: Yes
#   - Conflicts detected: 4
#   - Conflicts resolved: 4
#   - User decisions: Keep Local: 2, Keep Remote: 1, Keep Both: 1, Skipped: 0
```

### UPDATE Mode - 2-Way Merge with No Conflicts

```bash
/spec-code "Add new feature section"
# Step 1: Detects existing Notion pages
# Step 2: Spawn merge resolution subagent
#   - Fetch Notion content
#   - Compare with local files
#   - No conflicts found (local and Notion identical)
#   - Skip merge, proceed immediately
# Step 3-9: Add new content to local files
# Step 10: Sync to Notion with only new additions
# Step 11: Report shows:
#   - Merge performed: Yes
#   - Conflicts detected: 0
#   - Conflicts resolved: 0
#   - User decisions: N/A
```

### UPDATE Mode - 2-Way Merge with Skip Decisions

```bash
/spec-code "Refactor API documentation"
# Step 2: Merge resolution finds 5 conflicts
#   - User resolves 3 conflicts (Keep Local/Remote/Both)
#   - User skips 2 conflicts (marked as TODO for manual resolution)
# Local files updated with:
#   - 3 resolved sections
#   - 2 sections marked: "<!-- TODO: Resolve merge conflict -->"
# Step 10: Syncs to Notion with resolved content
# Step 11: Report shows:
#   - Conflicts detected: 5
#   - Conflicts resolved: 3
#   - User decisions: Keep Local: 2, Keep Remote: 0, Keep Both: 1, Skipped: 2
#   - Warning: 2 conflicts require manual resolution
```

### DOCUMENT Mode - Document Existing Code (NEW)

```bash
/spec-code "Document the existing Express API in this codebase"
# Mode: DOCUMENT (auto-detected - codebase exists, no DESIGN.md)
# Extracts package name from package.json (e.g., "express-api")
# Analyzes codebase structure
# Extracts tech stack from package.json
# Documents actual architecture from code organization
# Identifies components from file structure
# Extracts API endpoints from route files
# Generates DESIGN.md documenting reality
# Creates child files with frontmatter
# Searches Design Specification database for "express-api"
# If found: Updates existing page with Status="Implemented"
# If not found: Creates new page in database with Status="Implemented"
# Creates/updates child pages
# Updates frontmatter in ALL files with notion_urls and timestamps
```

### DOCUMENT Mode - Existing Project

```bash
/spec-code "Retrospectively document this Next.js application" --type=web-app
# Mode: DOCUMENT
# Scans Next.js project structure
# Documents actual pages, components, API routes
# Extracts UI component tree from code
# Captures current tech decisions
# Follows template structure
# All files include frontmatter
# Syncs to Notion with 1:1 mapping
```

### UPDATE with Template Sync (NEW)

```bash
/spec-code "Add user analytics dashboard" --sync-template
# Mode: UPDATE
# Fetches latest template structure
# Adds missing sections from template
# Removes sections not in template
# Reorganizes content to match template
# Updates UI Design section with analytics
# Preserves all content, updates structure
# Updates frontmatter timestamps
# Syncs to Notion
```

### CREATE with Template Sync

```bash
/spec-code "Create e-commerce API" --type=api --sync-template
# Mode: CREATE
# Uses latest template structure
# Ensures strict template adherence
# Creates all sections matching template
# No custom sections added
# All files have frontmatter
# Syncs to Notion
```

### DOCUMENT with Skip Sync

```bash
/spec-code "Document existing microservices architecture" --skip-notion-sync
# Mode: DOCUMENT
# Analyzes microservices codebase
# Documents each service structure
# Creates DESIGN.md with frontmatter locally
# Creates child files with frontmatter
# Does NOT sync to Notion
# Frontmatter notion_url and last_synced_at remain empty
```

### UPDATE with Custom Output

```bash
/spec-code "Update authentication to OAuth2" --output=docs/DESIGN.md
# Mode: UPDATE
# Updates docs/DESIGN.md
# Modifies auth-related sections
# Updates frontmatter in docs/DESIGN.md
# Updates child files in docs/ directory
# Syncs to Notion
```

### CREATE with Reference and Stack

```bash
/spec-code "Create SaaS platform" --type=fullstack --stack="Next.js, tRPC, Prisma" --reference="https://www.notion.so/saas-patterns"
# Mode: CREATE
# Fetches reference docs from Notion
# Uses suggested stack
# Follows template structure
# Creates DESIGN.md with frontmatter
# Creates all child page files with frontmatter
# Syncs to Notion
# Updates all frontmatter with URLs
```

### Error - Vague Instruction

```bash
/spec-code "app"
# Error: Please provide more details:
# - What does this app do?
# - Is this CREATE (new design), UPDATE (modify existing), or DOCUMENT (document code)?
# - What type of project?
```

### Error - Custom Section Request

```bash
/spec-code "Create API and add custom 'Future Enhancements' section"
# Warning: Template does not include 'Future Enhancements' section
# Cannot add sections outside template structure
# Please use only template sections or modify template first
```

### DOCUMENT - Partial Codebase

```bash
/spec-code "Document the authentication module only"
# Mode: DOCUMENT
# Analyzes auth-related files only
# Documents auth component architecture
# Extracts auth API endpoints
# Creates focused DESIGN.md
# Follows template structure
# Includes frontmatter
```
