# React Components: Violation Scan

> **Prerequisite**: Read `meta.md` in this directory first for dependencies and rule groups.

Any single violation blocks approval by default.
If a violation is detected, load the matching rule guide at `./rules/<rule-id>.md` to confirm the violation and follow its fix guidance.

## Quick Scan

### File Naming & Structure

- DO NOT name component files in lowercase or kebab-case — use `PascalCase.tsx` (e.g., `Button.tsx`, not `browser.tsx`) [`RC-NAMING-01`]
- DO NOT name hook files with PascalCase — use `camelCase.ts` starting with `use` (e.g., `useScroll.ts`, not `UseScroll.ts`) [`RC-NAMING-01`]

### Component Structure

- DO NOT use class components except for Error Boundaries — use functional components with `FC<Props>` [`RC-STRUCT-01`]
- DO NOT inline anonymous prop types — export an interface (`export interface ButtonProps`) and type the component with it [`RC-STRUCT-02`]

### Props Design

- DO NOT design deeply nested config object props (`config.display.variant`) — keep props flat, simple, and focused [`RC-PROPS-01`]
- DO NOT pile on prop flags to configure variants (`showHeader`, `headerStyle`) when composition (`<Card.Header>`) expresses intent better [`RC-PROPS-02`]

### State Management

- DO NOT lift state to a parent when only one child uses it — keep state local to where it's used [`RC-STATE-01`]
- DO NOT prop-drill the same value through 3+ levels — use Context for deep nesting [`RC-STATE-02`]

### Performance

- DO NOT create object/array literals inline in JSX (`style={{ margin: 10 }}`) — define outside or memoize [`RC-PERF-01`]
- DO NOT skip `useMemo` for genuinely expensive calculations or `useCallback` for handlers passed to memoized children [`RC-PERF-02`]

### Framework Integration

- DO NOT statically import heavy/optional components — use `dynamic(() => import(...))` with a loading fallback [`RC-NEXT-01`]
- DO NOT use raw `<img>` for content images in Next.js — use `next/image` with width/height/alt [`RC-NEXT-01`]

## Rule Matrix

| Rule ID | Violation | Bad Examples |
|---|---|---|
| `RC-NAMING-01` | Wrong file casing for component or hook | `browser.tsx` (should be `Browser.tsx`); `UseScroll.ts` (should be `useScroll.ts`) |
| `RC-STRUCT-01` | Class component used | `class BadButton extends Component { render() { ... } }` |
| `RC-STRUCT-02` | Inline/non-exported props type | `const BadButton = ({ onClick }: { onClick: () => void }) => ...` |
| `RC-PROPS-01` | Deeply nested config-object props | `config: { display: { variant }, behavior: { dismissible } }` |
| `RC-PROPS-02` | Prop explosion instead of composition | `<UserCard title="" showHeader headerStyle="primary" user={user} />` |
| `RC-STATE-01` | State lifted unnecessarily / placed too far from use | Top-level state used by only one leaf component |
| `RC-STATE-02` | Deep prop drilling | Same `user` prop threaded through 4 components instead of Context |
| `RC-PERF-01` | Object/array created inline in render | `style={{ margin: 10 }}`; `options={{ showEmail: true }}` in JSX |
| `RC-PERF-02` | Missing memoization on hot paths | Expensive sort each render; new handler each render passed to memoized child |
| `RC-NEXT-01` | Heavy import without `dynamic`; raw `<img>` instead of `next/image` | `import HeavyChart from '#components/Chart'`; `<img src="/hero.jpg">` |
