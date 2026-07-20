# Notion URL & Database-ID Resolution

Load this reference during pair resolution whenever a file-page pair lacks a
`ref:`. It documents the thin search/create substitutions over `notion-sync`.

If every pair already has a known `notion_url`, you can ignore this reference.

## Resolve Notion identity

The `notion-sync` CLI handles fuzzy matching internally; you do **not** need to implement strip/lowercase/partial-match logic by hand.

- If a search hint is available (frontmatter title, explicit hint, or
  `database_id`):
  - `Bash: notion-sync search "<title-or-hint>" -j -l 20`
  - Parse the JSON list; pick the best-matching entry and record its URL/id as
    the resolved `notion_ref`.
  - When `database_id` is provided, prefer entries whose `parent` resolves to that database.
- If the search returns no acceptable match: mark the pair as `CREATE_NEW` for Step 3.

## CREATE_NEW Fallback (no existing page)

When a pair is marked `CREATE_NEW`, do **not** call any creation tool here. Instead, defer to Step 3 and prepare the local file for the CLI to create the page on push:

- Set `parent: <database-page-id>` (or a parent page id / sibling local path) in the new file's frontmatter.
- Step 3 then runs `Bash: notion-sync push <file>`. The CLI creates the page under that parent and writes the resulting `ref:` back to the source file's frontmatter.
- Because the CLI writes `ref:` back, no separate metadata-update call is required to capture the new URL.

## Frontmatter identity extraction

Extract `ref:` (preferred) or legacy `notion_url` from frontmatter before this
branch:

- Read each file's frontmatter to extract `ref:` (or legacy `notion_url`).
- If missing and a search hint is available: run `notion-sync search` (the branch above).
- If missing and no hint: mark as `CREATE_NEW` and ensure the file has a `parent:` frontmatter entry before Step 3.

The resolved identity never determines the local filename. Preserve the path
created by notion-sync or explicitly supplied by the caller.

## Status Property Matching

When this skill (or any downstream consumer) reads Notion **status** properties to decide branching, **always match by group + keyword regex**, never by exact option name. Notion database labels drift over time, and exact-name matching silently breaks. Preserve any regex-based status logic exactly as written elsewhere in this skill or its callers.
