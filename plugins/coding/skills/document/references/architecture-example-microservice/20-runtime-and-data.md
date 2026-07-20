## 🔄 Data Flow

The sequence below shows a successful enqueue-through-ack. Producer and worker may run in the same process or on different hosts; the flow is identical.

```mermaid
sequenceDiagram
    participant Producer
    participant JobService
    participant Store as JobAdapter
    participant Broker as BrokerAdapter
    participant Worker
    participant Handler

    Producer->>JobService: enqueue(input)
    JobService->>Store: insert(job)
    Store-->>JobService: job
    JobService->>Broker: notify(jobId)
    JobService-->>Producer: job

    Broker-->>Worker: jobId
    Worker->>Store: leaseNext(workerId)
    Store-->>Worker: job
    Worker->>Handler: run(payload, context)
    Handler-->>Worker: result
    Worker->>Store: ack(job.id, 'succeeded')
    Store-->>Worker: ok
```

---

## 🔁 State & Lifecycle

Every job is modelled as a small state machine. Transitions are gated by `JobService` so the set of legal moves is centralised; adapters never mutate state directly.

```mermaid
stateDiagram-v2
    [*] --> queued
    queued --> running: worker leased
    running --> succeeded: handler resolved
    running --> retrying: handler rejected & attempts < max
    running --> failed: handler rejected & attempts == max
    retrying --> queued: backoff elapsed
    failed --> dead_letter: DLQ handler registered
    succeeded --> [*]
    failed --> [*]
    dead_letter --> [*]
```

---

## 🗃️ Data Model

The schema is four tables; there are no cross-table joins in the hot path, so every supported database reaches comparable throughput.

```mermaid
erDiagram
    JOB ||--o{ ATTEMPT : has
    JOB }o--|| HANDLER : dispatched_to
    JOB ||--o| DEAD_LETTER : terminates_as

    JOB {
        uuid id PK
        string kind
        json payload
        string status
        string idempotencyKey
        datetime runAt
        datetime createdAt
        int attemptCount
    }
    ATTEMPT {
        uuid id PK
        uuid jobId FK
        int index
        datetime startedAt
        datetime endedAt
        string error
        int durationMs
    }
    HANDLER {
        string kind PK
        int maxAttempts
        string backoff
        string schemaHash
    }
    DEAD_LETTER {
        uuid id PK
        uuid jobId FK
        datetime terminatedAt
        string reason
    }
```

---

## 🧩 Adapter Interface

Every storage adapter implements the same `JobAdapter` contract. The interface is nine methods; built-in implementations inherit from nothing, composition only.

```mermaid
classDiagram
    class JobAdapter {
        <<interface>>
        +insert(job: NewJob) Promise~Job~
        +leaseNext(workerId, visibilityMs) Promise~Job~
        +ack(id, result) Promise~void~
        +fail(id, error) Promise~void~
        +findById(id) Promise~Job~
        +findByIdempotencyKey(key) Promise~Job~
        +recordAttempt(attempt) Promise~void~
        +listDeadLetters(limit) Promise~Job[]~
        +ping() Promise~HealthReport~
    }
    class PostgresJobAdapter {
        -pool: Pool
        +insert(job) Promise~Job~
        +leaseNext(workerId, ms) Promise~Job~
    }
    class MySQLJobAdapter {
        -pool: Pool
        +insert(job) Promise~Job~
        +leaseNext(workerId, ms) Promise~Job~
    }
    class SQLiteJobAdapter {
        -db: Database
        +insert(job) Promise~Job~
        +leaseNext(workerId, ms) Promise~Job~
    }

    PostgresJobAdapter ..|> JobAdapter
    MySQLJobAdapter ..|> JobAdapter
    SQLiteJobAdapter ..|> JobAdapter
```

---
