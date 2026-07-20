## 🧰 Support Matrix

The worker is only as capable as the adapter pair you plug in. The matrix below is the authoritative feature map for every first-party adapter shipped in this repo. Adapters published separately should include their own row in their README and link back here.

| Adapter | Batch processing | Streaming | Transactional | Delay support | Priority queue |
| --- | --- | --- | --- | --- | --- |
| `@theriety/adapter-postgres` | ✅ | ⚠️ via `LISTEN/NOTIFY` | ✅ | ✅ | ✅ |
| `@theriety/adapter-mysql` | ✅ | ❌ | ✅ | ✅ | ⚠️ single-tier only |
| `@theriety/adapter-sqlite` | ⚠️ single-writer | ❌ | ✅ | ✅ | ❌ |
| `@theriety/adapter-redis-broker` | ✅ | ✅ | ❌ | ✅ | ✅ |
| `@theriety/adapter-rabbitmq-broker` | ✅ | ✅ | ⚠️ publisher confirms | 🔜 | ✅ |
| `@theriety/adapter-memory-broker` | ✅ | ✅ | ✅ | ✅ | ✅ |

Legend: ✅ supported &nbsp; ⚠️ partial &nbsp; ❌ unsupported &nbsp; 🔜 planned

---

## 📐 Architecture

A hexagonal runtime: a domain core (`src/domain`) drives every job, with storage and dispatch swapped behind `JobAdapter` / `BrokerAdapter` ports (`src/adapters`); `src/worker` owns the pull loop and draining.

See [`docs/architecture/durable-job-worker.md`](./docs/architecture/durable-job-worker.md) for adapter contracts, deployment topology, and state machine.

---

## 📦 Related Packages

- [`@theriety/queue-client`](../queue-client): browser-and-server-safe client for enqueuing jobs without pulling in the worker runtime — use this from edge functions and HTTP handlers
- [`@theriety/adapter-postgres`](../adapter-postgres): first-party `JobAdapter` implementation backed by `pg`; the recommended default for most teams
- [`@theriety/adapter-redis-broker`](../adapter-redis-broker): first-party `BrokerAdapter` backed by Redis streams; pairs with any `JobAdapter`
- [`@theriety/retry`](../retry): underlying retry engine reused for attempt scheduling and classifier logic

---

## ❓ FAQ

**Q: How does the admin HTTP surface authenticate callers?**
A: The admin surface is disabled by default; `worker.admin({ port })` accepts a `verify(req)` hook that returns the caller identity or rejects the request. In our reference deployment, the hook validates a short-lived service-to-service JWT minted by the platform's auth gateway — the worker itself never sees long-lived credentials. `/health` is the only endpoint exempt from the hook so liveness probes do not need a token; `/jobs`, `/jobs/:id`, and `/admin/drain` all require a valid principal.

**Q: Are there rate limits on `JobClient.enqueue` or the `POST /jobs` endpoint?**
A: The worker does not impose a fixed RPS limit; throughput is gated by the `JobAdapter` write path (for `@theriety/adapter-postgres`, that is a single `INSERT ... RETURNING`). In practice we recommend callers keep enqueue concurrency below `QUEUE_CONCURRENCY` on the writer side, and lean on the broker's backpressure — `@theriety/adapter-redis-broker` will reject enqueues once its stream depth exceeds the configured high-water mark, surfacing as a typed `QueueBackpressureError`.

**Q: When is the `idempotencyKey` required and how is it enforced?**
A: It is optional but strongly recommended for anything triggered from an HTTP handler or webhook. When present, the store enforces a unique constraint over `(kind, idempotencyKey)`; a duplicate enqueue returns the existing job rather than creating a second row, so retried producers cannot double-dispatch. The key is also surfaced in structured logs and in the `attempts[]` response so operators can trace a user action through every retry.

**Q: How do correlation IDs flow through the five-phase lifecycle?**
A: Every `JobContext` exposes a `traceId` and `spanId` derived from the enqueue-time headers (W3C `traceparent` if present, otherwise a fresh ULID). The same IDs are stamped on every log line emitted during execute, on the `Attempt` row written at ack, and on Prometheus exemplars attached to the `queue_job_duration_seconds` histogram — so a single request ID can be followed from the producer through every retry without bespoke glue.

**Q: What is the versioning policy for job kinds and payload schemas?**
A: Job kinds are part of the public API — renaming one is a breaking change. To evolve a payload, bump the `kind` (e.g. `send-email` → `send-email.v2`) and register both handlers during the transition; `defineJob` uses the Zod schema passed in, so old in-flight jobs keep validating against the old schema while new enqueues use the new one. We follow semver at the package level: adapter changes that alter on-disk layout are major bumps and ship with a `npx queue-worker migrate` step.

---

## 🛠️ Troubleshooting

- **Worker aborts at boot with an env-validation error** — every `QUEUE_*` variable is validated at startup; an invalid value (unparseable URL, non-numeric `QUEUE_CONCURRENCY`, missing `QUEUE_DB_URL`) exits non-zero with a descriptive message pointing at the offending key. Re-check the variable against the [Environment Variables](#-environment-variables) list, and remember that `QUEUE_BROKER_URL=memory://` is required — not "empty" — to disable broker dispatch.
- **`EADDRINUSE` on the metrics port or admin port** — `QUEUE_METRICS_PORT` defaults to `9090` and the admin server takes whatever you passed to `worker.admin({ port })`. In local dev a prior worker process or a stray Prometheus scraper often holds the port. Either set `QUEUE_METRICS_PORT=0` to disable metrics scrape entirely, pick a free port, or kill the holder with `lsof -i :9090`.
- **`/health` returns 503 with `failing: ['broker']` or `failing: ['store']`** — the probe reports the adapter that failed its connectivity check. For the Postgres store this usually means the `pg` pool cannot reach the DB (check `QUEUE_DB_URL`, security group, SSL mode); for the Redis broker it usually means TLS or AUTH mismatch. The worker keeps pulling queued jobs via DB polling while the broker is unhealthy, so `/health` flipping to 503 does not imply a full outage — it is a readiness signal for the load balancer.
- **Postgres connection pool exhaustion (`timeout exceeded when trying to connect`)** — the default `pg` pool is 10 connections per worker; a high `QUEUE_CONCURRENCY` plus a long-running handler can starve enqueue calls. Either lower `QUEUE_CONCURRENCY`, raise the pool size via the adapter's `pool: { max }` option, or move read-only queries off the worker's pool. Our standard alarm fires when `pg_pool_waiting` stays above zero for more than 60 seconds — that is the early warning before requests start timing out.

---
