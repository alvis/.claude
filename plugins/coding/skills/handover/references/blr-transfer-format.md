# Portable Notion Base/Local transfer v1

Use this contract whenever a Notion handover cannot safely resume from a fresh
remote fetch alone. The sole packer/validator is
`../scripts/blr-transfer.py`; do not synthesize this package with shell, an LLM,
an archive tool, or a generic JSON formatter.

## Invocation

Resolve the Specification plugin's bundled `sync-spec/scripts/spec-hashes.py`
for the current installation and pass its absolute path only as an invocation
argument. Neither helper path is stored in the package.

```bash
python3 <handover-skill-root>/scripts/blr-transfer.py pack \
  --base-root <absolute-immutable-base-root> \
  --base-manifest <absolute-spec-hash-input-v1.json> \
  --base-receipt <absolute-immutable-base-receipt.json> \
  --local-root <absolute-authored-local-root> \
  --local-manifest <absolute-spec-hash-input-v1.json> \
  --spec-hash-helper <absolute-spec-hashes.py> \
  --output <absolute-new-package.json>
```

`pack` creates the output with no-clobber semantics and returns its exact
`package_sha256`. Store that value as the handover carrier's outer checksum.

```bash
python3 <handover-skill-root>/scripts/blr-transfer.py validate \
  --package <absolute-package.json> \
  --package-sha256 sha256:<64-lowercase-hex> \
  --spec-hash-helper <absolute-spec-hashes.py> \
  --output-root <absolute-new-isolated-directory>
```

`validate` refuses an unavailable or unsafe Specification helper. It validates
the entire package and outer checksum before creating `output-root`, which must
not exist. It materializes only beneath that new isolated root, recomputes both
dual-hash results with the Specification helper, and succeeds only on exact
result equality. The caller promotes nothing directly from an unvalidated
package.

## Canonical package

The package is BOM/NUL/CR-free strict UTF-8 JSON, serialized with keys sorted,
no insignificant whitespace, no duplicate keys, non-ASCII preserved, and one
final LF. Its exact schema is:

```json
{
  "base": {
    "files": [
      {
        "content_base64": "<canonical RFC 4648 base64>",
        "path": "<portable relative unit path>",
        "sha256": "sha256:<exact-file-hex>"
      }
    ],
    "hash_result": "<complete spec-dual-hash-result-v1 object>",
    "manifest": "<complete spec-hash-input-v1 object>",
    "receipt": {
      "content_base64": "<exact immutable base receipt bytes>",
      "sha256": "sha256:<exact-receipt-hex>"
    }
  },
  "hash_implementation": "plugin:specification/sync-spec/scripts/spec-hashes.py",
  "hash_model": "specification-dual-hash-v1",
  "local": {
    "files": [
      {
        "content_base64": "<canonical RFC 4648 base64>",
        "path": "<portable relative unit path>",
        "sha256": "sha256:<exact-file-hex>"
      }
    ],
    "hash_result": "<complete spec-dual-hash-result-v1 object>",
    "manifest": "<complete spec-hash-input-v1 object>"
  },
  "schema": "specification-blr-transfer+json/v1"
}
```

The quoted object placeholders above denote JSON objects, not string values.
The implementation enforces their exact schemas. Each `files` array is sorted
by raw UTF-8 path bytes and equals its manifest's path set exactly. The embedded
hash result contains every unit's carrier kind, stable identity, logical id,
path, observed revision, exact file SHA-256, semantic-projection SHA-256, plus
the aggregate `transport_manifest_hash` and `contract_digest`. This removes any
side ambiguity: `base.hash_result` describes B and `local.hash_result` describes
L. The outer receipt checksum covers the complete canonical package bytes and
is not stored inside the bytes it hashes.

## Safety and portability

- Package and manifest JSON reject duplicate/unknown keys and non-canonical
  package bytes.
- Unit paths are NFC, canonical relative POSIX paths. Absolute, dot, traversal,
  backslash, duplicate, and case-colliding paths are refused.
- Roots, helper, package, manifests, receipt, and every unit are checked as
  non-symlink regular files/directories; output creation is no-clobber.
- The exact base receipt is strict JSON and may not contain an absolute host,
  `file://`, home-relative, UNC, or Windows-drive path. It must expose top-level
  `hash_model: specification-dual-hash-v1`, `transport_manifest_hash`, and
  `contract_digest` fields equal to the independently recomputed B result; a
  stale or unrelated receipt is refused. The package contains no origin mirror,
  worktree, plugin-cache, or temporary path.
- Base and Local bytes are canonical base64 with independent per-file hashes.
  The base receipt has an independent exact hash. Validation compares those
  first, then independently recomputes the complete dual-hash results.
- A package is reconciliation evidence, never a selected mirror, authored
  source, command vector, or permission to overwrite L.

`baseline_required` means a valid immutable B receipt/byte tree does not exist.
Because v1 deliberately cannot fabricate B, a handover in that state is blocked
until the source owner establishes a base; it may not emit a nominally complete
B/L package containing invented or empty base evidence.
