# Notion Sync — 4-Step Protocol

Default behavior of spec-code Step 10. Skipped only when `--skip-notion-sync` is provided.

**Database**: Design Specification — `https://www.notion.so/292b2572f78880fe95b9fdc8daeb862f` (database ID `292b2572-f788-803f-84f5-000b9b51b8b6`).

All Notion interactions go through the `notion-sync` CLI (`Bash: notion-sync ...`). The CLI requires `NOTION_TOKEN` in env. Recursive operations MUST use `--follow*` flags so a single invocation walks the entire subgraph — never iterate per-page across tool-call turns.

## Step 1 — Prepare Sync Payload

Collect:

- All local file paths (DESIGN.md + every child page file created in Step 9).
- All Notion refs known so far (from frontmatter `ref:`, or resolved via `Bash: notion-sync search "<title>" -j`).
- Merge report from the merge-resolution step (if any).
- Package name (from Step 1).
- Operation mode (CREATE / UPDATE / DOCUMENT).
- Database ID `292b2572-f788-803f-84f5-000b9b51b8b6`.
- Child page metadata captured in Step 1.

## Step 2 — Push Local Files to Notion

For every local file (DESIGN.md + child pages), run **one** `notion-sync push` per file. The CLI decides create-vs-update from the file's frontmatter.

### 2a — Update existing pages (`ref:` already present)

If the file's frontmatter already contains `ref:` (a Notion URL or 32-hex id), the CLI updates that page in place:

- `Bash: notion-sync push <file_path>`
- Add `--follow` if the file references other local files (via `parent:` chains) that should also be pushed in the same call.
- The CLI sets page properties on `Name` and any other frontmatter-mapped fields. For the main DESIGN.md, ensure frontmatter carries `Status: "Drafting"` (CREATE mode) or `Status: "Implemented"` (DOCUMENT mode) so the push propagates it.

### 2b — Create new pages (no `ref:` yet)

For files that do not yet exist on Notion:

1. Ensure the file's frontmatter contains `parent:` set to:
   - `292b2572-f788-803f-84f5-000b9b51b8b6` (the Design Specification database id) for the main DESIGN.md, or
   - the parent page id (or sibling local path) of the main DESIGN.md for each child page.
2. `Bash: notion-sync push <file_path>`
3. The CLI creates the page under `parent:` and **writes the resulting `ref:` back into the file's frontmatter**. No separate metadata step is required to capture the new URL.
4. Position child pages at the TOP of the main page (the CLI's child ordering follows the order children are pushed; push children immediately after the main page in the desired top-to-bottom order, or rely on `parent:` resolution against the main page).

### Collect URLs

After all pushes complete, re-read each file's frontmatter `ref:` to assemble the canonical list of Notion URLs (main + every child).

**Required tools**: Read, Edit, Bash (`notion-sync push`, `notion-sync search`).

**Execution mode**: Blocking (must complete before verification).

## Step 3 — Verify Sync Integrity

For each local file, run:

- `Bash: notion-sync diff <file_path>`
  - Empty output (or zero diff entries) ⇒ pass for that file.
  - Non-empty output ⇒ drift detected; record the file + diff summary for Step 4.

The diff command compares the file's local content against the remote page identified by frontmatter `ref:`. There is no need to fetch each page separately first.

**Required tools**: Bash (`notion-sync diff`).

If all files pass: proceed to Step 5.
If any file shows drift: proceed to Step 4 (patching).

## Step 4 — Re-Push Drifted Files (only if verification failed)

**Maximum 3 retry attempts.**

For each file flagged in Step 3:

- `Bash: notion-sync push <file_path>` — re-pushes the local file as the source of truth.
- After all drifted files are re-pushed, re-run Step 3 (`notion-sync diff`) to verify.

Increment the retry counter on every full Step 3 → Step 4 cycle. If files still show drift after 3 attempts: log the issues, report to the user, and mark sync as partially completed.

**Required tools**: Bash (`notion-sync push`, `notion-sync diff`).

## Step 5 — Update Frontmatter

`notion-sync push` already writes `ref:` back for newly-created pages. After verification passes, use the Edit tool to set or refresh the remaining sync metadata in every file:

- Confirm `ref:` is set (the CLI handled this on creation; verify present for every file).
- Set `last_synced_at` to the ISO 8601 timestamp of the successful sync.
- Verify all files have a non-empty `ref:`.
- Confirm the count of updated files equals `1 main + N children`.

For the exact frontmatter schema, see `references/frontmatter.md`.

## Update Todo List

- Mark Notion sync completed.
- Include verification status (`Verified` / `Partial`).
- List all Notion URLs (main + children).
- Note sync mode and database used.
