# React workflow

Read this before React, JSX, hooks, component, accessibility, project-structure, test, or Storybook work.

## Actions

| Action | Instruction |
| --- | --- |
| Select standards for React work | `react:react` |
| Mechanically enforce React standards | `react:lint` |
| Write, fix, test, review, document, save, or publish React code | Read `coding:references/WORKFLOW.md`, then use its action owner with the React standards below |
| Create or materially rewrite project artifacts | Follow the injected `essential:references/engineering-work.md` contract |

## Standards

Read every file in each applicable standards directory, following its cross-references.

| Applies to | Standards |
| --- | --- |
| Components and props | `react:constitution/standards/components/` plus `react:constitution/standards/accessibility/` |
| Hooks | `react:constitution/standards/hooks/` |
| Placement and promotion | `react:constitution/standards/project-structure/` |
| Stories | `react:constitution/standards/storybook/` |
| All React implementation | `coding:constitution/standards/universal/`, `coding:constitution/standards/function/`, `coding:constitution/standards/typescript/`, `coding:constitution/standards/naming/`, `coding:constitution/standards/testing/`, and `coding:constitution/standards/documentation/` |
| Files and project setup | `coding:constitution/standards/file-structure.md` |
| Review | `coding:constitution/standards/code-review.md` plus the React standards above |
| Commits, branches, and pull requests | `coding:constitution/standards/git/` |

React does not declare another framework or design plugin as a dependency; do not load standards or skills from one.
