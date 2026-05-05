# Notion Sync — 4-Step Protocol

Default behavior of spec-code Step 10. Skipped only when `--skip-notion-sync` is provided.

**Database**: Design Specification — `https://www.notion.so/292b2572f78880fe95b9fdc8daeb862f` (database ID `292b2572-f788-803f-84f5-000b9b51b8b6`).

## Step 1 — Prepare Sync Payload

Collect:

- All local file paths (DESIGN.md + every child page file created in Step 9).
- All Notion URLs known so far (from frontmatter or Step 1 database search).
- Merge report from the merge-resolution step (if any).
- Package name (from Step 1).
- Operation mode (CREATE / UPDATE / DOCUMENT).
- Database ID `292b2572-f788-803f-84f5-000b9b51b8b6`.
- Child page metadata captured in Step 1.

## Step 2 — Spawn Notion Sync Subagent

Use the Task tool to delegate Notion sync.

**Input to subagent**: all local file paths, all known Notion URLs, operation mode, package name, database ID, child page metadata.

**Subagent responsibilities**:

- Read all local files (DESIGN.md + child pages).
- Determine create vs update for the main page:
  - Check if a Notion URL is already known (from Step 1 search or frontmatter).
  - If no URL: search the database with fuzzy matching — strip `@` and `/`, lowercase, allow partial match.
  - If found: update the existing page using `mcp__plugin_specification_notion__notion-update-page`.
  - If not found: create a new page in the database using `mcp__plugin_specification_notion__notion-create-pages`.
- Set page properties on the main page:
  - `Name` = package name.
  - `Status` = `"Drafting"` (CREATE mode) or `"Implemented"` (DOCUMENT mode).
- For each child page:
  - Check whether the child already exists as a sub-page of the main page.
  - Create or update the child under the main page.
  - Set the title from child page metadata (e.g. `"Requirements"`, `"Components & APIs"`).
  - Position child pages at the TOP of the main page.
- Collect and return all Notion URLs (main + every child).

**Required tools**: Read, `notion-search`, `notion-fetch`, `notion-create-pages`, `notion-update-page`.

**Execution mode**: Blocking (must complete before verification).

## Step 3 — Spawn Verification Subagent

**Input**: all local file paths, all Notion URLs returned by the sync subagent.

**Subagent responsibilities**:

- Fetch all Notion pages using `notion-fetch`.
- Compare Notion content vs local files.
- Check for sync bugs: truncated content, broken formatting, missing sections, corrupted characters, missing child pages.
- Return verification status per page (pass / fail).
- Count total verified pages.

**Required tools**: Read, `notion-fetch`.

If all pages pass: proceed to Step 5.
If any page fails: proceed to Step 4 (patching).

## Step 4 — Spawn Patching Subagent (only if verification failed)

**Maximum 3 retry attempts.**

**Input**: verification report (failed pages/sections), local file paths, Notion URLs needing patches, current attempt number.

**Subagent responsibilities**:

- Focus only on failed pages/sections.
- Apply targeted fixes using `notion-update-page`.
- Make minimal changes to fix the specific issues identified.
- Return a patching report.

**Required tools**: Read, `notion-update-page`.

After patching: spawn a fresh verification subagent to re-check.
If still failing after 3 attempts: log the issues, report to the user, and mark sync as partially completed.

## Step 5 — Update Frontmatter

After successful sync, use the Edit tool to update frontmatter in every file:

- Set `notion_url` to the page URL returned by the sync subagent.
- Set `last_synced_at` to the ISO 8601 timestamp of the successful sync.
- Verify all files have a non-empty `notion_url`.
- Confirm the count of updated files equals `1 main + N children`.

For the exact frontmatter schema, see `references/frontmatter.md`.

## Update Todo List

- Mark Notion sync completed.
- Include verification status (`Verified` / `Partial`).
- List all Notion URLs (main + children).
- Note sync mode and database used.
