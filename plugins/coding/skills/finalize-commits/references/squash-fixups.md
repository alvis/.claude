# Fixup Review

Read-only detection identifies `fixup!`, `squash!`, or absorb candidates and
reports their intended target. Do not apply the fixup in this skill.

Return `status`, `summary`, `outputs.squashed`, `outputs.new_targets`, and
`issues`; use empty arrays when no fixups are found. After approval, invoke
`coding:commit` with the target and requested operation. It owns autosquash,
absorb, rollback, and all other history mutations. Re-enumerate the stack and
run the per-commit QA reference after the delegated operation.
