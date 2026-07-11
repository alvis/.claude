---
name: update-screen-design
description: Update existing responsive screen-design pages in Notion while preserving approved content and applying an explicit change request. Use for template migrations, accessibility corrections, or scoped screen revisions. Do not use for new pages; route creation to create-screen-design.
model: opus
allowed-tools: Bash, Read, Write, Edit, Glob, Skill
argument-hint: "[--product=<name>] [--screens=<selector>] [--changes=<request>] [--all]"
---

# Update screen design

Update existing Screens database pages. This skill owns documentation migration and revision; it does not create a missing page, implement UI code, or redesign an entire product without a selector.

## Inputs and boundaries

- Optional product filter, screen selector, and explicit change request.
- `--all` is required for an intentional bulk update; an omitted selector never means all pages.
- Notion access through `notion-sync`; the current template and each page's `ref:` are authoritative.

Reject an empty result, an unresolved selector, a request to create a new screen, or a request for frontend implementation.

## Workflow

1. Resolve the selector with one database pull and list the exact pages to change. Pull the current template once; fetch linked page context in the same recursive pull.
2. Compare each selected page with the template and requested change. Preserve content that remains valid, fold changes into the existing sections, and keep responsive states and accessibility decisions explicit.
3. Edit local Markdown files that already contain `ref:` values, then run `notion-sync diff` before `notion-sync push`. Never push an unselected page.
4. Pull or diff the updated pages to verify required sections, preserved relations, responsive coverage, and the requested change. Record pages already compliant separately from pages modified.

## Output

Report `status`, selector, pages inspected, pages changed, pages already compliant, conformance checks, and issues. Include each updated Notion URL and a short change summary.

## Ownership

Use `create-screen-design` for new pages. Use `web:design` for visual implementation direction, `web:audit` for rendered UI assessment, and `storybook` for story-state checks.
