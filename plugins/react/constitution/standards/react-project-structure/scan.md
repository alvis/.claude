# React Project Structure: Violation Scan

> **Prerequisite**: Read `meta.md` in this directory first for dependencies, exception policy, and rule groups.

Any single violation blocks submission by default.
If a violation is detected, load the matching rule guide at `./rules/<rule-id>.md`.

## Quick Scan

### Top-Level Layout

- DO NOT place code outside the decision order (route → feature → shared → utility → type), or skip a tier when a lower one applies [`RPS-LAYOUT-01`]

### `src/app/` (Route)

- DO NOT use `_components/` (Next.js underscore convention) — use `components/` [`RPS-ROUTE-01`]
- DO NOT put domain logic in `page.tsx` — `page.tsx` only composes feature containers and route-local components [`RPS-ROUTE-02`]

### `src/components/` (Shared, domain-agnostic UI)

- DO NOT import from `features/**` or `app/**` inside `src/components/**` [`RPS-COMPS-01`]
- DO NOT create domain-named folders (e.g., `components/billing/`) or a `containers/` folder under `src/components/` — allowed buckets are `primitives/`, `layouts/`, `composites/`, `headless/`, `boundaries/`, `providers/`, `adapters/` [`RPS-COMPS-02`]

### `src/features/<domain>/`

- DO NOT import from `features/<other>/**` inside `features/<this>/**` — cross-feature reuse means promotion to `src/components/` or `src/utilities/` [`RPS-FEAT-01`]
- DO NOT mix container (data-fetching/orchestration) and presentational (prop-in/JSX-out) responsibilities in the same file under `features/<domain>/` [`RPS-FEAT-02`]
- DO NOT create `features/ui/` or `features/shared/` — "shared" is not a domain [`RPS-FEAT-03`]

### `src/utilities/` and `src/types/`

- DO NOT use JSX, hooks, or React imports inside `src/utilities/` — utilities must be React-unaware [`RPS-UTIL-01`]
- DO NOT put domain-specific types in `src/types/` — they belong in `src/features/<domain>/types/` [`RPS-UTIL-01`]

### Promotion

- DO NOT promote a component to `src/components/` (or to `src/features/<domain>/`) with only one consumer — wait for the second real consumer; demote when reuse evaporates [`RPS-PROMO-01`]

## Rule Matrix

| Rule ID | Violation | Bad Examples |
|---|---|---|
| `RPS-LAYOUT-01` | Code placed out of decision order | `src/utilities/UserCard.tsx` (component in utilities); domain code in `src/types/` |
| `RPS-ROUTE-01` | Underscore-prefixed route-local folder | `src/app/dashboard/_components/Header.tsx` |
| `RPS-ROUTE-02` | Domain logic in `page.tsx` | `page.tsx` calls `fetchInvoices()` and renders an invoice table inline |
| `RPS-COMPS-01` | Upward import from shared components | `src/components/primitives/Button.tsx` imports from `#features/billing/...` |
| `RPS-COMPS-02` | Disallowed subfolder under `src/components/` | `src/components/billing/`; `src/components/containers/InvoiceList.tsx` |
| `RPS-FEAT-01` | Cross-feature import | `src/features/billing/...` imports from `#features/profile/...` |
| `RPS-FEAT-02` | Container/presentational mix | `features/billing/components/InvoiceList.tsx` calls `useQuery(...)` and renders styled JSX |
| `RPS-FEAT-03` | "shared" or "ui" used as a domain | `src/features/shared/Button.tsx`; `src/features/ui/Card.tsx` |
| `RPS-UTIL-01` | React in utilities, or domain type in global types | `src/utilities/useDebounce.ts` (hook in utilities); `src/types/Invoice.ts` |
| `RPS-PROMO-01` | Premature promotion | A `Button` lives in `src/components/primitives/` but is imported by exactly one feature |
