---
name: create-screen-design
description: Create new responsive screen-design documentation in the canonical Notion Screens database for a named product and screen. Use when a product needs a new UX contract, layout alternatives, interaction states, or handoff notes. Preserve the live template and database relations; route existing-page changes to update-screen-design.
model: opus
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "<product> <screen descriptions...> [--constraints=...] [--platforms=...]"
---

# Create Screen Design

Create new screen-design pages in the canonical Notion Screens database.
`update-screen-design` owns every change to an existing page.

## Boundaries

- Use for: authoring and pushing new screen-design documentation — UX
  contract, layout alternatives, interaction states, responsive behavior, and
  handoff notes — under the Screens database for a resolved product.
- Do not use for: updating an existing screen (`update-screen-design`),
  implementation-facing visual design (`web:design`), rendered assessment
  (`web:audit`), frontend code, clickable prototypes, or modifying the
  canonical template itself.

## Inputs

- **Required**: a product that resolves on Notion and at least one screen
  description. An unresolved product blocks creation.
- **Optional**: `--constraints` (brand, layout, or design limits; default:
  follow the template) and `--platforms` (default: web and mobile).
- **Prerequisites**: the `notion-sync` executable and `NOTION_TOKEN`. If
  either is missing or auth fails, stop before local authoring and report the
  prerequisite.

## Canonical Notion contract

- Template: `https://www.notion.so/4555730e74b44592b77dd8a97620d3f2`
- Screens database parent: `https://www.notion.so/110161382ea64eefa46a4907574d4530`
- Screens collection: `collection://c7bc479b-71db-41b1-b5ab-a07c641816b5`

<IMPORTANT>
All Notion operations use `notion-sync` through Bash. Never open Notion URLs
directly or substitute another API. Recursive pulls are one-shot: a single
`--follow*` invocation per tree, never a separate pull for each discovered
link.
</IMPORTANT>

## Workflow

1. Resolve the product and search for colliding screen names with
   `notion-sync search "<query>" -j`. A found existing screen routes to
   `update-screen-design`.
2. Create a run directory and pull the template once:

   ```bash
   notion-sync pull https://www.notion.so/4555730e74b44592b77dd8a97620d3f2 \
     --follow-children --follow-links --out "$RUN_DIR/template"
   ```

3. Pull the resolved product/context tree once with
   `--follow-children --follow-links` (or `--follow` when file or database
   children are required). Preserve the downloaded Markdown files as this
   run's content snapshot. If any recursive pull is incomplete, mark the
   affected screens `partial`; do not push from a guessed template or
   relation.
4. Read the mirrored template and context completely, then record a mapping
   from every requested screen to its product relation, source context files,
   platform constraints, and local destination file.
5. For each screen, copy the template's frontmatter shape and required
   headings into `<run-dir>/<screen-slug>.md`, set
   `parent: https://www.notion.so/110161382ea64eefa46a4907574d4530`, and
   preserve database property names with the product relation exactly as
   represented in the pulled context. Do not add a fake `ref:`;
   `notion-sync push` writes the created page reference back into the source
   file.
6. Fill each page with screen purpose, audience and task, content hierarchy,
   navigation, responsive behavior for the requested platforms, interaction
   and loading/empty/error states, accessibility, meaningfully distinct
   alternatives with rationale, accepted and open decisions, implementation
   notes, and linked product context. Neither five variants nor ASCII
   rendering is mandatory — structured layout notes or supplied visuals may
   communicate the contract better.
7. Before each push, compare the local page with the template snapshot:
   required headings, frontmatter and property keys, product relation,
   responsive coverage, and no unresolved placeholders. Save this pre-push
   snapshot and the screen-to-source mapping.
8. Run `notion-sync diff <file>` when supported, then `notion-sync push
   <file>`. Re-read the file and require a persisted `ref:` plus the returned
   Notion URL. If the push succeeds remotely but `ref:` is not persisted
   locally, stop and report `partial` rather than retrying creation and
   risking a duplicate. Do not push later screens after an auth failure,
   template mismatch, unresolved identity, or uncertain previous create;
   retain local files and mappings so continuation can determine exactly what
   exists.
9. Run the verification below for each created screen; when a check fails,
   fix the cause and re-run that check. Repeat until every check passes or a
   concrete blocker remains, then report the blocker instead of looping.

## Verification

- Pull each created page once into a verification directory, or run
  `notion-sync diff <file>` against its new `ref:`.
- Confirm title, required template sections, parent database, collection
  relationship, product relation, and responsive/state coverage.
- Confirm each source file carries exactly one persisted `ref:` matching the
  created page — one unambiguous remote page per screen.

## Completion

Return `success`, `partial`, or `blocked`; the canonical IDs used; template
and context snapshot paths; per-screen local file, product mapping, persisted
`ref:`, URL, and verification result; screens not attempted; and any recovery
action. A successful screen has one unambiguous remote page, a locally
persisted reference, and verified database/product placement.
