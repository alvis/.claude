# Finalization Workflow

`finalize-commits` coordinates read-only inspection, isolated QA, and approval
gates. It delegates every mutation to `coding:commit`, including correction
folds, message changes, stack movement, rollback, checkpointing, and push.

For a failed gate, route code changes to `coding:fix`, then ask `coding:commit`
to apply the approved change. For a semantic conflict or meaning-changing
reword, stop for approval. Resume only after `coding:commit` reports success and
rerun the affected commit's complete QA.
