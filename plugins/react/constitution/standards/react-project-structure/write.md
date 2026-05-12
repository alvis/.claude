# React Project Structure: Compliant Code Patterns

> **Prerequisite**: Read `meta.md` in this directory first for dependencies, exception policy, and rule groups.
> **Compliance**: Also follow `scan.md` in this directory to avoid violations during writing. When unsure about a specific rule, consult its detailed guidance in `rules/<rule-id>.md`.

## Key Principles

- Apply the decision order **route → feature → shared → utility → type** and stop at the first yes.
- Code starts route-local; promote outward only when a second real consumer appears.
- Imports flow one-way: `app/` → `features/` → `components/` → `utilities/`. Never reverse, never sideways between features.
- `src/components/` is domain-agnostic UI grouped by capability (primitives, layouts, composites, headless, boundaries, providers, adapters) — never by domain.
- Inside `src/features/<domain>/`, split container (`api/`, `hooks/`, `containers/`) from presentational (`components/`).
- `src/utilities/` is React-unaware. `src/types/` is for globally-shared types only.

## Core Rules Summary

### Top-Level Layout (RPS-LAYOUT)

- **RPS-LAYOUT-01**: Place code by the first-yes match in route → feature → shared → utility → type.

### Route (RPS-ROUTE)

- **RPS-ROUTE-01**: Route-local folder is `components/`, never `_components/`.
- **RPS-ROUTE-02**: `page.tsx` is a composition layer — no domain logic.

### Shared Components (RPS-COMPS)

- **RPS-COMPS-01**: `src/components/**` must not import from `features/**` or `app/**`.
- **RPS-COMPS-02**: Allowed buckets are primitives, layouts, composites, headless, boundaries, providers, adapters. No domain-named folders. No `containers/`.

### Features (RPS-FEAT)

- **RPS-FEAT-01**: A feature must not import from another feature.
- **RPS-FEAT-02**: Inside `features/<domain>/`, containers fetch/orchestrate and `components/` are pure presentational.
- **RPS-FEAT-03**: No `features/ui/` or `features/shared/` — "shared" is not a domain.

### Utilities & Types (RPS-UTIL)

- **RPS-UTIL-01**: `utilities/` is React-unaware (no JSX, no hooks, no React imports); domain types live in their feature.

### Promotion (RPS-PROMO)

- **RPS-PROMO-01**: Promote on the second real consumer. Demote when reuse evaporates.

## Patterns

### Reference Layout

```plaintext
src/
├── app/                              # Next.js routes
│   ├── layout.tsx
│   ├── page.tsx
│   └── <route>/
│       ├── page.tsx                  # composes feature containers + route-local components
│       ├── layout.tsx
│       └── components/               # route-local only (NOT _components/)
│           └── DashboardHeader.tsx
│
├── components/                       # domain-agnostic, reusable UI
│   ├── primitives/                   # Button, Input, Badge
│   ├── layouts/                      # PageShell, SidebarLayout, Grid
│   ├── composites/                   # Card, Modal, Combobox, Tabs (styled)
│   ├── headless/                     # Tabs (logic-only), Disclosure, Listbox
│   ├── boundaries/                   # ErrorBoundary, SuspenseBoundary
│   ├── providers/                    # ThemeProvider, AppProviders
│   └── adapters/                     # RadixTabsAdapter, DateAdapter, AnalyticsAdapter
│
├── features/                         # domain code, reused across routes in that domain
│   └── <domain>/                     # e.g., billing/, profile/, search/
│       ├── api/                      # fetchInvoices, createInvoice (data functions)
│       ├── hooks/                    # useInvoices, useInvoiceMutations
│       ├── containers/               # InvoiceListContainer (fetch + orchestrate)
│       ├── components/               # InvoiceRow, InvoiceBadge (pure, prop-in/JSX-out)
│       └── types/                    # Invoice, InvoiceStatus (domain types)
│
├── utilities/                        # React-unaware pure functions
│   ├── formatCurrency.ts
│   └── parseDate.ts
│
└── types/                            # globally-shared types only (e.g., ApiResponse<T>)
    └── api.ts
```

### Decision Order (first-yes wins)

1. **Is this for exactly one route?** Place it in `src/app/<route>/components/` (`RPS-ROUTE-01`).
2. **Is this domain-scoped and reused across routes inside that domain?** Place it in `src/features/<domain>/` (`RPS-FEAT-02`).
3. **Is this domain-agnostic UI?** Place it in `src/components/<bucket>/` (`RPS-COMPS-02`).
4. **Is this React-unaware logic?** Place it in `src/utilities/` (`RPS-UTIL-01`).
5. **Is this a globally-shared type?** Place it in `src/types/` (`RPS-UTIL-01`).

Stop at the first yes. Do not skip tiers.

### `src/app/` Rules

```typescript
// ✅ GOOD: route-local components/ (no underscore)
// src/app/dashboard/components/DashboardHeader.tsx
export const DashboardHeader: FC<Props> = ({ title }) => <header>{title}</header>;

// ✅ GOOD: page.tsx as composition layer only
// src/app/dashboard/page.tsx
import { InvoiceListContainer } from '#features/billing/containers/InvoiceListContainer';
import { DashboardHeader } from './components/DashboardHeader';

export default function DashboardPage() {
  return (
    <>
      <DashboardHeader title="Dashboard" />
      <InvoiceListContainer />
    </>
  );
}

// ❌ BAD: underscore folder
// src/app/dashboard/_components/DashboardHeader.tsx

// ❌ BAD: domain logic in page.tsx
// src/app/dashboard/page.tsx
export default async function DashboardPage() {
  const invoices = await fetchInvoices();    // domain fetch in page.tsx
  return <table>{invoices.map(...)}</table>; // domain rendering in page.tsx
}
```

### `src/components/` Taxonomy

`src/components/` is for domain-agnostic UI only. Group by **capability**, not by domain or by container/presentational. No `containers/` folder here — containers live in features (`RPS-COMPS-02`).

| Bucket          | Purpose & Examples                                                                 |
|-----------------|------------------------------------------------------------------------------------|
| `primitives/`   | Atomic styled elements: `Button`, `Input`, `Badge`, `Spinner`                      |
| `layouts/`      | Structural wrappers: `PageShell`, `SidebarLayout`, `Grid`, `Stack`                 |
| `composites/`   | Primitive combinations with styled JSX: `Card`, `Modal`, `Combobox`, styled `Tabs` |
| `headless/`     | Logic-only (render-prop or hook-based): headless `Tabs`, `Disclosure`, `Listbox`   |
| `boundaries/`   | Error/Suspense boundaries: `ErrorBoundary`, `SuspenseBoundary`                     |
| `providers/`    | Context providers: `ThemeProvider`, `AppProviders`                                 |
| `adapters/`     | Third-party wrapping: `RadixTabsAdapter`, `DateAdapter`, `AnalyticsAdapter`        |

Forbidden under `src/components/`: domain-named folders (`components/billing/`), `containers/`, `components/shared/`, free-form catch-all buckets.

### `src/features/<domain>/` Layout

A feature owns one domain end-to-end and ships both data and presentation. The split is enforced (`RPS-FEAT-02`):

```plaintext
src/features/billing/
├── api/                  # fetchInvoices, createInvoice — pure data functions
│   └── fetchInvoices.ts
├── hooks/                # useInvoices, useInvoiceMutations — wrap api/
│   └── useInvoices.ts
├── containers/           # combine api/ + hooks/, fetch & orchestrate
│   └── InvoiceListContainer.tsx
├── components/           # pure presentational — prop-in, JSX-out
│   └── InvoiceRow.tsx
└── types/                # domain types
    └── Invoice.ts
```

```typescript
// ✅ GOOD: container fetches & orchestrates
// src/features/billing/containers/InvoiceListContainer.tsx
import { useInvoices } from '../hooks/useInvoices';
import { InvoiceRow } from '../components/InvoiceRow';

export const InvoiceListContainer: FC = () => {
  const { data: invoices, isLoading } = useInvoices();
  if (isLoading) return <Spinner />;
  return <ul>{invoices.map((inv) => <InvoiceRow key={inv.id} invoice={inv} />)}</ul>;
};

// ✅ GOOD: presentational — prop-in, JSX-out
// src/features/billing/components/InvoiceRow.tsx
export interface InvoiceRowProps { invoice: Invoice }
export const InvoiceRow: FC<InvoiceRowProps> = ({ invoice }) => (
  <li>{invoice.number} — {invoice.amount}</li>
);

// ❌ BAD: container/presentational mix
// src/features/billing/components/InvoiceList.tsx
export const InvoiceList: FC = () => {
  const { data } = useQuery(...);                      // fetching in components/
  return <ul className="invoice-list">{data?.map(...)}</ul>;
};
```

Cross-feature imports are forbidden (`RPS-FEAT-01`). If `billing/` and `profile/` need the same building block, promote that block to `src/components/<bucket>/` or `src/utilities/`.

### `utilities/` and `types/`

`src/utilities/` must be React-unaware (`RPS-UTIL-01`): no JSX, no hooks, no `react` imports. Helper hooks live in `src/features/<domain>/hooks/` (domain-scoped) or in a component's local hook file.

```typescript
// ✅ GOOD: pure utility
// src/utilities/formatCurrency.ts
export function formatCurrency(amount: number, currency: string): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount);
}

// ❌ BAD: hook in utilities
// src/utilities/useDebounce.ts
import { useEffect, useState } from 'react';
export function useDebounce<T>(value: T, ms: number): T { ... }
```

`src/types/` holds only globally-shared types (e.g., `ApiResponse<T>`, `Pagination`). Domain types belong in `src/features/<domain>/types/`.

### Promotion Rules

```plaintext
route-local (src/app/<route>/components/)
        │
        │ second consumer appears in the SAME domain
        ▼
src/features/<domain>/components/
        │
        │ second consumer appears in a DIFFERENT domain (and the code is domain-agnostic)
        ▼
src/components/<bucket>/
```

- Promote **only on the second real consumer**, never speculatively (`RPS-PROMO-01`).
- Demotion is allowed and encouraged: if a shared component ends up with only one consumer again, move it inward.
- "Shared by default" is an anti-pattern — it locks in coupling before the shape is proven.

### Commonly Confused Cases (FAQ)

| Question                                                                 | Resolution                                                                                                                                  |
|--------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Is `Button` a primitive or a composite?                                  | **Primitive.** Single styled element with no internal composition.                                                                          |
| Is `Combobox` a primitive or a composite?                                | **Composite.** It combines an input, a listbox, and options into one styled unit.                                                           |
| `PageShell` vs `AppProviders` — which bucket?                            | `PageShell` is a structural wrapper → `layouts/`. `AppProviders` wraps Context providers → `providers/`.                                   |
| When does a `Card` become a domain component?                            | When it knows about a specific entity's shape (e.g., `props: { invoice: Invoice }`), move it to `src/features/<domain>/components/`.        |
| Headless vs composite — which to use?                                    | Headless ships behavior and ARIA only (no styled JSX). Composite ships styled JSX. Build a headless primitive once, wrap into composites.   |
| Should this go in `src/components/adapters/`?                            | Yes if it wraps a third-party library (Radix, Headless UI, date-fns, Sentry) behind a project-local API. No if it's first-party logic.      |
| Domain type that two features share?                                     | Either lift to `src/types/` if truly cross-cutting, or designate an owner feature and let the other feature import from `<owner>/types/`.   |

### Tabs Placement — Brief

Tabs are the canonical "where does this go?" puzzle. Formula:

- **Headless Tabs primitive** → `src/components/headless/Tabs.tsx`
- **Styled wrapper for the headless primitive** → `src/components/composites/Tabs.tsx`
- **Visual variants** (pill / underline / segmented) → `src/components/composites/Tabs/variants/`
- **Feature-specific tab content** (e.g., billing settings tabs) → `src/features/billing/components/BillingTabs.tsx`
- **Page-specific tab orchestration** (one-off for one route) → `src/app/dashboard/components/DashboardTabs.tsx`
- **Third-party tabs library wrapping** (Radix, Headless UI) → `src/components/adapters/RadixTabsAdapter.tsx`

Brief decision matrix:

| Use Case                                            | Placement                                       | Why                                                              |
|-----------------------------------------------------|-------------------------------------------------|------------------------------------------------------------------|
| Pure behavior, no styled JSX                        | `src/components/headless/Tabs.tsx`              | Reused across many styled wrappers                               |
| Styled, generic, app-wide                           | `src/components/composites/Tabs.tsx`            | Domain-agnostic UI                                               |
| Visual variant of the generic Tabs                  | `src/components/composites/Tabs/variants/`      | Variant is a styling concern, not a new component                |
| Tabs whose tab list is dictated by a domain         | `src/features/<domain>/components/`             | Knows about domain shape; composes generic Tabs                  |
| Tabs only one route ever uses                       | `src/app/<route>/components/`                   | Route-local; do not pollute features or shared                   |
| Tabs driving routing (URL per tab)                  | `src/app/<section>/layout.tsx` + route-local    | Tabs are a routing concern at that layout level                  |
| Tab list fetched from API                           | feature container fetches → composite Tabs      | Container/presentational split — see `RPS-FEAT-02`               |
| Wrapping Radix/Headless UI Tabs                     | `src/components/adapters/RadixTabsAdapter.tsx`  | Quarantine third-party API surface                               |

See `references/tabs-placement.md` for the full 8-section case study.

## Anti-Patterns

- Speculative `src/components/` entries with no real second consumer (`RPS-PROMO-01`).
- `src/components/billing/` or any other domain-named bucket — domain code belongs in `features/` (`RPS-COMPS-02`).
- `containers/` under `src/components/` — containers are domain-aware and live in features (`RPS-COMPS-02`, `RPS-FEAT-02`).
- `features/shared/` or `features/ui/` as a catch-all (`RPS-FEAT-03`).
- Cross-feature imports between sibling domains (`RPS-FEAT-01`).
- `page.tsx` doing data-fetching, mutations, or styled rendering of domain shapes (`RPS-ROUTE-02`).
- `useDebounce` or any hook inside `src/utilities/` (`RPS-UTIL-01`).
- Domain types in `src/types/` (`RPS-UTIL-01`).

## Quick Decision Tree

1. **Will only one route use this?**
   - Yes → `src/app/<route>/components/` (`RPS-ROUTE-01`).
   - No → continue.
2. **Is it tied to a specific domain (e.g., billing, profile, search)?**
   - Yes → `src/features/<domain>/...`
     - Fetches/orchestrates? → `containers/` (`RPS-FEAT-02`).
     - Prop-in/JSX-out? → `components/` (`RPS-FEAT-02`).
     - Data function? → `api/`.
     - Hook over `api/`? → `hooks/`.
     - Domain type? → `types/`.
   - No → continue.
3. **Is it React UI but domain-agnostic?**
   - Yes → `src/components/<bucket>/` (`RPS-COMPS-02`):
     - Atomic styled element → `primitives/`
     - Structural wrapper → `layouts/`
     - Combined styled JSX → `composites/`
     - Logic-only, no styled JSX → `headless/`
     - Error/Suspense boundary → `boundaries/`
     - Context provider → `providers/`
     - Third-party wrapping → `adapters/`
   - No → continue.
4. **Is it React-unaware logic?**
   - Yes → `src/utilities/` (`RPS-UTIL-01`).
   - No → continue.
5. **Is it a globally-shared type?**
   - Yes → `src/types/` (`RPS-UTIL-01`).
   - No → re-check step 1; the code probably belongs route-local.

Apply first-yes-wins. Apply the second-consumer rule before promoting (`RPS-PROMO-01`).
