---
name: create-screen-design
description: Create new responsive screen-design documentation in the canonical Notion Screens database for a named product and screen. Use when a product needs a new UX contract, layout alternatives, interaction states, or handoff notes. Preserve the live template and database relations; route existing-page changes to update-screen-design.
model: opus
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "<product> <screen descriptions...> [--constraints=...] [--platforms=...]"
---

# Create screen design

Create new screen pages only. This skill does not update an existing screen, implement UI code, publish a prototype, or force ASCII wireframes when structured layout notes or supplied visuals communicate the contract better.

## Canonical Notion contract

- Template: `https://www.notion.so/4555730e74b44592b77dd8a97620d3f2`
- Screens database parent: `https://www.notion.so/110161382ea64eefa46a4907574d4530`
- Screens collection: `collection://c7bc479b-71db-41b1-b5ab-a07c641816b5`

All Notion operations use `notion-sync` through Bash. Require the executable and `NOTION_TOKEN` before discovery. Never open Notion URLs directly or substitute another API. If auth/tool access fails, stop before local authoring and report the prerequisite.

## Discovery and one-shot pulls

1. Require a product and at least one screen description. Resolve the product and search for colliding screen names with `notion-sync search "<query>" -j`. A found existing screen routes to `update-screen-design`; an unresolved product blocks creation.
2. Create a run directory and pull the template once:

   ```bash
   notion-sync pull https://www.notion.so/4555730e74b44592b77dd8a97620d3f2 \
     --follow-children --follow-links --out "$RUN_DIR/template"
   ```

3. Pull the relevant product/context tree once, using the resolved product URL with `--follow-children --follow-links` (or `--follow` when files/database children are required). Never issue a pull for each discovered link. Preserve these downloaded Markdown files as the content snapshot used for this run.
4. Read the mirrored template and context completely. Record a mapping from every requested screen to its product relation, source context files, platform constraints, and local destination file.

If any recursive pull is incomplete, stop the affected screen as `partial`; do not push from a guessed template or relation.

## Author, inspect, and push

For each new screen:

1. Copy the template's frontmatter shape and required headings into `<run-dir>/<screen-slug>.md`. Set:

   ```yaml
   parent: https://www.notion.so/110161382ea64eefa46a4907574d4530
   ```

   Preserve database property names and set the product relation exactly as represented in the pulled context. Do not add a fake `ref:`; `notion-sync push` writes the created page reference back into the source file.
2. Fill the page with screen purpose, audience/task, content hierarchy, navigation, responsive behavior for requested platforms, interaction and loading/empty/error states, accessibility, alternatives and rationale, accepted/open decisions, implementation notes, and linked product context. Alternatives must be meaningfully distinct, but neither five variants nor ASCII rendering is mandatory.
3. Before push, compare the local page with the template snapshot: required headings, frontmatter/property keys, product relation, responsive coverage, and no unresolved placeholders. Save this pre-push snapshot and screen-to-source mapping.
4. Run `notion-sync diff <file>` when supported for the local reference state; then `notion-sync push <file>`. Read the file again and require a persisted `ref:` plus the returned Notion URL. If push succeeds remotely but `ref:` is not persisted locally, stop and report partial rather than retrying creation and risking a duplicate.
5. Pull the created page once into a verification directory or run `notion-sync diff <file>` against its new `ref:`. Confirm title, required sections, parent database, collection relationship, product relation, and responsive/state coverage.

Do not continue pushing later screens after an auth failure, template mismatch, unresolved identity, or uncertain previous create. Retain local files and mappings so continuation can determine exactly what exists.

## Completion

Return `success`, `partial`, or `blocked`; the canonical IDs used; template/context snapshot paths; per-screen local file, product mapping, persisted `ref:`, URL, and verification result; screens not attempted; and any recovery action. A successful screen has one unambiguous remote page, a locally persisted reference, and verified database/product placement.

Use `update-screen-design` for existing pages, `web:design` for implementation-facing visual design, and `web:audit` for rendered assessment.
