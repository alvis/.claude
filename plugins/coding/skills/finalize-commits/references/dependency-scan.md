# Stack Dependency Scan

Inspect the unpushed stack read-only and report each defect as:
`consumer`, `artifact`, `resolved_by`, and `remedy`.

Remedies are recommendations only: `reorder-before`, `fold-into`, or
`hoist-hunk`. Return `status`, `summary`, and `outputs.order_defects` with the
full `recommended_order`; include `modifications` as an empty list until an
approved operation is delegated. Present the full proposed order for approval. Once approved,
delegate the corresponding history operation to `coding:commit`; that skill is
the sole owner of rebase, split, squash, reorder, rollback, and checkpoint
operations. Re-run all detectors after the delegated operation and verify that
the tip tree is unchanged except for the approved history transformation.
