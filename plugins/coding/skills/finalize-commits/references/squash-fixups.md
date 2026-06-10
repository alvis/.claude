# Auto-Squash Fixups — detect + squash (jj + git)

Referenced from SKILL.md Step 3. Folds fixup-style commits into their targets before QA so each commit reads as one authored change (Coherence Mandate). All rewrites are guarded by `../../commit/scripts/backup.sh` then `../../commit/scripts/verify.sh`.

## Detect

### git

- `fixup!`/`squash!` subjects: a commit whose subject starts with `fixup! ` or `squash! ` names its target by the target's subject.
- List candidates oldest-first across `@{upstream}..HEAD`:

```bash
git log --reverse --format='%H %s' @{upstream}..HEAD | grep -E '^[0-9a-f]+ (fixup|squash)! '
```

### jj

jj has no literal `fixup!` convention; instead detect **absorb candidates** — uncommitted or late edits that belong to an earlier commit's lines:

- `jj absorb --dry-run` (preview which hunks would flow into which ancestor).
- Also treat any mutable commit whose description starts with `fixup!`/`squash!` (e.g. imported from git) as an explicit target reference.

## Squash

### git

```bash
git rebase --autosquash --interactive @{upstream}~1   # autosquash orders fixup!/squash! onto targets
```

Prefer non-interactive where the sequence is unambiguous: set `GIT_SEQUENCE_EDITOR=:` to accept the autosquash plan.

### jj

```bash
jj absorb                                  # flow eligible hunks into the ancestors that own those lines
jj squash --from <src> --into <dst>        # explicit fixup commit → its target
```

For an explicit `fixup!`-described commit, resolve `<dst>` from the referenced subject, then `jj squash --from <fixup-rev> --into <dst>`.

## After squashing

- Run `verify.sh`; on integrity failure roll back (`jj op restore` / `git reset --hard ORIG_HEAD`) and STOP.
- Re-enumerate targets (per SKILL.md Step 1) so the QA loop walks the post-squash stack.
- The squashed commit's message must still describe its full contents — if the fold changed what the commit does, message conformance in Step 4 will catch and reword it.
