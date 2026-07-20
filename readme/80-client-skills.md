# client skills (depends on: essential)

[Back to marketplace overview](../README.md#plugins-and-skills)

Client-facing screen design and UX documentation with Notion integration

This catalog is generated from the plugin manifest and each skill's `SKILL.md` frontmatter. Run `python3 scripts/generate_readme.py` after changing either source.

- `client:create-screen-design` — Create a new responsive screen-design contract from notion-derived work context, keep temporary exploration in the active work item, sync approved content through MDC/Notion owners, and promote durable design docs. Route existing screens to update-screen-design.
- `client:update-screen-design` — Update explicitly selected responsive screen-design contracts from notion-derived work context, preserving identity and approved content while recording temporary work design and promoting durable versioned design. Require a selector or --all; route missing pages to create-screen-design.
