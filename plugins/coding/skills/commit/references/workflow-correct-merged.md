# Auto-detected: target of edit/absorb is already merged on origin

Triggered any time the skill would rewrite a change whose bookmark is associated with a `MERGED` PR. Default = corrective PR on top per `GIT-PR-STACK-03`. Rewrite-with-consent is opt-in. See [SKILL.md](../SKILL.md).

## When triggered

Any of:

- [workflow-edit.md](./workflow-edit.md) Step 2 detects a merged ancestor
- [workflow-retrospective.md](./workflow-retrospective.md) blame map includes a merged target
- [workflow-reorder.md](./workflow-reorder.md) range includes a merged change
- Any other rewrite that would touch git history already on origin

Detection:

```bash
# For each bookmark pointing at or downstream of the target:
gh pr view <bookmark> --json state -q .state
# MERGED → this workflow
```

## Procedure

### 1. Ask the user (unless `--allow-rewrite-merged`)

If the user did NOT pass `--allow-rewrite-merged`, run `AskUserQuestion`:

```text
Target change <change_id> is already on origin and its PR is MERGED.

Rewriting merged history breaks consumers and violates GIT-PR-STACK-03.
How would you like to proceed?

[1] Corrective PR on top (recommended, default)
    — create a NEW change that fixes the issue
    — open a new PR targeting the same branch
[2] Rewrite the branch (explicit consent)
    — force-push a rewritten history
    — may insert new jj changes into history already on origin
    — requires coordinating with reviewers / consumers
```

If `--allow-rewrite-merged` is set, skip the prompt and proceed directly to Option 2.

### 2. Option 1 — corrective PR (default, recommended)

This is the `GIT-PR-STACK-03` path: never rewrite merged history; layer a fix on top.

```bash
# Start a fresh change on top of main@origin
jj new main@origin

# Apply the corrective changes (the original edits that triggered this workflow)
# (LLM applies the file edits here)

# Validate + describe
jj describe @ -m "<conventional-subject>" -m "Body explaining what the corrective change fixes from <merged_pr_url>."
```

Then follow the normal save flow ([workflow-save-local.md](./workflow-save-local.md)) and, if the user wants a PR, [workflow-stacked-pr.md](./workflow-stacked-pr.md) (single-PR variant works the same).

The corrective PR title typically uses `fix(scope): ...` referencing the regression. Link to the original merged PR in the body.

### 3. Option 2 — rewrite the branch (explicit consent)

Only on user choice [2] or `--allow-rewrite-merged`.

```bash
# Snapshot rollback handle
jj op log -n1 --no-graph -T 'self.id().short()'
```

Apply the originally-intended rewrite (edit, retrospective squash, reorder, or insertion of new jj changes into already-pushed history).

Examples:

```bash
# Edit a merged change
jj edit <merged_change_id>
# (modify files)
jj new

# Insert a new change before a merged one
jj new <merged_change_parent>
# (add code)
jj rebase -s <merged_change> -d @
```

Then force-push the affected bookmarks:

```bash
jj git push --bookmark <bookmark_name>
```

`jj git push --bookmark` enforces force-with-lease semantics natively (jj's operation log proves the local tip is a known rewrite of the remote tip — no extra flag needed for the rewrite case). When the bookmark needs to rewind to a non-descendant change (a true history rewind), `jj` refuses the push; resolve by:

```bash
jj bookmark forget <bookmark_name>     # drop local tracking
jj bookmark set <bookmark_name> -r <new_change>
jj git push --bookmark <bookmark_name> --allow-new
```

Verify the integrity guard ([SKILL.md](../SKILL.md) Step 5) passes.

### 4. Communicate to reviewers (Option 2 only)

After the force-push, the user MUST notify any open downstream PRs / consumers that their base has been rewritten. This is procedural, not automated — the skill surfaces a reminder:

```text
Rewrote merged-on-origin history at <bookmark>.
Notify reviewers and downstream consumers:
  - <list of open PRs / branches built on top>
```

## Hard rules

- Default route is ALWAYS the corrective PR. Only deviate on explicit user choice or `--allow-rewrite-merged`.
- `--allow-rewrite-merged` skips the `AskUserQuestion` prompt but does NOT skip the integrity guard.
- Conventional regex enforced on any new change introduced.
- A rewrite that touches main@origin's tip itself is forbidden — surface and abort regardless of consent.

## Mandatory follow-ups

- Option 1: normal save follow-ups ([workflow-save-local.md](./workflow-save-local.md)).
- Option 2: integrity check; restack.sh if downstream bookmarks exist; project scripts.
- Always: report the chosen route in [SKILL.md](../SKILL.md) Step 6 summary.

## Error / edge cases

| Symptom | Action |
|---|---|
| Force-push rejected by branch protection | Branch is protected against rewriting (correct posture for merged main). Route back to Option 1 (corrective PR). |
| User picks Option 2 then changes mind mid-flow | `jj op restore <op_id>` rewinds; `jj git push --bookmark <name>` re-syncs from clean state. |
| Multiple merged targets in one rewrite | Run the prompt ONCE listing all targets; user's choice applies to the whole batch. |
