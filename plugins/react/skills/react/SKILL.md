---
name: react
description: 'Apply React, Next.js, JSX, hooks, accessibility, and Storybook standards proactively whenever React work happens. Triggers when: editing or creating .tsx/.jsx files, writing JSX, building React/Next.js components, authoring custom hooks (use*), managing React state, combining Tailwind with React, writing Storybook .stories.tsx files, or whenever the user mentions "React", "Next.js", "JSX", "hook", "component", "useState/useEffect/useMemo/useCallback", "memo", "Server Component", "client component", or "story". Use to enforce naming, structure, performance, accessibility (WCAG 2.1 AA), and story-coverage rules across the React surface.'
model: sonnet
context: inline
allowed-tools: Read, Glob, Grep, Skill
---

# React Standards

Always-on enforcer for the React/Next.js surface. Loads the four React sub-standards and routes detail work to specialised skills. Standards content lives in the standard files — this skill links to them, it does not duplicate them.

## When to use / triggers

Activate proactively whenever any of these are happening:

- Reading, editing, or creating `.tsx` / `.jsx` files
- Writing JSX (component returns, fragments, JSX expressions)
- Building React or Next.js components (functional components, FC, RSC, client components)
- Authoring or modifying custom hooks (any function with the `use*` prefix)
- Using built-in hooks: `useState`, `useEffect`, `useMemo`, `useCallback`, `useReducer`, `useRef`, `useContext`
- Managing React component state (local, lifted, or via Context)
- Combining Tailwind CSS classes with React component markup
- Writing or updating Storybook stories (`*.stories.tsx`, `*.demo.stories.tsx`)
- Explicit user mentions of: React, Next.js, JSX, hooks, components, stories, memoization, ARIA, accessibility on web

Skip when the work is purely backend, CLI, build-config, or non-UI library code with no React surface.

## Standards loaded

Four sub-standards govern this surface. Each has a three-tier layout (`meta.md` for orientation, `scan.md` to audit existing code, `write.md` to author new code, plus a `rules/` directory for granular violations).

### Accessibility (WCAG 2.1 AA)

Semantic HTML, keyboard navigation, ARIA, focus management, forms, color/contrast, screen-reader support.

- Meta: `/Users/alvis/Repositories/.claude/plugins/react/constitution/standards/accessibility/meta.md`
- Scan existing code: `/Users/alvis/Repositories/.claude/plugins/react/constitution/standards/accessibility/scan.md`
- Write new code: `/Users/alvis/Repositories/.claude/plugins/react/constitution/standards/accessibility/write.md`
- Rule groups: `A11Y-SEMA-*`, `A11Y-KBD-*`, `A11Y-HEAD-*`, `A11Y-ARIA-*`, `A11Y-FOCUS-*`, `A11Y-FORM-*`, `A11Y-COLOR-*`, `A11Y-SR-*`

### React Components

Functional components with TypeScript interfaces, single responsibility, prop design, state placement, performance (`memo`/`useMemo`/`useCallback`), Next.js integration patterns.

- Meta: `/Users/alvis/Repositories/.claude/plugins/react/constitution/standards/react-components/meta.md`
- Scan existing code: `/Users/alvis/Repositories/.claude/plugins/react/constitution/standards/react-components/scan.md`
- Write new code: `/Users/alvis/Repositories/.claude/plugins/react/constitution/standards/react-components/write.md`
- Rule groups: `RC-NAMING-*`, `RC-STRUCT-*`, `RC-PROPS-*`, `RC-STATE-*`, `RC-PERF-*`, `RC-NEXT-*`

### React Hooks

`use*` naming, consistent return shapes, dependency arrays, async data hooks (`{ data, loading, error, refetch }`), cleanup, stable references, composition, `useReducer` for complex state.

- Meta: `/Users/alvis/Repositories/.claude/plugins/react/constitution/standards/react-hooks/meta.md`
- Scan existing code: `/Users/alvis/Repositories/.claude/plugins/react/constitution/standards/react-hooks/scan.md`
- Write new code: `/Users/alvis/Repositories/.claude/plugins/react/constitution/standards/react-hooks/write.md`
- Rule groups: `RH-NAMING-*`, `RH-RETURN-*`, `RH-DEPS-*`, `RH-ASYNC-*`, `RH-CLEANUP-*`, `RH-STABLE-*`, `RH-COMPOSE-*`, `RH-REDUCER-*`

### Storybook

PascalCase `.stories.tsx` filenames, path-based titles, complete state coverage (default/disabled/loading/error/edge), `Meta`/`StoryObj` typing, `tags: ['autodocs']`, `play` interactions, comprehensive `argTypes`, pure stories using existing components and mock data.

- Meta: `/Users/alvis/Repositories/.claude/plugins/react/constitution/standards/storybook/meta.md`
- Scan existing code: `/Users/alvis/Repositories/.claude/plugins/react/constitution/standards/storybook/scan.md`
- Write new code: `/Users/alvis/Repositories/.claude/plugins/react/constitution/standards/storybook/write.md`
- Rule groups: `SB-NAME-*`, `SB-ORG-*`, `SB-COVERAGE-*`, `SB-STRUCT-*`, `SB-PLAY-*`, `SB-CONTROLS-*`, `SB-PURE-*`

## Workflow: scan → write → verify

Pick the tier that matches the activity. Do not load every file — load only what the current task touches.

### Scan (auditing existing React code)

When reading or reviewing existing `.tsx` / `.jsx` / hooks / stories:

- Load the relevant `scan.md` files for the surfaces you are inspecting (components, hooks, accessibility, storybook).
- Apply the heuristics in those files to flag violations by rule group code (e.g. `RC-PERF-*`, `A11Y-KBD-*`).
- For deep enforcement across many files, delegate to `coding:lint` and pass the standards paths above so the linter agent applies them.

### Write (authoring new React code)

When creating or modifying components, hooks, or stories:

- Load the relevant `write.md` files BEFORE drafting code so patterns are correct on first pass.
- Always pair `react-components/write.md` with `accessibility/write.md` (every component must be accessible).
- Add `react-hooks/write.md` whenever a `use*` function is involved.
- Add `storybook/write.md` whenever a `*.stories.tsx` file is involved.
- Honour the dependent-standard chain declared in each `meta.md` (TypeScript, Function, Naming, Documentation, Testing, File Structure standards from the coding plugin).

### Verify (after a flagged violation)

When a scan or review surfaces a specific violation code, open the matching file under the standard's `rules/` directory for the precise rule definition and remediation. Re-run the relevant `scan.md` heuristic to confirm the fix.

## Hand-off / routing

Defer to the right skill instead of doing the work inline:

- Detailed implementation work (full TDD lifecycle: design → skeleton → implement → test → refactor) → `coding:write-code`
- Granular single-component scaffold (one component, one tree, one shot) → `react:create-component`
- Design, visual, layout, palette, typography, animation work → `web:design`
- Next.js debugging (SSR, App Router, route handlers, build issues, RSC boundaries, hydration) → `web:next`
- Linting / standards enforcement across many files → `coding:lint` (pass the standard paths above)
- Story authoring as part of a broader feature → keep scope here; for a one-shot scaffold defer to `react:create-component`

This skill itself does NOT scaffold components, run lifecycles, or fix lint at scale — it loads context, surfaces the right standards, and routes.
