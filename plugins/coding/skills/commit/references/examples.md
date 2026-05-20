# End-to-end transcripts

Reference transcripts for every route the skill takes. See [SKILL.md](../SKILL.md) for the pipeline that contains these.

---

## 1. Default save — simple one-concern `@`

User: "commit my changes"

```bash
jj diff --stat
# A packages/web/src/components/AvatarPicker.tsx | +42 -0
```

LLM proposes:

```text
Route: default save
Plan: 1 commit
  feat(user-profile): add AvatarPicker component
```

User confirms. Skill executes:

```bash
jj describe @ -m "feat(user-profile): add AvatarPicker component" -m "Initial picker with drag-drop and crop preview."
git commit --allow-empty -m "feat(user-profile): add AvatarPicker component

Initial picker with drag-drop and crop preview."
jj new
```

Hook prints `── Integrity Check ── PASS / PASS`. `npm run lint/test/build` all green. Report.

---

## 2. Auto-detected split — multi-concern `@`

User: "commit my changes"

```bash
jj diff --name-only
# packages/data/src/user/avatar.ts
# packages/service/src/user/uploadAvatar.ts
# packages/web/src/components/AvatarPicker.tsx
# packages/auth/src/tokenExpiry.ts                   (unrelated bugfix!)
# packages/auth/test/tokenExpiry.spec.ts             (unrelated)
```

LLM detects two concerns. Proposes:

```text
Route: auto-split (2 commits)

01 feat(user-profile): add avatar upload
   - packages/data/src/user/avatar.ts
   - packages/service/src/user/uploadAvatar.ts
   - packages/web/src/components/AvatarPicker.tsx

02 fix(auth): correct token expiry off-by-one
   - packages/auth/src/tokenExpiry.ts
   - packages/auth/test/tokenExpiry.spec.ts
```

User confirms. Skill executes per [workflow-split.md](./workflow-split.md):

```bash
jj split packages/auth/src/tokenExpiry.ts packages/auth/test/tokenExpiry.spec.ts
jj describe @- -m "fix(auth): correct token expiry off-by-one" -m "Token comparison was using >= where > was correct..."
jj describe @  -m "feat(user-profile): add avatar upload" -m "Data + service + UI..."
jj new
```

Both commits build standalone. Report two change ids.

---

## 3. Auto-detected edit — "edit commit X"

User: "edit the avatar commit — picker should clamp at 5MB not 10"

```bash
jj log -r 'description(glob:"avatar")' --no-graph
# Resolves to change abc123
gh pr view feat-avatar/01-web --json state -q .state
# OPEN — proceed
```

Skill executes per [workflow-edit.md](./workflow-edit.md):

```bash
jj op log -n1 --no-graph -T 'self.id().short()'     # rollback handle: op42
jj edit abc123
# (edits file)
jj new
```

Downstream bookmark exists → `restack.sh feat-avatar` reparents two downstream PRs. Integrity PASS. Report.

---

## 4. Auto-detected parallel-workspace — unrelated work

User: "while we wait for review on the avatar stack, can you also fix the broken footer link?"

LLM detects: avatar work on `@`, footer is in a different package, no shared files. AskUserQuestion:

```text
Proposed work (footer fix in packages/web/src/Footer.tsx) is unrelated
to current @ (avatar work in packages/user-profile/).

Open a parallel jj workspace?
[Y] Yes — `jj workspace add ../repo-footer-fix` on main@origin
[N] No — keep work on @, accept mixed history
```

User: Y. Skill executes per [workflow-parallel.md](./workflow-parallel.md):

```bash
jj workspace add ../repo-footer-fix --revision main@origin
cd ../repo-footer-fix
# (edits Footer.tsx)
jj describe @ -m "fix(web): repair broken privacy-policy link in footer"
git commit ...
```

Work integrated separately. Later: `jj workspace forget repo-footer-fix` from main workspace.

---

## 5. Auto-detected empty change — abandon prompt

User: "commit my changes"

```bash
jj diff --stat
# (empty)
jj log -r @ --no-graph
# abc999  (no description)
jj op log -r '@::' --limit 5
# op55 new
```

Skill detects empty + only `new` op. Proposes:

```text
@ is empty (no description, no diff, only `new` op since creation).
Abandon and start fresh?
```

User: yes.

```bash
jj abandon @
jj new
```

Report: nothing to commit.

---

## 6. Auto-detected divergent change — investigate-and-resolve

```bash
jj log -r 'visible_heads()'
# ??  abc123  feat(user-profile): add avatar upload
# ??  abc123  feat(user-profile): add avatar upload  (newer)
```

Skill detects `??` per [scenario-divergent.md](./scenario-divergent.md):

```bash
jj log -r 'change_id(abc123)' --no-graph
# abc123/0  commit deadbeef  2 days ago  (matches main@origin parent A)
# abc123/1  commit feedcafe  10 min ago  (matches main@origin parent B — newer fetch)

jj diff --from abc123/0 --to abc123/1
# /0 has an extra hunk in avatar.ts that /1 lacks
```

Skill proposes: absorb /0's hunk into /1, abandon /0.

```bash
jj squash --from abc123/0 --into abc123/1
jj abandon abc123/0
jj log -r 'change_id(abc123)' --no-graph
# (single result — divergence resolved)
```

`restack.sh feat-avatar` re-syncs the chain. Report.

---

## 7. Auto-detected correct-merged — corrective PR vs rewrite

User: "edit the original auth feature commit to bump the rate limit"

```bash
gh pr view feat-auth/01-service --json state -q .state
# MERGED
```

Skill detects merged target per [workflow-correct-merged.md](./workflow-correct-merged.md). AskUserQuestion:

```text
Target change is on origin and PR is MERGED.
[1] Corrective PR on top (recommended, default)
[2] Rewrite the branch (explicit consent)
```

User picks [1]. Skill executes:

```bash
jj new main@origin
# (apply the rate-limit bump in service code)
jj describe @ -m "fix(auth): raise login rate limit from 5 to 10 per minute" \
              -m "Tighter limit caused legitimate burst sign-ins to fail post-launch (ref: feat-auth/01-service merged PR)."
git commit ...
```

Subsequently `/coding:commit --create-pr` opens a single new PR on `main`.

---

## 8. `--retrospective` — three-stage

User: "/coding:commit --retrospective"

`@` has hunks belonging to two earlier commits in the open stack.

```bash
jj op log -n1 --no-graph -T 'self.id().short()'   # rollback: op77

# Stage 1
jj absorb
jj diff --stat
# Still 2 hunks unresolved in src/auth/utils.ts
```

Skill runs Stage 2 per [workflow-retrospective.md](./workflow-retrospective.md):

```bash
jj blame @ src/auth/utils.ts -L 42,58
# Surrounding lines last touched by change def456 (feat(auth): add token util)
jj blame @ src/auth/utils.ts -L 60,71
# Same change def456

# All residue maps to def456
jj squash --from @ --into def456 src/auth/utils.ts
jj diff --stat
# (empty — Stage 2 complete)
```

Stage 3 not needed (no git-only target). `restack.sh feat-auth` re-syncs descendants. Integrity PASS. Per-change build PASS. Report.

---

## 9. `--reorder` — content-equivalence pass

User: "/coding:commit --reorder"

Chain has UI before data:

```bash
jj log -r 'main@origin..@'
# abc123 feat(web): avatar picker UI
# def456 feat(service): upload endpoint
# ghi789 feat(data): avatar field
```

Skill plans data → service → UI. User confirms.

```bash
jj op log -n1 --no-graph -T 'self.id().short()'   # rollback: op88
jj rebase -s ghi789 -d main@origin
jj rebase -s def456 -d ghi789
jj rebase -s abc123 -d def456

bash "${CLAUDE_PLUGIN_ROOT}/skills/commit/scripts/verify.sh"
# ── Integrity Check ──
# GIT_TREE_MATCH: PASS
# CONTENT_MATCH:  PASS
```

`restack.sh feat-avatar` reparents the three open PRs (each PR's base now matches the new parent). Report.

---

## 10. `--create-pr` — 3-PR stack with branch-prefix

User: "/coding:commit --create-pr --branch-prefix feat-avatar"

Chain is already clean + linear (from prior `--reorder`). Skill walks per [workflow-stacked-pr.md](./workflow-stacked-pr.md):

```bash
# PR 01
jj bookmark set feat-avatar/01-data --revision ghi789
jj git push --bookmark feat-avatar/01-data --allow-new
# Invoke /coding:write-pr ghi789
# → title + body returned
gh pr create --draft --title "feat(data): add avatar field" --body-file - --base main --head feat-avatar/01-data <<<"$BODY"

# PR 02
jj bookmark set feat-avatar/02-service --revision def456
jj git push --bookmark feat-avatar/02-service --allow-new
# /coding:write-pr def456
gh pr create --draft --title "feat(service): add upload endpoint" --body-file - --base feat-avatar/01-data --head feat-avatar/02-service <<<"$BODY"

# PR 03
jj bookmark set feat-avatar/03-web --revision abc123
jj git push --bookmark feat-avatar/03-web --allow-new
# /coding:write-pr abc123
gh pr create --draft --title "feat(web): add AvatarPicker" --body-file - --base feat-avatar/02-service --head feat-avatar/03-web <<<"$BODY"
```

Report 3 PR URLs.

---

## 11. Behaviour flags — `--no-verify`, `--dry-run`, `--allow-rewrite-merged`

### `--no-verify`

```bash
/coding:commit --no-verify
# Default save runs. git commit --no-verify skips pre-commit hooks.
# Step 5 SKIPS `npm run lint/test/build`.
# PostToolUse integrity hook STILL fires (independent of --no-verify).
```

### `--dry-run`

```bash
/coding:commit --dry-run
# Plan printed:
#   Route: auto-split (2 commits)
#   01 feat(user-profile): add avatar upload
#      - packages/data/src/user/avatar.ts ...
#   02 fix(auth): correct token expiry off-by-one
#      - packages/auth/src/tokenExpiry.ts ...
# No jj/git mutation. No bookmarks set. No PRs opened.
```

### `--allow-rewrite-merged`

```bash
/coding:commit --retrospective --allow-rewrite-merged
# Target ancestor is merged-on-origin.
# AskUserQuestion is SKIPPED.
# Skill proceeds to Option 2 (rewrite) per workflow-correct-merged.md.
# For rewind (non-descendant push): jj bookmark forget; jj bookmark set; jj git push --allow-new.
```
