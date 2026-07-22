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
- `last_edited_time` is remote revision metadata returned and updated only by
  Notion transport. Local MDC authoring preserves it byte-for-byte and never
  replaces it with a local clock. An unsynced locally authored page omits this
  key until transport supplies it.
- Local edit timestamps belong in ignored work evidence or the sync receipt,
  never in Notion-backed MDC frontmatter.
- Preserve Notion properties and relationship annotations verbatim.
- MDC remains transport state and is edited only through its owning workflow.

## Versioned contract carrier and provenance

`docs/specs/<capability>/index.md` is the reachable capability entry and links
all derived children. Promotion preserves the source contract's semantic
frontmatter and body; it does not inject source, timestamp, receipt, or hash
fields into contract Markdown. If a selected project/template already requires
frontmatter, those bytes are semantic and are compared directly as part of the
contract (disregarding only the volatile Notion `last_edited_time` line). Put
derivation metadata in `docs/specs/<capability>/provenance.json` instead:

```json
{
  "schema": "specification-provenance-v1",
  "source_kind": "local",
  "source_locators": ["repo:requirements/capability.md"],
  "source_revision": "<git-blob-oid-or-notion-revision-or-empty>",
  "carrier_revision": "<git-blob-oid-or-empty>",
  "approved_content_ref": "<durable reachable locator to the exact approved specification content>",
  "logical_units": [
    {"id": "contract:root", "source_path": "requirements/capability.md", "output_path": "docs/specs/capability/index.md"}
  ],
  "outputs": [
    {"path": "docs/specs/capability/index.md", "exact_sha256": "sha256:<64-lowercase-hex>"}
  ],
  "template": {"locator": "plugin:specification/spec-code/assets/technical-spec-template.md", "plugin_version": "<exact-installed-version>", "exact_sha256": "sha256:<64-lowercase-hex>"},
  "derived_at": "2026-07-20T10:33:00Z",
  "receipt_anchor": "github-pr:owner/repository#123"
}
```

- `source_kind` is exactly `notion`, `local`, or `inline`.
- `source_locators` contains only durable, portable identifiers. Use
  `notion:<page-uuid>` for Notion, `repo:<repository-relative-path>` for a
  reachable local source, and `inline-approved:sha256:<exact-byte-hash>` for an
  inline-approved candidate. Never publish an absolute local path, an ignored
  work path, or a conversation/prompt locator. If an explicit local source is
  not itself durable, use `local-approved:sha256:<exact-byte-hash>` and treat
  the promoted carrier as the reachable authority.
- Authority has one deterministic interpretation. A reachable `repo:` locator
  remains the live authority and the durable carrier is a checked derivation;
  plan/implementation compare both content directly before use. For
  `local-approved:` and `inline-approved:` locators, the content-equivalent
  durable carrier becomes the sole reachable authority after promotion, while
  the locator remains historical origin evidence. Never treat both an
  unreachable origin and its carrier as independently editable truths.
- `source_revision` and `carrier_revision` are lightweight change signals (a Git
  blob oid or Notion revision). Authority is the specification content itself:
  approval, plan, and review bind to it and are confirmed by direct comparison,
  not by any recorded hash.
- `approved_content_ref` is a durable, reachable pointer to the exact approved
  specification content — not a hash — so `implement-code` and
  `review-implementation` can confirm a resumed spec still matches by direct
  content comparison. For a reachable `repo:` source it is that source path; for
  `local-approved:` and `inline-approved:` origins whose origin is not reachable,
  it is the promoted durable carrier (`docs/specs/<capability>/index.md`) that
  retains the approved content, or an external durable receipt/anchor holding it.
  It is required for local and inline sources and must resolve after ignored
  local work is retired. A Notion source uses `ref` plus per-unit
  `source_revision` and omits this field.
- Notion provenance additionally records exact per-unit `source_revision`
  values and may record transport relationships. Local provenance may record a
  reachable Git object. Inline provenance omits source revision. Neither local
  nor inline provenance requires a Notion id, page revision, or Notion receipt.
- `logical_units` preserves the source logical ids in the output carrier, so a
  renamed derived path cannot silently remap semantic units.
- The bundled fallback template uses the stable
  `plugin:specification/spec-code/assets/technical-spec-template.md` locator,
  exact installed plugin version, and exact asset SHA-256. Never record the
  origin machine's plugin cache/install path. Explicit/project templates use a
  durable `repo:` or selected remote locator instead.
- `outputs` lists contract Markdown files only and **must exclude
  `provenance.json` itself**. Compute the provenance file's own exact SHA-256
  only after its final write; store that self-hash in ignored work evidence, an
  external durable receipt/anchor, and the run report. Never insert the
  self-hash into the file it hashes.
- `receipt_anchor` points to the durable owning task, pull request, repository
  record, or Notion work item that records completion. It remains resolvable
  after ignored local work is retired. Only ignored work evidence may contain
  temporary absolute source or receipt paths.
- Derived filenames use Essential's `derive-engineering-name` executable,
  never the Notion mirror filename.
- The PM's final output manifest includes all derived `.md` files and
  `provenance.json` in `generated_files`; versioned `docs/**` remains excluded
  from the final size check, which selects only eligible Markdown inside
  `.engineering/`.
