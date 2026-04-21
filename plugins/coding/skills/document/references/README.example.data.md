# @theriety/data-billing

<br/>

📌 A CRUD orchestrator for billing data: accounts, invoices, purchases, payment methods, and the ledger. It wraps a single Prisma schema behind a small set of domain-shaped operations so that the service layer never reaches for the Prisma delegate directly. This keeps billing business rules out of transport code and guarantees referential integrity at the data boundary.

The `@theriety/data-billing` package is **Prisma-first**: the `prisma/schema.prisma` file is the source of truth, and every model is wrapped by a repository class under `src/prisma/models`. Operations under `src/operations` are verb-noun files that compose one-to-many model calls into an atomic unit — multi-row writes always run inside `prisma.$transaction`, single-row writes use `upsert`. There is no caching layer and no message bus; if the caller needs a list, they get it from the database, full stop.

<br/>
<div align="center">

•&emsp;&emsp;💡 [Concept](#-core-concept)&emsp;&emsp;•&emsp;&emsp;🔑 [Env](#-environment-variables)&emsp;&emsp;•&emsp;&emsp;🗄️ [Objects](#-data-objects)&emsp;&emsp;•&emsp;&emsp;🔧 [Ops](#-operations)&emsp;&emsp;•&emsp;&emsp;📖 [Usage](#-usage)&emsp;&emsp;•&emsp;&emsp;📐 [Arch](#-architecture)&emsp;&emsp;•

</div>
<br/>

---

## 💡 Core Concept

A data controller is a **Prisma-first orchestrator**. `@theriety/data-billing` exposes a `createBilling(config)` factory that returns a bound orchestrator — operations are methods on the instance, configuration is injected once. The instance knows the shape of the domain data and exposes operations named after domain verbs (`initiatePaymentAccount`, `attachPaymentMethod`); it does not know — and refuses to know — why the caller wants the result. Business rules live in the service layer; this package owns persistence semantics only.

- **One schema**: every model is defined once in `prisma/schema.prisma`; there is no parallel DTO hierarchy
- **Model class per entity**: each delegate (`prisma.paymentAccount`, `prisma.invoice`, …) is wrapped in `src/prisma/models/<Entity>.ts` with domain-aware finders and guards
- **Operation per verb**: each file under `src/operations/<verb-noun>.ts` is a single atomic unit — it either succeeds or leaves the database untouched
- **No business logic**: validation of *domain rules* ("is this customer allowed to pay?") happens upstream; this package validates only referential and transactional invariants

The deeper rationale and the full ER diagram live in the sibling [`ARCHITECTURE.md`](./ARCHITECTURE.md).

---

## 🔑 Environment Variables

Configuration comes from the environment and is validated at boot. Invalid or missing required values abort startup with a descriptive error.

- `BILLING_DATABASE_URL`: primary connection string (Postgres); required
- `BILLING_READ_REPLICA_URL`: optional read-replica connection; when set, read operations are routed here
- `PRISMA_LOG_LEVEL`: one of `query`, `info`, `warn`, `error`; defaults to `warn`
- `BILLING_MIGRATION_LOCK_MS`: advisory-lock timeout for `prisma migrate deploy`; defaults to `30000`

---

## 🗄️ Data Objects

The schema contains six models and five relations. The table below is the canonical summary; the full ER diagram is in `ARCHITECTURE.md`.

| Model | Purpose | Key fields |
| --- | --- | --- |
| `PaymentAccount` | holds a customer's billing identity | `id`, `spaceId`, `providerCustomerId`, `status` |
| `Invoice` | a single billable document | `id`, `accountId`, `amount`, `status`, `dueAt` |
| `Purchase` | line-item on an invoice | `id`, `invoiceId`, `sku`, `quantity`, `unitPrice` |
| `PaymentMethod` | tokenized card/bank attached to an account | `id`, `accountId`, `providerToken`, `brand`, `last4` |
| `Transaction` | ledger entry for a successful/failed charge | `id`, `accountId`, `amount`, `status`, `occurredAt` |
| `Space` | tenant boundary for multi-tenant billing | `id`, `slug`, `plan` |

---

## 🔧 Operations

Operations are thin wrappers over Prisma calls. Each is atomic, typed, and throws a domain-specific error on violation — callers never see a raw Prisma error.

| Operation | Inputs | Returns | Throws |
| --- | --- | --- | --- |
| `initiate-payment-account` | `{ spaceId, provider }` | `PaymentAccount` | `AccountAlreadyExists` |
| `list-purchases` | `{ accountId, from?, to? }` | `Purchase[]` | `AccountNotFound` |
| `set-purchase` | `{ id?, invoiceId, sku, quantity, unitPrice }` | `Purchase` (upsert) | `InvoiceLocked` |
| `attach-payment-method` | `{ accountId, providerToken }` | `PaymentMethod` | `DuplicateToken` |
| `detach-payment-method` | `{ methodId }` | `void` | `MethodInUse` |

---

## 📖 Usage

### Example: Initiate a payment account from a service

The service layer calls the operation directly; the controller opens its own transaction so the caller never reasons about boundaries.

```ts
import { createBilling } from '@theriety/data-billing';

const billing = createBilling({
  databaseUrl: process.env.BILLING_DATABASE_URL!,
});

const account = await billing.initiatePaymentAccount({
  spaceId: 'space_42',
  provider: 'stripe',
});

console.log(account.id, account.status);
```

### Example: List purchases within a date range

Read operations are automatically routed to the read-replica when `BILLING_READ_REPLICA_URL` is set; the caller sees no difference.

```ts
import { createBilling } from '@theriety/data-billing';

const billing = createBilling({
  databaseUrl: process.env.BILLING_DATABASE_URL!,
});

const purchases = await billing.listPurchases({
  accountId: 'acct_1',
  from: new Date('2026-04-01'),
  to: new Date('2026-04-30'),
});

console.log(`${purchases.length} purchases in range`);
```

---

## 📐 Architecture

A Prisma-first data controller: model classes under `src/prisma/models` wrap Prisma delegates, and verb-noun operation files under `src/operations` compose them into atomic units.

```plain
src
├── prisma        # client singleton + model classes
├── operations    # verb-noun operation files
├── types         # shared domain types (no runtime)
└── index.ts
```

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the ER diagram, transaction lifecycle, and extension guidance.

---

## 📦 Related Packages

- `@prisma/client`: generated client used by every model class
- [`@theriety/data-common`](../data-common): shared pagination and filter types consumed by every data controller

---
