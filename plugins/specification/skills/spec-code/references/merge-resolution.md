# 2-Way Merge Conflict Resolution

Conflict-resolution protocol for reconciling local DESIGN.md (and child page files) with their Notion counterparts. Runs only when existing Notion pages were found in Step 1 of the spec-code workflow.

## When To Run

- **Skip** if no Notion pages exist (new project in CREATE mode).
- **Run** if Notion pages exist (UPDATE/DOCUMENT mode, or existing pages found via database search).

## Protocol

### 1. Check Merge Requirement

- If no Notion pages exist (new project in CREATE mode): Skip to next step of parent workflow.
- If Notion pages exist (UPDATE/DOCUMENT mode or existing pages found): Proceed with merge resolution.

### 2. Spawn Merge Resolution Subagent

Use the Task tool to delegate merge conflict resolution.

**Input to subagent**:

- All local file paths (DESIGN.md + child page files if they exist)
- All Notion URLs (from frontmatter or Step 1 database search)
- Operation mode (UPDATE or DOCUMENT)
- Package name

**Subagent responsibilities**:

- Fetch full content from all Notion pages using `mcp__plugin_specification_notion__notion-fetch`.
- Read all local files using the Read tool.
- Compare local vs Notion content section-by-section.
- Identify ALL differences:
  - **Additions**: Content in local but not in Notion.
  - **Removals**: Content in Notion but not in local.
  - **Modifications**: Content exists in both but differs.
- For EACH difference found:
  - Display LOCAL version clearly.
  - Display NOTION version clearly.
  - Highlight the specific difference.
  - Use the AskUserQuestion tool with options:
    - **Keep Local** — use local version
    - **Keep Remote** — use Notion version
    - **Keep Both** — merge both versions
    - **Skip** — leave unresolved for manual fix
  - Record the user's decision.
- Apply user decisions to create merged content:
  - Keep Local: Use local content.
  - Keep Remote: Use Notion content.
  - Keep Both: Intelligently combine both.
  - Skip: Mark as TODO in content (e.g. `<!-- TODO: Resolve merge conflict -->`).
- Write merged content back to local files using Write/Edit tools.
- Return a comprehensive merge report (see below).

**Required tools**: Read, Write, Edit, AskUserQuestion, `mcp__plugin_specification_notion__notion-fetch`.

**Execution mode**: Blocking (must complete before the next workflow step).

### 3. Wait for Merge Completion

- Block and wait for subagent completion.
- Receive merge report from subagent.
- Verify local files have been updated with merged content.
- Store merge statistics for final reporting.

### 4. Update Todo List

- Mark merge resolution completed.
- Note number of conflicts resolved.
- List files modified.

### 5. Proceed with Agreed State

- Local files now represent the agreed-upon state (merge of local + Notion).
- Continue to the next workflow step using merged files as the source of truth.
- All subsequent steps work with the merged content.

## Merge Report Format

Return:

- Total conflicts detected.
- Decisions breakdown (Keep Local: X, Keep Remote: Y, Keep Both: Z, Skipped: W).
- Files modified with change summary.
- List of skipped conflicts needing manual resolution.

## Example Conflict Walkthrough

```
Conflict 1/4: Architecture Overview
  LOCAL:  "Uses microservices architecture"
  NOTION: "Uses monolithic architecture"
  User selects: Keep Local

Conflict 2/4: Tech Stack
  LOCAL:  "Node.js 20, Express 5"
  NOTION: "Node.js 18, Express 4"
  User selects: Keep Both

Conflict 3/4: New section in local
  LOCAL:  "## Caching Strategy"
  NOTION: (missing)
  User selects: Keep Local

Conflict 4/4: Removed section from local
  LOCAL:  (missing)
  NOTION: "## Legacy API Support"
  User selects: Keep Remote
```

If the user skips conflicts, the affected sections are marked with a TODO comment for manual follow-up, and the report's `Skipped` count reflects this.
