# Handover examples

```bash
/coding:handover auth-refresh
# Refreshes .engineering/work/auth-refresh/state.md and working.md,
# reconciles existing lazy indexes, and emits a portable receipt.
```

```bash
/coding:handover
# Uses the active work ID from injected/current PM context; rejects ambiguity.
```

```bash
/coding:takeover <task-or-PR-containing-receipt> --revalidate
# Builds an isolated disposable post-anchor tree, verifies the complete v3
# engineering-work-state+json/v1 snapshot plus local, inline, or Notion
# specification carriers there,
# then restores a clean destination and resumes through the declared owner.
```

```bash
/coding:handover checkout-refunds
# If relevant changes exist only in the working copy, returns blocked until an
# approved remote revision or externally attached patch/bundle carries them.
```

Invalid work IDs, missing Essential contract paths, missing specification
identity for specification-led work, non-portable source anchors,
contradictory receipts, or a complete work item are explicit errors. A generic
coding receipt may omit a specification. There is no prefix-based or root-file
compatibility fallback.

For a response-only patch handover, the receipt itself contains the complete
encoded patch, complete state snapshot, and any inline specification payload;
each declares format, encoding, application semantics, and a verified SHA-256.
For an externally published handover, those same carriers may use stable
attachment locators. A path such as `.engineering/work/auth-refresh/state.md`
or `/tmp/auth.patch` is never a portable locator.

For a Notion-backed specification, a portable receipt records a logical
profile such as `product-specs`, the stable page ref, captured remote revision
and paired `transport_manifest_hash`/`contract_digest`, plus at most a contained
suggestion such as `.engineering/notion`. It never records
`/Users/alice/project/.engineering/` or another origin-workspace transport root.
During takeover, `product-specs` is mapped to an exact destination-local ignored
root (or the user selects one), that mapping is recorded, and only then is the
page fetched.

The receipt copies the sync owner's `status`, `classification`, and
`next_action` without mapping them. A ref-only transfer is sufficient only for
`status: success`, `classification:
initial|unchanged|metadata_only|converged`, and `next_action: none`, with no
authored or pending local work. `local_only`, `remote_only`,
`structural_change`, `concurrent`, `baseline_required`, and
`materialization_conflict`, an operational `partial`/`blocked` status, or any
pending next action require the exact helper-produced, checksum-bound
`specification-blr-transfer+json/v1` package. It carries the immutable B
receipt/bytes and authored L tree with their input manifests, observed
revisions, per-unit hashes, and paired dual hashes. Takeover validates and
restores those only into destination-owned isolation, fetches fresh R, and
resumes with a B/L/R classification; it never replaces unsynced L with the
fresh page. If B does not exist or the package is unavailable, handover blocks.

A v2 receipt is an input to migration, not takeover. Re-run `coding:handover`
from its authoritative workspace or explicitly migrate every carrier and add a
checksum-bound complete state snapshot before the destination is touched.
