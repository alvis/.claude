# Specification hash model

Load this reference whenever a specification is materialized, approved,
planned, reviewed, derived, reconciled, or published. Two hashes are required;
they are not interchangeable.

## Sole implementation

Run the bundled read-only helper through the skill's allowed Bash tool:

```bash
python3 <sync-spec-skill-root>/scripts/spec-hashes.py \
  --root <absolute-carrier-root> \
  --manifest <absolute-input-manifest.json> \
  --kind both
```

This helper is the sole implementation of the hash model. Do not reproduce its
algorithm with `jq`, shell text filters, an LLM rewrite, a YAML parser, or an
unversioned external tool. It uses only Python's standard library, never writes
carrier or manifest bytes, emits canonical JSON to stdout, and returns 2 on an
invalid or ambiguous input. If `python3` or the helper is unavailable, return
`refused`; do not substitute a different hash.

`--kind transport` and `--kind semantic` exist for independent verification,
but every base, approval, reconciliation, derivation, and publication run uses
`--kind both` and stores both results.

## Hashes and their owners

- **Transport manifest hash** (`transport_manifest_hash`) proves the exact
  bytes, stable source identity, selected path, and observed revision for every
  carrier unit. It protects immutable bases, transport integrity, remote
  rechecks, and conditional writes. A change to any accepted byte or framed
  field changes this hash.
- **Semantic contract digest** (`contract_digest`) identifies the contract that
  people approve and that plans and reviews consume. It excludes only the
  uniquely validated volatile metadata line declared below; every other
  frontmatter and body byte remains semantic. Specification approval records
  `approved_contract_digest`; plan approval records its consumed
  `contract_digest`; implementation review records that same value as
  `reviewed_spec_hash` for compatibility.

Never call either value merely `content_hash`, `source_hash`, or `hash` in a
receipt. Legacy `reviewed_spec_hash` is permitted only with
`hash_kind: semantic_contract_digest_v1` beside it.

## Strict input manifest and containment

Create a temporary, ignored input JSON object with exactly this schema; reject
unknown or duplicate JSON keys:

```json
{
  "schema": "spec-hash-input-v1",
  "units": [
    {
      "carrier_kind": "notion-mdc",
      "stable_transport_identity": "notion:0123456789abcdef0123456789abcdef",
      "logical_contract_unit_id": "notion:0123456789abcdef0123456789abcdef",
      "path": "selected/root-page.mdc",
      "observed_revision": "2026-07-20T10:30:00.000Z",
      "semantic_lineage": "notion"
    }
  ]
}
```

Allowed carrier kinds are `notion-mdc`, `local-markdown`, `inline-markdown`,
and `derived-markdown`. A derived unit retains its source
`semantic_lineage` (`notion`, `local`, or `inline`) and source logical unit id.
Use the normalized `notion:<32-lowercase-hex-ref>` identity for Notion,
`repo:<portable-relative-source-path>` for reachable local,
`local-approved:sha256:<exact-source-byte-sha256>` for a non-versioned local
source, and
`inline-approved:sha256:<exact-candidate-byte-sha256>` for inline. A Notion
unit requires its exact fresh-pull revision; a non-Notion unit uses a recorded
content-derived Git blob oid or the empty string. Compute that blob oid from the
exact file bytes even before commit; never use commit/index presence or a
repository commit oid, so saving unchanged bytes cannot alter the manifest.

The helper requires one absolute non-symlink root and canonical `/`-separated
relative paths beneath it. It rejects absolute/dot/backslash paths, symlink
components, non-regular files, path escapes, duplicate paths, duplicate stable
identities, duplicate logical ids, implicit Unicode normalization, UTF-8 BOM,
NUL, CR/mixed line endings, and invalid/non-round-tripping UTF-8. LF is the sole
line separator. The presence or absence of the final LF remains significant.

## Exact transport manifest v1

For reproducibility, `frame(x)` is the eight-byte unsigned big-endian length of
byte string `x` followed by `x`; counts are unsigned eight-byte big-endian
integers. The helper sorts units by raw UTF-8 stable-identity bytes, then path,
and hashes this byte sequence with SHA-256:

1. exact ASCII `spec-transport-manifest-v1\n`;
2. unit count;
3. for each unit, framed carrier kind, stable transport identity, portable
   relative path, observed revision, and **exact full file bytes**.

The output is `transport_manifest_hash`, rendered as `sha256:` plus 64
lowercase hex characters. The immutable base stores the same exact full bytes;
its receipt stores the framed fields, per-file exact SHA-256, and aggregate
manifest hash. The observed remote revision and exact pulled bytes used for
comparison must be those used by a conditional update or immediate pre-push
recheck. A semantic digest is never CAS evidence.

## Semantic contract digest v1

Each source unit has a unique `logical_contract_unit_id` recorded in the first
receipt and preserved by every derivation. A manifest has one semantic lineage;
mixing lineages is invalid. A Notion unit's logical id must exactly equal its
normalized `notion:<32hex>` identity. A single-file local or inline contract
must use `contract:root`. Every unit in a multi-file local/inline contract must
use `contract-unit:<portable-relative-unit-path>`. The same portable path rules
apply to that suffix. A missing, duplicate, malformed, or remapped id is
invalid.

For local and inline lineages, semantic projection is the complete exact file
bytes; no frontmatter key is ignored. For a Notion lineage, the helper requires
frontmatter to open at byte zero with exact `---\n` and close at the first later
exact `---\n` line. Within those delimiters it recognizes only a column-zero,
unquoted, single-line `last_edited_time:` key. Zero occurrences remove nothing;
one occurrence is removed including its LF; duplicates, an empty value, or a
YAML block scalar (`|`/`>`) are invalid. Quoted, indented, nested, differently
spelled, or other metadata remains byte-for-byte semantic rather than being
guessed away. Thus **only** the declared and uniquely validated volatile
transport line can be excluded, without requiring YAML parsing.

The helper sorts units by raw UTF-8 logical-id bytes and hashes:

1. exact ASCII `spec-semantic-contract-v1\n`;
2. unit count;
3. for each unit, framed logical id and framed semantic-projection bytes.

The output is `contract_digest`, in the same `sha256:<lowercase-hex>` form. A
manifest, containment, encoding, identity, or volatile-line ambiguity is a
refusal, never permission to fall back to whole-file or line-oriented hashing.

## Classification and receipts

Compare B/L/R semantically for authoring decisions and exactly for transport
evidence:

- A changed `transport_manifest_hash` with the same `contract_digest` is only a
  **candidate** for `metadata_only`. Compare every helper unit and require the
  same carrier kind, stable transport identity, logical contract unit id, path,
  and `semantic_projection_sha256`; the only permitted differences are
  `observed_revision` and exact file bytes whose sole projection difference is
  the uniquely validated `last_edited_time` line. Only then classify
  `metadata_only`. It does not invalidate specification approval, plan
  approval, code, or review, but still requires a fresh verification pull and a
  new immutable exact base/receipt before the remote revision or transport
  bytes become current.
- A verified path/layout change with stable identities and carrier kinds intact
  is `structural_change`, not metadata-only. A path rename is contract-relevant
  revalidation even when exact content and `contract_digest` happen to remain
  equal. It invalidates approval, plan, code alignment, and review; transport
  may promote it only through the explicit structural-change matrix row. A
  carrier-kind, stable-identity, or logical-id shift is invalid evidence and
  refuses rather than being promoted as a structural rename.
- A changed `contract_digest` is a contract change even when a transport
  timestamp did not move. It invalidates every approval, plan, code alignment,
  and review bound to the former digest.
- Never hide an identity, path, encoding, containment, or stable-frontmatter
  change as metadata-only. Those differences are semantic, structural and
  revalidation-requiring, or invalid evidence.

Every immutable materialization/publication receipt records
`hash_model: specification-dual-hash-v1`, B/L/R transport manifest hashes,
B/L/R contract digests, per-unit identities/revisions/exact file hashes and
semantic projection hashes, the fixed volatile-key policy, helper path/hash,
and resulting classification. Reports expose both hashes. State may point to a
receipt but must not restate one hash without the other.

The receipt for the newly current immutable Base also exposes its own
`transport_manifest_hash` and `contract_digest` as paired top-level fields next
to `hash_model`. These duplicate only the explicitly identified current-Base
entry and must equal it; portable B/L transfer validation uses the top-level
pair to reject a stale or unrelated receipt without guessing among historical
B/L/R fields.

Identify the helper portably as
`plugin:specification/sync-spec/scripts/spec-hashes.py` with the exact installed
Specification plugin version and helper-file SHA-256. Never publish an origin
machine's absolute plugin installation/cache path.

For filesystem paths, use `transport_manifest_key`, the 64 lowercase hex
suffix of `transport_manifest_hash`, without the `sha256:` prefix. Bases live
at `bases/<transport_manifest_key>/` and receipts at
`materializations/<transport_manifest_key>.json`; the receipt/report still
stores the full prefixed hash. This avoids a colon in portable filenames.

`docs/specs/<capability>/provenance.json` records source hashes and the exact
hashes of contract output files. Its embedded output set **excludes
`provenance.json` itself**. The provenance file's own exact SHA-256 is computed
after writing it and stored only in ignored work evidence, an external durable
receipt/anchor, and the run report; it is never inserted into the file it
hashes.
