# @theriety/queue-worker

> README = how to run it. For design rationale, see [`docs/architecture/durable-job-worker.md`](./docs/architecture/durable-job-worker.md).

<br/>

📌 A horizontally-scalable background job runner for TypeScript services that turns ad-hoc cron scripts and in-process `setInterval` loops into a uniform, observable work queue. It solves the "background job drift" problem: every team writes their own half-correct worker with different retry semantics, different idempotency stories, and different ways to drain safely during deploys.

The `@theriety/queue-worker` package centres job execution around a **pluggable adapter pair** — one `JobAdapter` for durable storage (Postgres / MySQL / SQLite) and one `BrokerAdapter` for dispatch (Redis / RabbitMQ / in-memory) — driven by a small hexagonal core. Compared to BullMQ it is broker-agnostic and ships a Postgres-only mode for teams who do not want a Redis dependency; compared to Agenda it exposes the adapter contract as a first-class extension seam so new stores can land in under 200 lines.

<br/>
<div align="center">

•&emsp;&emsp;💡 [Concept](#-core-concept)&emsp;&emsp;•&emsp;&emsp;🚀 [Start](#-quick-start)&emsp;&emsp;•&emsp;&emsp;🔑 [Env](#-environment-variables)&emsp;&emsp;•&emsp;&emsp;📖 [Usage](#-usage)&emsp;&emsp;•&emsp;&emsp;📚 [API](#-api-reference)&emsp;&emsp;•&emsp;&emsp;📐 [Arch](#-architecture)&emsp;&emsp;•

</div>
<br/>

---

## 💡 Core Concept

The worker is a **hexagonal runtime** (`ports & adapters`): the domain core owns job lifecycle rules, and every I/O concern is a pluggable port. Every job flows through the same five phases in the same order, so observability, retries, and draining are uniform across adapters:

1. **Enqueue** (via `JobService.enqueue`) so that a job is persisted with an `idempotencyKey` before a broker ever sees it — the queue survives a broker outage
2. **Dispatch** (via `Worker.pullNext`) so that the broker hands back one job at a time with a visibility lease; in-memory mode short-circuits directly through the `JobAdapter`
3. **Execute** (via `HandlerRegistry.run`) so that the registered handler for the job `kind` runs with a typed payload and a structured `JobContext`
4. **Acknowledge** (via `JobService.ack`) so that success marks the job `succeeded` and failure records an `Attempt` before the retry policy decides the next state
5. **Drain** (via `Worker.drain`) so that `SIGTERM` stops new pulls and waits for in-flight handlers to finish within a bounded grace period

Because storage and dispatch are decoupled, you can run a Postgres-backed queue with no broker at all (polling mode), or pair Postgres with RabbitMQ for low-latency dispatch, or run an in-memory adapter for tests — the handler code does not change. The deeper rationale and diagrams live in [`docs/architecture/durable-job-worker.md`](./docs/architecture/durable-job-worker.md).

---

## 🔑 Environment Variables

The worker reads its configuration from the process environment so that the same binary runs in every stage without rebuilds. All values are validated at boot; an invalid value aborts startup with a descriptive error.

- `QUEUE_DB_URL`: connection string for the chosen `JobAdapter` (e.g. `postgres://user:pass@host/db`); required
- `QUEUE_BROKER_URL`: connection string for the `BrokerAdapter`; set to `memory://` to disable broker dispatch and fall back to DB polling
- `QUEUE_CONCURRENCY`: maximum number of handlers to run in parallel per worker process; defaults to `8`
- `QUEUE_POLL_INTERVAL_MS`: DB polling interval when running without a broker or when recovering stuck jobs; defaults to `2000`
- `QUEUE_VISIBILITY_MS`: lease duration for an in-flight job before it becomes visible again; defaults to `60000`
- `QUEUE_SHUTDOWN_GRACE_MS`: maximum wait during drain before in-flight handlers are cancelled; defaults to `30000`
- `QUEUE_LOG_LEVEL`: log verbosity (`trace|debug|info|warn|error`); defaults to `info`
- `QUEUE_METRICS_PORT`: Prometheus scrape port; set to `0` to disable; defaults to `9090`
- `QUEUE_WORKER_ID`: unique worker identifier surfaced in logs and metrics; defaults to `hostname`

---

## 🚀 Quick Start

Install the package and run the bundled migrations against the target database, then start the worker with a minimal configuration.

```bash
npm install @theriety/queue-worker @theriety/adapter-postgres
npx queue-worker migrate --url "$QUEUE_DB_URL"
npx queue-worker start
```

For a code-first startup — which is the recommended path in most services — register handlers and start the worker from your own entrypoint:

```ts
import { createWorker } from '@theriety/queue-worker';
import { postgresAdapter } from '@theriety/adapter-postgres';

const worker = createWorker({
  store: postgresAdapter({ url: process.env.QUEUE_DB_URL! }),
  broker: 'memory',
  concurrency: 8,
});

worker.register('send-email', async (payload: { to: string }) => {
  await fetch('https://mail.example.com', { method: 'POST', body: JSON.stringify(payload) });
});

await worker.start();
```

---
