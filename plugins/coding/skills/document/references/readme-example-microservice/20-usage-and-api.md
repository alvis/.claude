## 📖 Usage

### Example: Enqueue a job from an HTTP handler

Producers talk to the queue through `JobClient`, which validates the payload against the registered handler's schema and writes the job durably before returning.

```ts
import { createJobClient } from '@theriety/queue-worker';
import { postgresAdapter } from '@theriety/adapter-postgres';

const jobs = createJobClient({
  store: postgresAdapter({ url: process.env.QUEUE_DB_URL! }),
});

await jobs.enqueue({
  kind: 'send-email',
  payload: { to: 'alice@example.com', subject: 'Welcome' },
  idempotencyKey: `welcome:${userId}`,
  runAt: new Date(Date.now() + 60_000),
});
```

### Example: Register a typed handler with backoff

Handlers are registered once at startup; the type of `payload` is inferred from the Zod schema passed to `defineJob`, so producers and consumers cannot drift.

```ts
import { createWorker, defineJob } from '@theriety/queue-worker';
import { postgresAdapter } from '@theriety/adapter-postgres';
import { z } from 'zod';

const sendEmail = defineJob({
  kind: 'send-email',
  schema: z.object({ to: z.string().email(), subject: z.string() }),
  retry: { maxAttempts: 5, backoff: 'exponential' },
});

const worker = createWorker({
  store: postgresAdapter({ url: process.env.QUEUE_DB_URL! }),
  broker: 'memory',
});

worker.register(sendEmail, async ({ payload, attempt }) => {
  await fetch('https://mail.example.com', {
    method: 'POST',
    body: JSON.stringify({ ...payload, attempt }),
  });
});

await worker.start();
```

### Example: Health check endpoint for Kubernetes

The worker exposes a lightweight HTTP probe suitable for liveness and readiness checks; a failing adapter fails the probe so the pod is restarted or removed from the service pool.

```ts
import { createWorker } from '@theriety/queue-worker';
import { postgresAdapter } from '@theriety/adapter-postgres';
import { createServer } from 'node:http';

const worker = createWorker({
  store: postgresAdapter({ url: process.env.QUEUE_DB_URL! }),
  broker: process.env.QUEUE_BROKER_URL!,
});

await worker.start();

createServer(async (_req, res) => {
  const health = await worker.health();
  res.statusCode = health.status === 'ok' ? 200 : 503;
  res.setHeader('content-type', 'application/json');
  res.end(JSON.stringify(health));
}).listen(8080);
```

---

## 📚 API Reference

### HTTP Endpoints

The admin HTTP surface is disabled by default and must be opted in via `worker.admin({ port })`. The table below lists every endpoint the worker exposes when enabled.

| Method | Path | Purpose | Request Body | Response |
| --- | --- | --- | --- | --- |
| `POST` | `/jobs` | enqueue a new job (alternative to `JobClient.enqueue`) | `{ kind, payload, idempotencyKey?, runAt? }` | `201 { id, status }` |
| `GET` | `/jobs/:id` | fetch the current state of a job including its attempt history | — | `200 { id, status, attempts[] }` |
| `GET` | `/health` | liveness + readiness probe; checks adapter connectivity | — | `200 { status: 'ok' }` or `503 { status, failing[] }` |
| `POST` | `/admin/drain` | stop pulling new jobs and drain in-flight handlers with the configured grace window | `{ graceMs?: number }` | `202 { draining: true }` |

### Core Functions

<details>
<summary><code>createWorker(config: WorkerConfig): Worker</code></summary>

**Description:**
Constructs a `Worker` bound to the chosen adapters. Does not open connections until `.start()` is called, so tests can assert configuration eagerly without side effects.

**Parameters:**

- `config` (`WorkerConfig`): the store adapter, broker adapter (or `'memory'`), concurrency, and shutdown grace window

**Returns:**

- `Worker`: exposes `register`, `start`, `drain`, `health`, and `admin`

**Example:**

```ts
import { createWorker } from '@theriety/queue-worker';
import { postgresAdapter } from '@theriety/adapter-postgres';

const worker = createWorker({
  store: postgresAdapter({ url: process.env.QUEUE_DB_URL! }),
  broker: 'memory',
});
```

</details>

<details>
<summary><code>defineJob&lt;S extends ZodSchema&gt;(spec: JobSpec&lt;S&gt;): JobDefinition&lt;S&gt;</code></summary>

**Description:**
Declares a job `kind` with its payload schema and retry policy. The returned definition is shared between producer and consumer so payload types cannot drift.

**Parameters:**

- `spec.kind` (`string`): globally unique job name; becomes the discriminator in the `jobs` table
- `spec.schema` (`ZodSchema`): validates the payload at both enqueue and execute time
- `spec.retry` (`RetryPolicy`, optional): maximum attempts and backoff shape; defaults to 5 attempts, exponential

**Returns:**

- `JobDefinition<S>`: value passed to both `JobClient.enqueue` and `Worker.register`

</details>

---
