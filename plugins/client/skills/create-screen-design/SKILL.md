---
name: create-screen-design
description: Create new responsive screen-design documentation in Notion for a named product and screen. Use when a product needs a new UX contract, layout alternatives, interaction states, or handoff-ready design notes. Do not use for changing an existing screen; route those requests to update-screen-design.
model: opus
allowed-tools: Bash, Read, Write, Edit, Glob, Skill
argument-hint: "<product> <screen descriptions...> [--constraints=...] [--platforms=...]"
---

# Create screen design

Create new screen records in the Screens database. This skill owns creation only; it does not update existing pages, implement UI code, or publish a prototype.

## Inputs

- Product name and one or more new screen descriptions (required).
- Optional responsive platforms, accessibility constraints, brand rules, or interaction requirements.
- Notion access through the `notion-sync` CLI and the current screen-design template.

Reject a missing product or screen description, an unknown product, a request to modify an existing page, or a request for frontend implementation.

## Workflow

1. Confirm the product and screen list with `notion-sync search`; pull the template and relevant product context once with `notion-sync pull --follow-children --follow-links`.
2. Create one local Markdown page per requested screen. Keep the template's required headings, but express alternatives as concise structured layout notes rather than mandatory ASCII diagrams or a fixed count of variants.
3. Document content hierarchy, responsive behavior, states, accessibility, open decisions, and implementation notes. Keep each page self-contained and link related product records.
4. Push each page with `notion-sync push`, using the Screens database as `parent:`. Never push a page whose product or screen identity is unresolved.
5. Pull or diff the created pages to verify required sections, database relation, responsive coverage, and the returned Notion reference.

## Output

Report `status`, created page URLs, screens completed, responsive/platform coverage, template sections checked, and any unresolved issues. Leave local source files beside the generated `ref:` values so the pages can be resumed or reviewed.

## Ownership

Use `update-screen-design` for migrations or edits to existing pages. Use the web plugin's `design` for implementation-facing visual direction and `web:audit` for assessing a rendered interface.
