# Frontmatter Specification

Every file produced by spec-code (DESIGN.md and all child page files) MUST include YAML frontmatter so Notion sync can maintain a 1:1 mapping between local files and Notion pages.

## Schema

```yaml
---
notion_url: https://www.notion.so/...      # Notion page URL (empty until synced)
last_edited_at: 2025-10-25T10:30:00Z       # ISO 8601 timestamp of last local edit
last_synced_at: 2025-10-25T10:32:00Z       # ISO 8601 timestamp of last Notion sync (empty until synced)
related_files: [REFERENCE.md, NOTES.md]    # See rules below
---
```

## Field Rules

- **`notion_url`** — Full Notion page URL. Leave empty (`notion_url:`) until Step 10 (Notion sync) populates it. Verify all files have a non-empty `notion_url` after sync; the count must equal `1 main + N children`.
- **`last_edited_at`** — ISO 8601 timestamp of the most recent local edit. Always populated.
- **`last_synced_at`** — ISO 8601 timestamp of the most recent successful Notion sync. Empty until Step 10. Updated by the Edit tool after sync verification passes.
- **`related_files`** — Cross-reference array:
  - In **DESIGN.md**: list every child page file (e.g. `[REFERENCE.md, REQUIREMENTS.md, NOTES.md, DATA.md, UI.md, DEPLOYMENT.md]`).
  - In each **child file**: list only `[DESIGN.md]`.

## Initial vs Post-Sync State

### Initial (Step 9, before Notion sync)

```yaml
---
notion_url:
last_edited_at: 2025-10-25T10:30:00Z
last_synced_at:
related_files: [REFERENCE.md, NOTES.md, DATA.md]
---
```

### After Successful Sync (Step 10.5)

DESIGN.md:

```yaml
---
notion_url: https://www.notion.so/main-page-id
last_edited_at: 2025-10-25T10:30:00Z
last_synced_at: 2025-10-25T10:32:00Z
related_files: [REFERENCE.md, NOTES.md, DATA.md]
---
```

Each child page file:

```yaml
---
notion_url: https://www.notion.so/child-page-id
last_edited_at: 2025-10-25T10:30:00Z
last_synced_at: 2025-10-25T10:32:00Z
related_files: [DESIGN.md]
---
```

## Update Protocol

- Use the Edit tool to update frontmatter in place; do not rewrite the whole file.
- After sync verification passes, update both `notion_url` and `last_synced_at` in every file.
- If sync is skipped (`--skip-notion-sync`), `notion_url` and `last_synced_at` remain empty.
- Verify that the number of files with non-empty `notion_url` equals `1 main + N children`.

## Filename Mapping (Notion title → local file)

Convert each Notion child-page title to its first main word in UPPERCASE, omitting any `[ Optional ]` prefix:

| Notion title              | Local file       |
| ------------------------- | ---------------- |
| Components & APIs         | `REFERENCE.md`   |
| Requirements              | `REQUIREMENTS.md`|
| Dev Notes                 | `NOTES.md`       |
| Persistent Data           | `DATA.md`        |
| [ Optional ] UI Designs   | `UI.md`          |
| [ Optional ] Deployment   | `DEPLOYMENT.md`  |
