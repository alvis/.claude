---
name: update-screen-design
description: Update explicitly selected responsive screen-design pages in the canonical Notion Screens database while preserving approved content and applying a template migration or stated change. Use for scoped revisions and accessibility corrections. Require a selector or --all; route missing/new pages to create-screen-design.
model: opus
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[--product=<name>] [--screens=<selector>] [--changes=<request>] [--all]"
---

# Update screen design

Update existing screen pages only. This skill does not create a missing screen, implement frontend code, or modify the canonical template. Never treat an omitted selector as all pages.

## Canonical Notion contract and gate

- Template: `https://www.notion.so/4555730e74b44592b77dd8a97620d3f2`
- Screens database parent: `https://www.notion.so/110161382ea64eefa46a4907574d4530`
- Screens collection: `collection://c7bc479b-71db-41b1-b5ab-a07c641816b5`

Require `notion-sync` and `NOTION_TOKEN`; use no other Notion client. Require `--screens`, `--product` plus an unambiguous bounded result, or explicit `--all`. Before pulling, search and list the exact page set for confirmation in the execution record. Empty, ambiguous, or unexpectedly broad results block mutation.

## One-shot snapshot and mapping

1. Pull the Screens database tree once:

   ```bash
   notion-sync pull https://www.notion.so/110161382ea64eefa46a4907574d4530 \
     --follow-children --follow-links --out "$RUN_DIR/screens-before"
   ```

2. Pull the current template once:

   ```bash
   notion-sync pull https://www.notion.so/4555730e74b44592b77dd8a97620d3f2 \
     --follow-children --follow-links --out "$RUN_DIR/template"
   ```

3. Select only from the mirrored database snapshot. Record a manifest mapping each selected Notion `ref:` and URL to its local Markdown file, product relation, requested change, and original content snapshot. Never follow discovered links with per-page pull loops.
4. Verify every selected page belongs to the parent/collection above and already has a stable `ref:`. A missing page routes to `create-screen-design`; a missing/duplicate reference blocks that page.

If either recursive pull or mapping is incomplete, stop before pushes and report partial coverage.

## Preserve, diff, push, verify

For each selected page, in stable order:

1. Compare its headings/frontmatter with the template. Build a section mapping that says where every existing substantive block will live after migration. Preserve approved decisions, rationale, alternatives, product relations, attachments/links, and still-valid responsive/accessibility content. Do not discard content merely because a template heading changed.
2. Apply only the requested change and necessary template alignment to the local file that carries the page's `ref:`. Keep the parent and database properties intact. Alternatives may use prose, tables, images, or ASCII; no format is mandatory unless the page or request requires it.
3. Run `notion-sync diff <file>` and inspect the complete diff. Reject unintended deletion, relation changes, unselected pages, and unresolved placeholders before push. Save the diff path/output as evidence.
4. Run `notion-sync push <file>`. Re-read the local frontmatter and require the same persisted `ref:`. On auth, conflict, partial push, changed/missing ref, or uncertain remote state, stop the batch immediately; do not retry blindly or continue with later pages.
5. Verify using `notion-sync diff <file>` or one post-update pull of the selected subtree. Check requested change, template sections, preserved-content mapping, product/database relations, responsive states, and accessibility decisions. Record already-compliant pages without pushing them.

Bulk `--all` still requires an exact manifest and per-page diff. No page outside the recorded selector may be written.

## Completion

Return `success`, `partial`, or `blocked`; selector and `--all` state; canonical IDs; before/template/after snapshot paths; page mapping; pages inspected, changed, already compliant, not attempted, or failed; each diff, URL and stable `ref:`; preservation checks; and recovery instructions. Never claim full migration when any selected page lacks verified remote and local state.

Use `create-screen-design` for new pages, `web:design` for source-facing design work, `web:audit` for rendered QA, and `storybook` for story-state audits.
