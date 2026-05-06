# Notion URL & Database-ID Resolution

Load this reference during **Step 1 (Load and Validate Resources)** in `SKILL.md` whenever a file-page pair has a missing `notion_url` (marked `SEARCH REQUIRED` or `CREATE NEW`). It contains the branching logic the validation subagent uses to resolve a Notion URL from a database ID, fall back to fuzzy search, or signal that a new page must be created in Step 3.

If every pair already has a known `notion_url`, you can ignore this reference.

## Resolve Notion URL (if not provided or marked SEARCH REQUIRED)

- If `database_id` provided:
  * Use notion-search to find existing page
  * Apply fuzzy matching: strip special chars (@, /), lowercase, partial match
  * Search by file name or title from frontmatter
- If found: Record the discovered notion_url
- If not found: Mark as `CREATE_NEW` for Step 3

## Frontmatter URL Extraction (preceding behavior)

Step 1 Phase 1 already extracts `notion_url` from each file's frontmatter before this branching kicks in:

- Read each file's frontmatter to extract `notion_url` field
- If notion_url missing and database_id provided: prepare for fuzzy search (use the branch above)
- If notion_url missing and no database_id: mark as "create new page"

## Status Property Matching

When this skill (or any downstream consumer) reads Notion **status** properties to decide branching, **always match by group + keyword regex**, never by exact option name. Notion database labels drift over time, and exact-name matching silently breaks. Preserve any regex-based status logic exactly as written elsewhere in this skill or its callers.
