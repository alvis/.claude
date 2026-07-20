# Specification metadata

Use separate schemas for Notion transport and durable derivation. Never copy
transport-only metadata into versioned docs without purpose.

## Notion-backed MDC

Paths are returned by notion-sync and never derived. Preserve all existing
properties; the keys below are the minimum identity/provenance surface:

```yaml
---
title: Capability contract
last_edited_time: 2026-07-20T10:30:00.000Z
ref: 01234567-89ab-cdef-0123-456789abcdef
parent: 01234567-89ab-cdef-0123-456789abcdef # only for an unsynced child
---
```

- `ref` is the stable Notion identity and never derives a local filename.
- `parent` is present only when needed to create an unsynced page.
- `last_edited_time` is stamped once after the complete MDC edit batch.
- Preserve Notion properties and relationship annotations verbatim.
- MDC is transport state and exempt from the Markdown byte gate.

## Versioned derived specification

Every `docs/specs/<capability>/*.md` file has lowercase human-owned naming and
source provenance:

```yaml
---
notion_ids:
  - 0123456789abcdef0123456789abcdef
source_revision: '2026-07-20T10:32:00.000Z'
source_hash: 'sha256:<digest>'
derived_at: '2026-07-20T10:33:00Z'
receipt_anchor: 'notion:0123456789abcdef0123456789abcdef'
---
```

- `index.md` is the capability overview and links all derived children.
- `source_hash` covers the normalized authoritative MDC source set recorded by
  the receipt; normalization and file order must be deterministic.
- `receipt_anchor` points to the durable owning task, pull request, or Notion
  work item that records completion. It must remain resolvable after ignored
  local work state is retired.
- The local derivation receipt lists every source ref/path/revision/hash and
  every output path, but its ignored path is recorded only in `state.md`; never
  embed that expiring path in versioned documentation.
- Derived filenames use Essential's `derive-engineering-name` executable, never the Notion
  mirror filename.
- The PM's final output manifest includes all derived `.md` files for the one
  end-of-run size check.
