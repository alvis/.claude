# Web workflow

Read this before UI/UX design, CSS, image-generation, Next.js diagnosis, Storybook audit, rendered-interface audit, or frontend implementation work.

## Actions

| Action | Instruction |
| --- | --- |
| Design or redesign an interface | `web:design` |
| Audit a rendered interface | `web:audit` |
| Create or maintain the root color-mode stylesheet | `web:css` |
| Generate or edit visual assets | `web:imagine` |
| Diagnose a Next.js runtime | `web:next` |
| Audit Storybook | `web:storybook` |
| Write, test, review, save, or publish frontend code | Read `coding:references/WORKFLOW.md`, then use its action owner |
| Create or materially rewrite project artifacts | Follow the injected `essential:references/engineering-work.md` contract |

Before work delegation, read `web:references/ROUTING.md`.

## Standards

Read every file in each applicable standards directory, following its cross-references.

| Applies to | Standards |
| --- | --- |
| Visual and interaction design or audit | `web:constitution/standards/design/` |
| Light, dark, and system color modes | `web:constitution/standards/css/` plus `web:constitution/standards/design/` |
| Brand and token theming | `web:constitution/standards/theming/` plus `web:constitution/standards/css/` and `web:constitution/standards/design/` |
| Frontend implementation | `coding:constitution/standards/universal/`, `coding:constitution/standards/function/`, `coding:constitution/standards/typescript/`, `coding:constitution/standards/naming/`, `coding:constitution/standards/testing/`, and `coding:constitution/standards/documentation/` |
| Files and project setup | `coding:constitution/standards/file-structure.md` |
| Review | `coding:constitution/standards/code-review.md` plus the Web standards above |
| Commits, branches, and pull requests | `coding:constitution/standards/git/` |

Web does not declare another framework plugin as a dependency; do not load its standards or skills.
