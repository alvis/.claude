---
name: update-screen-design
description: Update explicitly selected responsive screen-design pages in the canonical Notion Screens database while preserving approved content and applying a template migration or stated change. Use for scoped revisions and accessibility corrections. Require a selector or --all; route missing/new pages to create-screen-design.
model: opus
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[--product=<name>] [--screens=<selector>] [--changes=<request>] [--all]"
---

# Update Screen Design

Update explicitly selected existing pages in the canonical Notion Screens
database. `create-screen-design` owns new pages; the canonical template itself
is never modified here.

## Boundaries

- Use for: scoped revisions, template migrations, and accessibility
  corrections on existing Screens-database pages while preserving approved
  content, relations, and page identity.
- Do not use for: creating a missing screen (`create-screen-design`),
  source-facing design work (`web:design`), rendered assessment
  (`web:audit`), story-state audits (`storybook`), or editing the canonical
  template.

## Inputs

- **Required**: an explicit selection — `--screens=<selector>`,
  `--product=<name>` resolving to an unambiguous bounded set, or explicit
  `--all`. An empty, ambiguous, or unexpectedly broad selection blocks
  mutation; an omitted selector never means all pages.
- **Optional**: `--changes=<request>` for stated modifications beyond
  template alignment.
- **Prerequisites**: the `notion-sync` executable and `NOTION_TOKEN`; stop
  and report if either is missing or auth fails.

## Canonical Notion contract

- Template: `https://www.notion.so/4555730e74b44592b77dd8a97620d3f2`
- Screens database parent: `https://www.notion.so/110161382ea64eefa46a4907574d4530`
- Screens collection: `collection://c7bc479b-71db-41b1-b5ab-a07c641816b5`

<IMPORTANT>
All Notion operations use `notion-sync` through Bash — no other Notion
client. Recursive pulls are one-shot per tree, never a pull loop over
discovered links. Before pulling, search and list the exact page set for
confirmation in the execution record; no page outside that recorded selection
may be written.
</IMPORTANT>

## Workflow

1. Pull the Screens database tree once into this run's before-snapshot:

   ```bash
   notion-sync pull https://www.notion.so/110161382ea64eefa46a4907574d4530 \
     --follow-children --follow-links --out "$RUN_DIR/screens-before"
   ```

2. Pull the current template once:

   ```bash
   notion-sync pull https://www.notion.so/4555730e74b44592b77dd8a97620d3f2 \
     --follow-children --follow-links --out "$RUN_DIR/template"
   ```

3. Resolve the selection only against the mirrored snapshot and record a
   manifest mapping each selected page's `ref:` and URL to its local Markdown
   file, product relation, requested change, and original content snapshot. A
   requested page missing from the database routes to `create-screen-design`;
   a missing or duplicate reference blocks that page. Verify every selected
   page belongs to the canonical parent/collection. If a recursive pull or
   the manifest is incomplete, stop before any push and report partial
   coverage.
4. For each selected page in stable manifest order, compare its headings and
   frontmatter with the template and build a section mapping that says where
   every existing substantive block will live after migration. Preserve
   approved decisions, rationale, alternatives, product relations,
   attachments and links, and still-valid responsive/accessibility content —
   never discard content merely because a template heading changed.
5. Apply only the requested change and necessary template alignment to the
   local file that carries the page's `ref:`, keeping the parent and database
   properties intact. Alternatives may use prose, tables, images, or ASCII;
   no format is mandatory unless the page or request requires it.
6. Run `notion-sync diff <file>` and inspect the complete diff before any
   push. Reject unintended deletion, relation changes, unselected pages, and
   unresolved placeholders; save the diff output as evidence. Record
   already-compliant pages without pushing them.
7. Run `notion-sync push <file>`, then re-read the local frontmatter and
   require the same persisted `ref:`. On auth failure, conflict, partial
   push, changed or missing `ref:`, or uncertain remote state, stop the batch
   immediately — do not retry blindly or continue with later pages. Bulk
   `--all` still requires an exact manifest and per-page diff.
8. Run the verification below for each updated page; when a check fails, fix
   the cause and re-run that check. Repeat until every check passes or a
   concrete blocker remains, then report the blocker instead of looping.

## Verification

- Verify each pushed page with `notion-sync diff <file>` or one post-update
  pull of the selected subtree.
- Confirm the requested change landed, template sections are present, the
  preserved-content mapping is honored, and product/database relations,
  responsive states, and accessibility decisions are intact.
- Confirm no page outside the recorded selection was written and every pushed
  file retains its original stable `ref:`.

## Completion

Return `success`, `partial`, or `blocked`; the selector and `--all` state;
canonical IDs; before/template/after snapshot paths; the page manifest; pages
inspected, changed, already compliant, not attempted, or failed; each diff,
URL, and stable `ref:`; preservation checks; and recovery instructions for
any uncertain page. Never claim full migration when any selected page lacks
verified remote and local state.
