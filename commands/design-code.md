---
allowed-tools: Bash, Write, Read, Task, WebSearch, WebFetch, Glob, Grep, TodoWrite, mcp__context7__resolve-library-id, mcp__context7__get-library-docs, mcp__notion__search, mcp__notion__fetch, mcp__notion__create-pages, mcp__notion__update-page

argument-hint: "<instruction>" [--type=api|web-app|mobile|library|fullstack] [--stack=tech-hints] [--reference=docs] [--output=path] [--skip-notion-sync]

description: Create/update DESIGN.md for projects with architecture specs (syncs to Notion)
---

# Design Code

Create or update comprehensive design specification documents (DESIGN.md) for projects, detailing architecture, component specifications, tech stack decisions, API interfaces, and UI design. Works in two modes: CREATE (new greenfield projects) or UPDATE (modify existing designs). Automatically syncs to Notion following a standard template unless --skip-notion-sync is specified.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Document or analyze existing codebases (use code documentation tools instead)
- Generate actual implementation code (this is for design/planning only)
- Make technology decisions without research and justification
- Replace manual code reviews or technical specifications

**When to REJECT:**

- Request to analyze existing code (use analysis tools)
- Vague or unclear instructions without context
- Request to generate implementation code instead of design specs
- Instructions that require implementation details not yet decided

## 📊 Dynamic Context

- **[IMPORTANT]** At the start of the command, you MUST run the command to load all the context below

### System State

- Current branch: !`git branch --show-current`
- Working directory: !`pwd`

### Project Context

- Workflows: !`find ~/.claude/constitutions/workflows "$(git rev-parse --show-toplevel)/constitutions/workflows" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`
- Standards: !`find ~/.claude/constitutions/standards "$(git rev-parse --show-toplevel)/constitutions/standards" -type f -name "*.md" 2>/dev/null | sed 's|^'"$(realpath ~)"'|~|g'`

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 0: Detect Mode and Load Materials

**Actions:**

1. **Determine Operation Mode**:
   - Parse --output argument to determine file path (default: DESIGN.md in current directory)
   - Check if DESIGN.md exists at specified path using Read tool (if file doesn't exist, Read will return error)
   - Extract project name from instruction (first few words or explicit project identifier)
   - Search for existing Notion page:
     - Use `mcp__notion__search` with project name
     - Look for design specification pages matching the project
   - **Set Mode**:
     - **CREATE mode** if: No local DESIGN.md AND no Notion page found
     - **UPDATE mode** if: Local DESIGN.md exists OR Notion page found
   - Store mode for use throughout workflow

2. **Load Existing Design** (if UPDATE mode):
   - If local DESIGN.md exists: Read file content
   - If Notion page exists: Use `mcp__notion__fetch` to retrieve current content
   - If both exist: Use most recent version or prompt user which to use as base
   - Parse existing design structure and content
   - Identify all current sections for targeted updates

3. **Fetch Notion Template** (REQUIRED):
   - **[IMPORTANT]** Use `mcp__notion__fetch` tool to access the standard design template at: <https://www.notion.so/2cc0248cba33432faba65985a2c65047>
   - **[IMPORTANT]** DO NOT use WebFetch or browser tools for Notion URLs - ONLY use Notion MCP tools
   - Extract the complete template structure including all sections, headings, and formatting
   - Store template structure to use as the format guide for generating/updating DESIGN.md
   - Note all required sections and their organization
   - **[IMPORTANT]** Check for child pages in the template:
     - Identify all child pages (e.g., Requirements, API Specification, Architecture Details)
     - For each child page found:
       - Use `mcp__notion__fetch` to retrieve child page content
       - Store child page title and content
       - Map to local filename: convert title to UPPERCASE-WITH-DASHES.md format
       - Example: "Requirements" → "REQUIREMENTS.md", "API Specification" → "API-SPECIFICATION.md"
     - Store child page metadata for use in Steps 7 and 7.5

4. **Load Reference Documentation** (if --reference provided):
   - Parse --reference argument which can be:
     - Notion URLs (<https://www.notion.so/>...): Use `mcp__notion__fetch` tool
     - Local file paths: Use Read tool
     - External URLs: Use WebFetch tool
   - For multiple references, fetch all of them
   - Extract key information:
     - Architecture patterns and decisions
     - Tech stack choices and rationale
     - API design patterns
     - Component structures
     - Best practices and conventions
   - Use reference materials to inform design decisions throughout the workflow

5. **Validate Setup**:
   - Confirm mode detection (CREATE or UPDATE)
   - Confirm successful fetch of Notion template structure
   - If template fetch fails, notify user and ask for alternative template or proceed with default structure
   - Ensure all reference docs are accessible
   - Display mode to user: "Mode: CREATE - generating new design" or "Mode: UPDATE - modifying existing design"

### Step 1: Gather Requirements

**Actions:**

1. **Parse Arguments**:
   - Extract instruction from main argument
   - Parse optional flags: --type, --stack, --reference, --output, --skip-notion-sync
   - Validate output path (default: DESIGN.md in current directory)
   - Note if --skip-notion-sync flag is present (default is to sync to Notion)

2. **Clarify Scope** (mode-dependent):

   **If CREATE mode**:
   - If instruction is vague, ask clarifying questions:
     - What is the primary problem this project solves?
     - Who are the target users?
     - What are the key features/functionality?
     - Any specific constraints (timeline, team size, budget)?
   - If --type not specified, infer from instruction or ask
   - Record all requirements for design document

   **If UPDATE mode**:
   - Parse instruction to understand what needs to change:
     - Which sections to update? (e.g., "Update architecture section")
     - What specific changes? (e.g., "Add caching layer", "Change auth to OAuth")
     - Scope of changes? (e.g., single section vs cross-cutting change)
   - If instruction is ambiguous, ask clarifying questions:
     - Which part of the design should be modified?
     - What is the rationale for this change?
     - Should this affect related sections?
   - Identify impacted sections from existing design

3. **Create Todo List**:
   - Use TodoWrite to track design specification sections to complete/update
   - CREATE mode: All sections from template
   - UPDATE mode: Only sections that need modification

### Step 2: Research Tech Stack

**[Mode-Dependent]**: This step is primarily for CREATE mode. In UPDATE mode, only research if instruction involves tech stack changes.

**Actions:**

1. **Delegate Research to Subtask**:
   - Use Task tool to spawn a subagent for technology research
   - Provide agent with:
     - Project type and requirements from Step 1
     - --stack argument if provided (for validation and research)
     - Mode (CREATE or UPDATE) and scope of research needed
     - Existing tech stack (if UPDATE mode)

   **Research Scope by Mode**:

   **If CREATE mode - Agent should research**:
   - Appropriate tech stack for project type:
     - For APIs: Frameworks (Express, FastAPI, Spring Boot), databases, auth
     - For web apps: Frontend frameworks (React, Vue, Svelte), state management, styling
     - For mobile: React Native, Flutter, native platforms
     - For libraries: Language, build tools, distribution strategy
   - Current best practices and trends using WebSearch
   - Library compatibility and features using mcp__context7 tools
   - Alternatives evaluation and trade-offs

   **If UPDATE mode - Agent should research**:
   - Only specific technologies mentioned in instruction
   - Compatibility with existing stack
   - Migration path if replacing technologies
   - Impact assessment on current architecture

2. **Receive and Process Research Results**:
   - Agent returns comprehensive technology recommendations with:
     - Recommended technologies with justifications
     - Alternatives considered and rejection rationale
     - Version requirements and compatibility notes
     - Official documentation links
     - UPDATE mode: Migration considerations and rationale for changes
   - Incorporate research results into design document planning

### Step 3: Design Architecture

**[Mode-Dependent]**: CREATE mode designs from scratch. UPDATE mode modifies specific architectural aspects per instruction.

**Actions:**

1. **Define System Architecture**:

   **If CREATE mode**:
   - Identify architectural layers (presentation, business logic, data, infrastructure)
   - Choose architectural pattern (MVC, layered, microservices, serverless, etc.)
   - Design data flow and control flow
   - Plan for scalability, security, and maintainability

   **If UPDATE mode**:
   - Identify which architectural aspects need modification per instruction
   - Preserve existing architecture where not affected
   - Assess impact of changes on other architectural components
   - Update only affected layers/patterns while maintaining consistency

2. **Create Architecture Diagram Description**:
   - CREATE mode: Describe complete high-level component relationships (text-based)
   - UPDATE mode: Update diagram description to reflect architectural changes
   - Note key architectural decisions and trade-offs
   - Identify external dependencies and integrations

### Step 4: Specify Components

**[Mode-Dependent]**: CREATE mode specifies all components. UPDATE mode modifies only affected components.

**Actions:**

1. **Break Down into Components**:
   - CREATE mode: Identify all major system components/modules
   - UPDATE mode: Identify which components are affected by the instruction
   - Define component responsibilities and boundaries
   - Specify component interfaces and contracts
   - Document component dependencies (update dependency graph in UPDATE mode)

2. **Detail Component Specifications**:
   - For each component (new or affected):
     - Purpose and responsibilities
     - Key classes/modules/functions
     - Data structures and models
     - Error handling approach
   - UPDATE mode: Preserve specifications of unaffected components

### Step 5: Design APIs (if applicable)

**[Mode-Dependent]**: Skip if not relevant to project type or instruction scope.

**Actions:**

1. **Define API Contracts**:
   - CREATE mode: List all endpoints with HTTP methods
   - UPDATE mode: Add/modify only affected endpoints
   - Specify request/response schemas
   - Define authentication/authorization requirements
   - Document error responses and status codes
   - UPDATE mode: Maintain backward compatibility or document breaking changes

2. **Design Data Models**:
   - CREATE mode: Define all entity schemas
   - UPDATE mode: Modify affected schemas, add new entities, or update relationships
   - Specify relationships and constraints
   - Plan database schema or data storage structure
   - Consider data validation and sanitization
   - UPDATE mode: Plan migration strategy for schema changes

### Step 6: Design UI (if applicable)

**[Mode-Dependent]**: Skip if not relevant to project type or instruction scope.

**Actions:**

1. **Define User Interface Structure**:
   - CREATE mode: List all main screens/pages/views
   - UPDATE mode: Add new screens or modify affected screens only
   - Describe navigation flow and routing
   - Specify user interactions and workflows
   - Note accessibility requirements

2. **Specify UI Components**:
   - CREATE mode: List all reusable UI components needed
   - UPDATE mode: Add new components or modify affected components
   - Define component props and state
   - Specify styling approach (CSS modules, styled-components, Tailwind, etc.)
   - Plan responsive design breakpoints
   - UPDATE mode: Ensure consistency with existing UI patterns

### Step 7: Generate or Update DESIGN.md

**Actions:**

1. **Compile Design Document Following Notion Template**:
   - **[IMPORTANT]** Use the Notion template structure fetched in Step 0 as the format guide
   - Follow the exact section organization, headings, and structure from the template

   **If CREATE mode**:
   - Generate complete design document from scratch
   - Populate each template section with project-specific content:
     - Adapt section names and organization from the Notion template
     - Fill in all required sections based on template structure
     - Maintain the template's formatting and organization
     - Include all subsections present in the template
   - Incorporate insights from reference documentation (if provided) into relevant sections
   - For each section, provide:
     - Clear, actionable content
     - Specific technical details
     - Rationale for decisions
     - Examples where helpful

   **If UPDATE mode**:
   - Load existing DESIGN.md content from Step 0
   - Identify sections affected by the instruction
   - Update only the affected sections with new/modified content:
     - Preserve section structure from template
     - Merge new content with existing content intelligently
     - Maintain consistency in tone and detail level
     - Update cross-references to modified sections
   - Preserve all unaffected sections exactly as they were
   - Add change notes or version history if template includes it
   - Ensure document remains coherent after updates

2. **Write Main File**:
   - Use Write tool to create/overwrite DESIGN.md at specified output path
   - CREATE mode: Write complete new document
   - UPDATE mode: Write merged document with updates applied
   - Ensure proper markdown formatting matching template style
   - Include table of contents if present in template (update in UPDATE mode)
   - Add diagrams descriptions where helpful
   - Preserve template structure and section hierarchy

3. **Write Child Page Files** (if child pages exist from Step 0):
   - For each child page identified in the Notion template:
     - Generate markdown content following the child page template structure
     - Use Write tool to create separate file with UPPERCASE-WITH-DASHES.md naming
     - Include appropriate content based on:
       - CREATE mode: Generate new content following child page structure
       - UPDATE mode: Update existing child file if it exists, create if new
     - Add cross-references:
       - Link from main DESIGN.md to child files: `See [Requirements](./REQUIREMENTS.md)`
       - Link from child files back to main: `← Back to [Main Design](./DESIGN.md)`
     - Maintain consistent formatting with main document
   - Examples of common child pages:
     - REQUIREMENTS.md: Detailed functional and non-functional requirements
     - API-SPECIFICATION.md: Complete API endpoint documentation
     - ARCHITECTURE-DETAILS.md: Deep dive into architectural decisions
     - DATA-MODELS.md: Comprehensive data schema documentation

4. **Update Todo List**:
   - Mark all sections as completed
   - TodoWrite final status
   - Note mode (CREATE or UPDATE) and sections affected
   - List all files created (main + child pages)

### Step 7.5: Sync to Notion (DEFAULT - unless --skip-notion-sync)

**Actions:**

**[IMPORTANT]** This step runs by DEFAULT. Only skip if --skip-notion-sync flag was provided.

#### 7.5.1: Delegate Notion Sync to Subtask

1. **Spawn Sync Agent**:
   - Use Task tool to spawn agent for Notion operations
   - **[CRITICAL]** Instruct agent to use DESIGN.md and child files (from Step 7) as the source of truth
   - Provide agent with:
     - Path to DESIGN.md file generated/updated in Step 7
     - Paths to all child page files (if any exist)
     - Child page metadata from Step 0 (titles, structure)
     - Mode (CREATE or UPDATE) determined in Step 0
     - Existing Notion page URL (if UPDATE mode, from Step 0)
     - Project name from instruction
     - Notion template structure from Step 0

2. **Agent Instructions for Main Page Sync** (mode-dependent):

   **If CREATE mode - Agent should**:
   - Read DESIGN.md file content as source of truth
   - Use `mcp__notion__create-pages` tool (NOT WebFetch or browser tools)
   - Create new page with:
     - Title: Project name
     - Content: Full design specification from DESIGN.md
     - Parent: Appropriate Notion database or page (prompt user if needed)
   - Ensure content follows Notion template structure
   - Return main Notion page URL

   **If UPDATE mode - Agent should**:
   - Read DESIGN.md file content as source of truth
   - Use existing Notion page URL provided
   - Use `mcp__notion__update-page` tool (NOT WebFetch or browser tools)
   - Update page with content from DESIGN.md:
     - All sections from DESIGN.md (including modified and unmodified)
     - Updated metadata (last modified date, version, etc.)
   - Return main Notion page URL

3. **Agent Instructions for Child Page Sync** (if child pages exist):

   **For each child page file** (e.g., REQUIREMENTS.md, API-SPECIFICATION.md):

   **If CREATE mode - Agent should**:
   - Read child page file content as source of truth
   - Use `mcp__notion__create-pages` tool to create child page
   - Create as child of main page with:
     - Title: Child page title from metadata (e.g., "Requirements")
     - Content: Full content from child file
     - Parent: Main Notion page URL from step 2
   - **[CRITICAL]** Position child pages at the TOP of the main Notion page
   - Ensure all child pages appear before main content sections
   - Return child page URLs

   **If UPDATE mode - Agent should**:
   - Check if child page already exists as child of main page
   - If exists: Use `mcp__notion__update-page` to update content
   - If new: Use `mcp__notion__create-pages` to create as described above
   - **[CRITICAL]** Ensure child pages remain at the TOP of the main page
   - Reorder if necessary to maintain child pages above main content
   - Return all child page URLs

4. **Process Sync Agent Results**:
   - Receive main Notion page URL
   - Receive all child page URLs (if any)
   - Store URLs for verification step
   - CREATE mode: Add note at top of local DESIGN.md with link to Notion page
   - UPDATE mode: Ensure link to Notion page is still present and correct in DESIGN.md

#### 7.5.2: Verify Notion Sync (REQUIRED)

**[IMPORTANT]** Notion sync tools are known to be buggy. Verification is MANDATORY.

1. **Spawn Verification Agent**:
   - Use Task tool to spawn separate verification agent
   - **[CRITICAL]** This must be a DIFFERENT agent than the sync agent for independent verification
   - Provide verification agent with:
     - Path to local DESIGN.md
     - Paths to all child page files (if any)
     - Main Notion page URL from 7.5.1
     - All child Notion page URLs from 7.5.1

2. **Verification Agent Instructions**:
   - Use `mcp__notion__fetch` to retrieve content from all Notion pages
   - Compare retrieved content against local files:
     - Main page vs DESIGN.md
     - Each child page vs corresponding child file
   - Check for common sync bugs:
     - **Truncated content**: Missing sections or incomplete text
     - **Broken formatting**: Malformed markdown, broken lists, broken tables
     - **Missing sections**: Entire sections not synced
     - **Corrupted special characters**: Unicode issues, broken code blocks
     - **Child page issues**: Missing child pages, wrong order, incorrect content
   - For each page, return verification status:
     - ✅ PASS: Content matches, no issues
     - ❌ FAIL: List specific issues found with locations

3. **Process Verification Results**:
   - Receive verification report for all pages
   - Count total pages verified and pages with issues
   - If all pages PASS: Mark verification complete, proceed to 7.5.4
   - If any pages FAIL: Proceed to 7.5.3 for patching

#### 7.5.3: Patch Broken Notion Pages (if verification fails)

**[IMPORTANT]** Only runs if 7.5.2 found issues. Can retry up to 3 times.

1. **Spawn Patching Agent** (attempt 1-3):
   - Use Task tool to spawn patching agent (separate from sync and verification agents)
   - Provide patching agent with:
     - Verification report with specific issues
     - Path to local files (DESIGN.md and child files)
     - Notion page URLs that need patching
     - Attempt number (1, 2, or 3)

2. **Patching Agent Instructions**:
   - Focus ONLY on pages and sections that failed verification
   - For each issue identified:
     - Use `mcp__notion__update-page` to apply targeted fix
     - Address specific problem (truncation, formatting, missing content)
     - Use local file as source of truth
   - Apply minimal changes to fix issues
   - DO NOT re-sync entire page unless absolutely necessary
   - Return patching report with actions taken

3. **Re-verify After Patching**:
   - **[CRITICAL]** After patching, MUST re-run verification (return to 7.5.2)
   - Spawn new verification agent to check patched pages
   - Use same verification process as 7.5.2
   - Compare against local files again

4. **Retry Logic**:
   - **Attempt 1**: If re-verification passes → proceed to 7.5.4
   - **Attempt 1**: If re-verification fails → retry patching (attempt 2)
   - **Attempt 2**: If re-verification passes → proceed to 7.5.4
   - **Attempt 2**: If re-verification fails → retry patching (attempt 3)
   - **Attempt 3**: If re-verification passes → proceed to 7.5.4
   - **Attempt 3**: If re-verification fails → Report failure, provide manual fix instructions

5. **Handle Patch Failure After 3 Attempts**:
   - Log all attempts and issues
   - Report to user:
     - Which pages failed verification
     - What issues persist
     - Manual fix recommendations
   - Suggest:
     - Manual review of Notion pages
     - Consider using --skip-notion-sync and sync manually
     - Check Notion API status for service issues
   - Mark sync as partially completed with warnings

#### 7.5.4: Finalize Sync

1. **Update Local Files with Notion Links**:
   - Add or update metadata section in DESIGN.md
   - Include main Notion page URL
   - Include all child Notion page URLs with labels
   - CREATE mode: Add note at top of document
   - UPDATE mode: Update existing metadata

2. **Update Todo**:
   - Mark Notion sync as completed
   - Include verification status: ✅ Verified or ⚠️ Partial (after 3 failed attempts)
   - List all Notion page URLs (main + children)
   - Note: CREATE (new pages) or UPDATE (existing pages updated)
   - If verification failed: Note number of patching attempts

### Step 8: Reporting

**Output Format:**

```
[✅/❌] Command: design-code "$ARGUMENTS"

## Summary
- Mode: [CREATE or UPDATE]
- Design document: [output-path]
- Child documents: [count and list if any, else "None"]
- Template used: Notion template (https://www.notion.so/2cc0248cba33432faba65985a2c65047)
- Template child pages: [count if any, else "None"]
- Reference docs: [count if provided, else "None"]
- Project type: [type]
- Tech stack: [primary technologies or "No changes" if UPDATE with no stack changes]
- Sections [created/updated]: [count]
- Notion sync: [Synced to URL] or [Skipped (--skip-notion-sync)]
- Sync verification: [✅ Verified / ⚠️ Partial / ❌ Failed / Skipped] (if synced)
- Child pages synced: [count and URLs if any, else "None"]

## Actions Taken (mode-dependent)

**If CREATE mode**:
1. Detected CREATE mode - no existing design found
2. Loaded Notion template structure [and N child pages] and reference documentation
3. Gathered requirements and clarified project scope
4. Researched and selected tech stack: [technologies]
5. Designed system architecture: [pattern/approach]
6. Specified [N] major components
7. [Designed API with N endpoints] (if applicable)
8. [Designed UI with N screens/components] (if applicable)
9. Generated comprehensive DESIGN.md following Notion template format
10. [Created N child page files: list filenames] (if template had child pages)
11. [Synced to Notion - created new page and N child pages] (unless --skip-notion-sync)
12. [Verified sync - status: ✅ Verified / ⚠️ Partial after N attempts / ❌ Failed] (if synced)

**If UPDATE mode**:
1. Detected UPDATE mode - loaded existing design from [source]
2. Loaded Notion template structure [and N child pages] and reference documentation
3. Parsed instruction to identify affected sections: [list]
4. [Researched tech stack changes] (if applicable to instruction)
5. [Updated architecture: specific changes made] (if applicable)
6. [Modified components: list of affected components] (if applicable)
7. [Updated API design: endpoints added/modified] (if applicable)
8. [Updated UI design: screens/components modified] (if applicable)
9. Merged changes into DESIGN.md preserving unaffected sections
10. [Updated/created child page files: list affected filenames] (if template had child pages)
11. [Synced to Notion - updated existing page and child pages] (unless --skip-notion-sync)
12. [Verified sync - status: ✅ Verified / ⚠️ Partial after N attempts / ❌ Failed] (if synced)

## Reference Materials Used
- Notion template structure: [sections count]
- [Existing design baseline] (UPDATE mode only)
- [Reference doc 1: key insights extracted] (if provided)
- [Reference doc 2: key insights extracted] (if provided)

## Technology Decisions (if applicable)
- **Frontend**: [framework + reasoning]
- **Backend**: [framework + reasoning]
- **Database**: [choice + reasoning]
- **Infrastructure**: [approach + reasoning]
- UPDATE mode: [Changes made and rationale]

## Changes Summary (UPDATE mode only)
- **Sections modified**: [list]
- **Sections added**: [list]
- **Sections preserved**: [count]
- **Breaking changes**: [Yes/No + description]

## Notion Sync Details (if synced)
- **Main page**: [URL] - [✅ Verified / ⚠️ Issues / ❌ Failed]
- **Child pages** (if any):
  - [Child page 1 name]: [URL] - [✅ Verified / ⚠️ Issues]
  - [Child page 2 name]: [URL] - [✅ Verified / ⚠️ Issues]
- **Verification attempts**: [N attempts if patching was needed]
- **Issues found**: [Brief description if any issues persist]
- **Manual fixes needed**: [List if verification failed after 3 attempts]

## Next Steps
1. Review [created/updated] DESIGN.md [and N child page files] and refine as needed
2. [Review Notion page and child pages] (if synced)
3. [Manually fix any failed verification issues] (if verification warnings)
4. Share with team for feedback and approval
5. [Communicate changes to stakeholders] (UPDATE mode)
6. Begin/continue implementation following design specifications
7. Keep design documents synchronized with implementation
```

## 📝 Examples

### CREATE Mode - Simple API Project

```bash
/design-code "Create REST API for task management with user auth"
# Mode: CREATE (no existing design)
# Creates DESIGN.md with:
# - API endpoints for tasks and users
# - Database schema
# - Auth strategy
# - Tech stack recommendations
# Syncs to Notion automatically
```

### UPDATE Mode - Add Feature to Existing Design

```bash
/design-code "Add caching layer using Redis to the architecture"
# Mode: UPDATE (existing DESIGN.md found)
# Updates only Architecture section:
# - Adds Redis caching layer
# - Updates data flow diagram
# - Preserves all other sections
# Syncs changes to existing Notion page
```

### UPDATE Mode - Modify Authentication

```bash
/design-code "Update authentication from JWT to OAuth 2.0 with Auth0"
# Mode: UPDATE
# Updates multiple sections:
# - Tech Stack: Adds Auth0
# - Architecture: Updates auth flow
# - API Design: Modifies auth endpoints
# - Security: Updates considerations
# Syncs all changes to Notion
```

### UPDATE Mode - Add New API Endpoints

```bash
/design-code "Add user profile management endpoints (GET, PUT /api/users/:id/profile)"
# Mode: UPDATE
# Updates API Design section:
# - Adds new endpoints with schemas
# - Updates API documentation
# - Adds related data models
# Preserves existing endpoints
# Syncs to Notion
```

### CREATE Mode - Skip Notion Sync

```bash
/design-code "Create mobile fitness tracker app" --type=mobile --skip-notion-sync
# Mode: CREATE
# Creates complete DESIGN.md locally
# Does NOT sync to Notion (--skip-notion-sync)
# Use when working offline or Notion not needed
```

### UPDATE Mode - Skip Notion Sync

```bash
/design-code "Add offline support to mobile app" --skip-notion-sync
# Mode: UPDATE
# Updates DESIGN.md locally only
# Does NOT sync changes to Notion
# Useful for draft changes before team review
```

### CREATE Mode - Web App with Type Specification

```bash
/design-code "Create e-commerce storefront" --type=web-app
# Mode: CREATE
# Creates DESIGN.md with:
# - React/Next.js frontend architecture
# - Component specifications
# - State management approach
# - API integration design
# Syncs to Notion
```

### CREATE Mode - With Tech Stack and References

```bash
/design-code "Create real-time chat application" --type=fullstack --stack="Next.js, WebSocket, PostgreSQL" --reference="https://www.notion.so/chat-patterns-id"
# Mode: CREATE
# Fetches reference doc from Notion
# Creates DESIGN.md with suggested stack:
# - Next.js app router architecture
# - WebSocket server design following reference patterns
# - PostgreSQL schema
# - Real-time message flow
# Syncs to Notion
```

### CREATE Mode - Custom Output Path

```bash
/design-code "Create fitness tracking mobile app" --type=mobile --output=docs/DESIGN.md
# Mode: CREATE
# Creates docs/DESIGN.md with:
# - React Native or Flutter recommendation
# - Screen specifications
# - Local storage strategy
# - API integration for cloud sync
# Syncs to Notion
```

### UPDATE Mode - With External Reference

```bash
/design-code "Refactor components to use new design system" --reference="docs/design-system.md"
# Mode: UPDATE
# Loads local reference doc
# Updates UI Design section:
# - Applies design system patterns
# - Updates component specifications
# - Adds new styling guidelines
# Syncs to Notion
```

### CREATE Mode - Complex Fullstack with Multiple Features

```bash
/design-code "Create multi-tenant SaaS for project management" --type=fullstack --stack="Next.js, tRPC, Prisma, PostgreSQL" --reference="https://www.notion.so/saas-arch-id,docs/multi-tenant-guide.md"
# Mode: CREATE
# Fetches both Notion and local references
# Creates comprehensive DESIGN.md:
# - Multi-tenant architecture with tenant isolation
# - Database schema with row-level security
# - tRPC API design
# - React component hierarchy
# - Authentication and RBAC authorization
# - Real-time collaboration features
# - Deployment and scaling strategy
# Syncs to Notion
```

### UPDATE Mode - Multiple Sections

```bash
/design-code "Migrate from REST to GraphQL API" --reference="docs/graphql-guide.md"
# Mode: UPDATE
# Loads GraphQL guide as reference
# Updates multiple sections:
# - Tech Stack: Adds Apollo Server
# - Architecture: Updates API layer design
# - API Design: Replaces REST endpoints with GraphQL schema
# - Components: Updates API client logic
# Preserves UI and other unaffected sections
# Syncs to Notion
```

### Error Case: Vague Instruction (CREATE mode)

```bash
/design-code "app"
# Mode: CREATE attempt
# Response: "Please provide more details:
# - What problem does this project solve?
# - Who are the target users?
# - What are the key features?
# - What type of project? (api, web-app, mobile, library, fullstack)"
```

### Error Case: Ambiguous Update Instruction

```bash
/design-code "Make it better"
# Mode: UPDATE (existing design found)
# Response: "Please clarify your update instruction:
# - Which section(s) need improvement?
# - What specific changes are needed?
# - What is the goal of these improvements?
# Example: 'Improve API performance by adding caching'"
```

### Error Case: Notion Template Unavailable

```bash
/design-code "Create simple REST API" --type=api
# Mode: CREATE
# If Notion template fetch fails:
# Warning: Could not fetch Notion template at https://www.notion.so/2cc0248cba33432faba65985a2c65047
# Proceeding with default structure. Consider providing alternative template.
# Creates DESIGN.md with fallback structure
# Syncs to Notion (if template issue is temporary)
```

### Error Case: Invalid Reference

```bash
/design-code "Create web dashboard" --reference="invalid-url" --type=web-app
# Mode: CREATE
# Error: Could not fetch reference document at "invalid-url"
# Options:
# 1. Continue without reference? (y/n)
# 2. Provide alternative reference URL
# 3. Cancel command
```

### UPDATE Mode - Detecting Existing Design

```bash
# Scenario: DESIGN.md already exists in current directory
/design-code "Add user analytics dashboard"
# Mode: UPDATE (auto-detected existing DESIGN.md)
# Message: "Detected existing design - entering UPDATE mode"
# Updates:
# - UI Design: Adds analytics dashboard screens
# - Components: Adds data visualization components
# - API Design: Adds analytics endpoints
# Preserves existing architecture and other sections
# Syncs to Notion
```
