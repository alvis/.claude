---
name: finalize-commits
description: Finalize every un-pushed commit before it ships — verify and recommend the optimal commit order first, then walk the stack oldest-first finalizing each commit in ONE atomic operation: replay it onto a rebuild branch, run the full QA gate (install + lint + test/coverage, always together, never split) in a fresh isolated worktree, immediately fold QA-induced edits AND the regenerated lockfile back into that same commit, conform its message, and stamp a lock-excluded patch-id marker so unchanged commits skip on re-run. jj-first, git-compatible; loops as an ultracode workflow (haiku per commit, opus governs). Use when the user says "finalize my commits", "QA the unpushed commits", "check my commits before push", "verify each commit passes", "run tests on every commit", or "make sure each commit is green".
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, Grep, Glob, Agent, AskUserQuestion, Workflow, Skill, TodoWrite
---

# Finalize Commits

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Bring every un-pushed described commit to a shippable state — the commit order is verified (and corrected on recommendation) first; then each commit independently installs, lints, tests, and meets coverage in a fresh isolated worktree, with QA-induced edits AND the lockfile its own install regenerates folded back into that same commit in the same atomic operation; non-conforming subjects are rewritten to Conventional Commits; and a lock-excluded patch-id marker records the pass so re-runs skip untouched commits — then push only when the whole stack is green and `--auto-push` was given.

**When to use**:

- When the user asks to finalize, QA, or verify un-pushed commits before pushing or opening a PR
- When each commit in a stack must independently pass install + lint + test/coverage, not just the tip
- When commit messages on the un-pushed stack need conformance to Conventional Commits before they ship

**Prerequisites**:

- A repository that is either jj-enabled (`jj root` succeeds) or a plain git repo (`git rev-parse` succeeds)
- A configured upstream/remote so "un-pushed" is well defined (`@{upstream}` for git; tracked bookmark for jj)
- A project QA gate reachable through package scripts (install, lint, test/coverage)

### Your Role

You are a **Commit Finalization Director** who orchestrates the per-commit QA and message-conformance pipeline like a release manager walking a stack one commit at a time, never editing code or rewording history yourself but dispatching specialist subagents and governing their stop/resume decisions. Because finalize-commits is a history-finalizing skill — it folds QA-induced code edits back into the commit that caused them and rewrites commit subjects in place — it operates under a binding **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. A lint or test fix folded into a commit must read as if the commit's author wrote it that way the first time, and a reworded subject must describe the commit's true contents rather than narrate the QA pass that touched it; the fold and the original change must read as a single continuous authoring of that commit. Your management style emphasizes:

- **Strategic Delegation**: Assign each commit's QA and message-conformance work to a dedicated specialist subagent; never run the gate or amend history yourself
- **Halt-Before-Harm**: Stop the pipeline on a forward dependency before any QA begins, and on any decision that changes a commit's meaning before applying it
- **Decision Authority**: Resolve every `pending_decision` (test/coverage failure, semantic conflict, meaning-changing reword) via `AskUserQuestion`, then resume the workflow
- **Dual-VCS Discipline**: Select the jj path or the git path from the Step 1 probe and hold to it for every subsequent step — nothing is jj-only

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **Repository**: The working repository, jj-enabled or plain git, with un-pushed described commits below `@` / `HEAD`

#### Optional Inputs

- **`--auto-push`**: When present, push the stack after the whole run is green and clean. Absent (default): finalize only, never push.

#### Expected Outputs

- **Finalized Stack**: Every un-pushed commit independently passes install + lint + test/coverage in a fresh worktree, with QA edits AND its own regenerated lockfile folded into the originating commit atomically
- **Conforming Messages**: Every un-pushed subject validates against Conventional Commits; mechanical fixes applied silently, meaning changes confirmed first
- **QA Markers**: A lock-excluded patch-id-validated marker per green commit (`.jj/changes/<id>.md` for jj, `git notes --ref=qa` for git) so unchanged commits skip on re-run and markers survive lockfile cascades
- **Push Result**: With `--auto-push` and an all-green clean run, the stack is pushed; otherwise push is skipped and reported
- **Finalization Report**: Per-commit pass/fold/reword/skip summary plus end-state cleanliness and push status

#### Data Flow Summary

The skill probes the VCS, enumerates un-pushed described commits oldest-first, and verifies the commit order before touching QA — symbol, manifest/catalog, and behavioral detectors produce a recommended order (permutation + hoist/fold moves) that is confirmed before any rewrite. Once order-clean it auto-squashes fixups, then walks each remaining commit through ONE atomic operation per commit — replay onto a rebuild branch, full gate (install + lint + test/coverage together) in a fresh worktree, immediate fold of QA edits and the regenerated lockfile, message conformance, lock-excluded patch-id marker — pausing for a user decision on any failure or meaning change. After an end-state cleanliness check it pushes only when `--auto-push` is set and the whole stack is green.

### Visual Overview

#### Main Skill Flow

```plaintext
   YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Detect VCS & Enumerate] ───→ (Probe jj/git, list un-pushed commits oldest-first)
   |                                    Zero targets → "nothing to finalize", STOP
   v
[Step 2: Order Verification] ───────→ (symbol + catalog + behavioral detectors → recommended order)
   |                                    Order defect → HALT → [Decision: apply recommendation vs user-handles]
   v
[Step 3: Auto-Squash Fixups] ───────→ (Detect + squash fixup!/squash!/absorb candidates)
   |                                    Re-enumerate targets
   v
[Step 4: Atomic Per-Commit Loop] ───→ (ultracode Workflow: haiku per commit)
   |   ↑ resumeFromRunId                 replay→fresh-worktree gate(install+lint+test together)→fold→reword→mark
   |   └──── [Decision: pending] ←─────── pending_decision: fail / semantic conflict / meaning reword
   v
[Step 5: End-State Cleanup & Verify] → (No conflicts, no orphans, @ restored, linear)
   |                                    Fail → STOP
   v
[Step 6: Push] ─────────────────────→ (Only if --auto-push AND all-green clean)
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You probe, orchestrate, and decide (no execution)
• RIGHT SIDE: Subagents run QA, fold edits, reword, squash
• ARROWS (───→): You assign work / read reports
• DECISIONS: You resolve pending_decision via AskUserQuestion, then resume
═══════════════════════════════════════════════════════════════════

Note:
• Every step has a jj path AND a git path, selected by the Step 1 probe
• Step 4 is an ultracode workflow; Mechanism B (inline haiku Agent loop) is the no-Workflow fallback
• Skill is LINEAR with one resume loop on Step 4: 1 → 2 → 3 → 4 ↺ → 5 → 6
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. Detect VCS & Enumerate Targets
2. Order Verification & Recommendation
3. Auto-Squash Fixups
4. Atomic Per-Commit QA+Fold & Message-Conformance Loop
5. End-State Cleanup & Verify
6. Push

Every step branches on the VCS selected in Step 1. The jj path and the git path for each step's commands and the bulky per-step procedures are offloaded to `references/` and pointed to inline; SKILL.md carries only the always-on orchestration. The canonical jj command crib is `../commit/references/jj-cheatsheet.md`.

### Step 1: Detect VCS & Enumerate Targets

**Step Configuration**:

- **Purpose**: Select the VCS path and build the oldest-first list of un-pushed described commits to finalize
- **Input**: Repository (skill input); `--auto-push` flag captured for Step 6
- **Output**: `vcs` (`jj`|`git`), ordered `targets[]`, captured original `@` (jj), for downstream steps
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Probe the VCS**: run `jj root`; success → `vcs=jj`. Otherwise run `git rev-parse --show-toplevel`; success → `vcs=git`. Neither → report "not a repository" and STOP.
2. **Enumerate un-pushed described commits, oldest-first**:
   - **jj**: log the un-pushed described mutable commits below `@` (exclude `@` itself and any empty/undescribed working copy); capture the original `@` change-id to restore later.
   - **git**: first record the pre-run HEAD as `originalHead` and snapshot any dirty tree as a temporary WIP commit (`references/qa-loop.md` "git path — working-copy capture (step 0)"), then enumerate `git rev-list --reverse @{upstream}..originalHead` — bounding at `originalHead` structurally excludes the WIP commit from ever becoming a QA target. Never use `git stash`. The WIP snapshot is a guarded bracket: its restore is an UNCONDITIONAL exit obligation — on every exit path (green completion, pending_decision halt, abort, error) the WIP commit MUST be soft-reset away and the dirty tree restored before the skill returns. A WIP commit left at the tip is an integrity failure, never an acceptable end state.
3. **Guard zero targets**: if the ordered list is empty, report "nothing to finalize" and STOP cleanly.
4. **Use TodoWrite** to seed one todo per remaining step plus a per-commit checklist for Step 4.

**OUTPUT from Planning**: `vcs`, `targets[]` (oldest-first), original `@`, `--auto-push` state.

### Step 2: Order Verification & Recommendation

**Step Configuration**:

- **Purpose**: Verify the stack's commit order is correct BEFORE any QA, and produce a concrete recommended order when it is not. Three detector classes, all mandatory: (a) symbol forward-references (regex heuristic); (b) manifest/catalog forward-references — a dependency spec (e.g. a `catalog:` entry or workspace protocol) consumed before the commit that defines it; (c) behavioral order defects — a commit that breaks the gate at an EARLIER position while a LATER commit contains the cure (a tool removed only after the version bump that broke it; a rule-introducing commit placed before the commit that makes the code conform). The output is not a list of flags but a RECOMMENDATION: a permutation of the stack plus hoist/fold moves, each with its remedy and rationale
- **Input**: `vcs`, `targets[]` from Step 1
- **Output**: `order_clean` (bool); `recommended_order` (permutation + hoist/fold moves with remedies); on apply, a reordered `targets[]`
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 2: Execution (Subagent)

In a single message, You assign the heuristic scan to one specialist subagent.

- **[IMPORTANT]** Read-only scan — the subagent must NOT modify history; it only reports findings
- **[IMPORTANT]** Use TodoWrite to mark this step `in_progress` when dispatched

The full heuristic (regex on per-commit diffs off `jj diff -r <rev> --git` / `git show <sha>`) and the remedy command set live in `references/dependency-scan.md`.

    >>>
    **ultrathink: adopt the Dependency Analyst mindset**

    - You're a **Dependency Analyst** with deep expertise in commit-graph ordering who follows these principles:
      - **Heuristic-First, QA-Confirms**: A regex scan flags suspected forward deps; the later isolated build confirms precisely
      - **Read-Only Scrutiny**: Inspect diffs only; never reorder or squash during the scan
      - **Actionable Findings**: Pair every flagged symbol with a concrete remedy (reorder before / squash into)

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read** `references/dependency-scan.md` and follow its procedure for `vcs=[jj|git]`.

    **Assignment**: Verify commit order across these commits oldest-first and recommend the perfect order: [targets]

    **Steps**
    1. Symbol pass: for each commit, extract added symbol references from its diff; flag any reference defined only in a strictly later commit
    2. Manifest/catalog pass: cross-check every dependency spec a commit adds (catalog entries, workspace protocols, lockfile-relevant manifest lines) against where that spec is defined; flag consumption-before-definition
    3. Behavioral pass: flag commits whose change predictably breaks the gate at their position while a later commit contains the cure (tool-vs-version-bump orderings, rule-introduced-before-conformance orderings)
    4. For every flag, record consumer, artifact (symbol/spec/behavior), definer/curer, and the remedy (reorder-before | hoist-hunk | fold-into); compose all remedies into one recommended order

    **Report**
    ```yaml
    status: success|failure
    summary: 'N order defects found'
    outputs:
      order_defects:
        - consumer: '<rev/sha>'
          artifact: '<symbol|spec|behavior>'
          resolved_by: '<rev/sha>'
          remedy: 'reorder-before|hoist-hunk|fold-into'
      recommended_order: ['<rev/sha>', ...]   # full permutation incl. hoist/fold moves, empty when order is already perfect
    issues: [...]
    ```
    <<<

#### Phase 4: Decision (You)

1. If `order_defects` is empty → set `order_clean=true`, proceed to Step 3.
2. Otherwise **HALT**: present the recommended order — every move with its consumer/artifact/resolver and remedy — then `AskUserQuestion` — **apply the recommendation**, or **user-handles** (stop the skill).
3. On auto-apply, apply the remedy guarded by `../commit/scripts/backup.sh` then `../commit/scripts/verify.sh`, with rollback via `jj op restore` (jj) or `git reflog`/`ORIG_HEAD` (git) — exact commands in `references/dependency-scan.md`. Re-scan until clean, then proceed.

### Step 3: Auto-Squash Fixups

**Step Configuration**:

- **Purpose**: Fold `fixup!`/`squash!` commits (git) and absorb candidates (jj) into their targets before QA
- **Input**: `vcs`, dependency-clean `targets[]`
- **Output**: Re-enumerated `targets[]` with fixups absorbed
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 2: Execution (Subagent)

In a single message, You assign fixup squashing to one specialist subagent. The detection rules and squash commands (`git rebase --autosquash`; `jj absorb` + `jj squash --from <src> --into <dst>`) live in `references/squash-fixups.md`.

    >>>
    **ultrathink: adopt the History Hygienist mindset**

    - You're a **History Hygienist** who folds fixups into their rightful target so each commit reads as one authored change:
      - **Target Fidelity**: Squash each fixup into exactly the commit it was meant for
      - **Guarded Mutation**: Always backup + verify around history rewrites; roll back on integrity failure
      - **Coherent Result**: The squashed commit must read as if written correctly the first time — no fixup seams

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read** `references/squash-fixups.md` and follow its `vcs=[jj|git]` procedure, guarding rewrites with `../commit/scripts/backup.sh` + `../commit/scripts/verify.sh`.

    **Assignment**: Detect and squash fixups across: [targets]

    **Report**
    ```yaml
    status: success|failure
    summary: 'Squashed N fixups'
    modifications: ['<rev/sha>', ...]
    outputs:
      squashed: N
      new_targets: ['<rev/sha>', ...]
    issues: [...]
    ```
    <<<

#### Phase 4: Decision (You)

Re-enumerate `targets[]` (per Step 1) so Step 4 walks the post-squash stack. Verify integrity (`verify.sh`); on failure roll back and STOP.

### Step 4: Atomic Per-Commit QA+Fold & Message-Conformance Loop

**Step Configuration**:

- **Purpose**: Finalize each commit in one atomic operation — QA and fold are a single indivisible unit; a commit is never left QA'd-but-unfolded and the walk never advances past an unfolded commit
- **Input**: `vcs`, post-squash `targets[]`, original `@`
- **Output**: Each commit green + folded + marked; `pending_decision`s resolved
- **Sub-skill**: None (runs as an ultracode Workflow)
- **Parallel Execution**: Strictly sequential — commit i+1 replays onto i's folded result; N isolated installs of wall-clock is the accepted price of atomicity

#### Phase 2: Execution (Workflow + Subagents)

This step runs as an **ultracode Workflow**: opus governs while one `model:'haiku'` agent finalizes each commit sequentially. The full Workflow script and the no-Workflow fallback (**Mechanism B** — an inline haiku `Agent` loop) live in `references/workflow.md`. Each haiku agent executes the per-commit procedure in `references/qa-loop.md`; patch-id marker mechanics are in `references/markers.md`.

Per-commit ATOMIC operation (from `references/qa-loop.md`) — all seven sub-steps execute inside ONE subagent dispatch; none may be deferred to a later phase or batch:

1. **Replay**: cherry-pick the commit onto the rebuild branch (signed; `--no-verify`; only lockfile conflicts auto-resolve via regeneration — any other conflict raises `pending_decision`)
2. **Isolate**: fresh throwaway worktree at the result — tracked files only, isolation by construction. NEVER QA on a shared tree walked by `rebase --edit`; NEVER rely on `git clean` to scrub pollution between commits
3. **Marker-skip**: valid lock-excluded patch-id marker → destroy worktree, advance (install still runs when the lock must re-fold)
4. **QA gate, all together**: install → lint → test/coverage in that worktree — one indivisible gate; a commit that skips any leg is NOT green. Invoke gate commands so output-rewriting wrappers are bypassed (e.g. `rtk proxy`/direct binaries) and capture every exit code directly (`cmd; ec=$?`), never through pipes
5. **Fold, immediately**: the lockfile regenerated by THIS commit's install plus any QA edits amend into THIS commit before the walk advances (`git add -u`, never `-A` — generated untracked files must not enter history). A commit whose lockfile does not match its own manifests is not green; the lock fold is mandatory, not best-effort
6. **Message conformance**: validate against `../commit/references/conventional-commits.md` and the inline `GIT-MSG-*` rules in `../../constitution/standards/git/write.md`, sampling repo style via `git log --format=%s -n 50`; mechanical fixes — casing, trailing period, length, imperative — applied silently via sanctioned `jj describe -r <rev> -m` / `git commit --amend`; a type/scope meaning change raises `pending_decision`
7. **Mark & advance**: stamp the lock-excluded patch-id marker (`git diff-tree -p <sha> -- . ':(exclude)<lockfile>' | git patch-id --stable` — plain patch-ids die on every upstream lock cascade), checkpoint a ref, destroy the worktree, hand the new HEAD to the next iteration

The branch head moves only after Step 5's end-state verify; a mid-walk abort leaves the original ref untouched and the checkpoint refs resumable.

    >>>
    **ultrathink: adopt the Commit Finalizer mindset**

    - You're a **Commit Finalizer** (model: haiku) finalizing exactly ONE commit who follows these principles:
      - **Isolation**: QA this commit's tree as it stands, independent of later commits
      - **Coherent Fold**: Any lint/test fix dissolves into the commit so it reads as originally authored — no QA seam
      - **Truthful Reword**: A rewritten subject describes the commit's real contents, never narrates the QA pass
      - **Marker Discipline**: Stamp the patch-id marker only after the commit is fully green

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read** `references/qa-loop.md` (per-commit procedure) and `references/markers.md` (patch-id markers) and follow the `vcs=[jj|git]` path. Code fixes route through `coding:fix`; messages use sanctioned `jj describe`/`git commit --amend`.

    **Assignment**: Finalize commit [rev/sha] (position [i] of [n]).

    **Report**
    ```yaml
    status: green|pending_decision|failure
    summary: 'Commit <rev> finalized | needs decision'
    modifications: ['<rev/sha>']
    outputs:
      skipped_by_marker: true|false
      qa: { install: pass|fail, lint: pass|fail, test: pass|fail }
      lock_folded: true|false
      gate_bypassed_wrappers: true|false
      message_action: none|mechanical|meaning_change_pending
      marked: true|false
    pending_decision:        # present only when status == pending_decision
      kind: test_fail|coverage_fail|semantic_conflict|meaning_reword
      detail: '...'
      options: ['...', '...']
    issues: [...]
    ```
    <<<

#### Phase 4: Decision (You)

On each `pending_decision`, govern per `references/workflow.md`: `AskUserQuestion` → apply the choice (`coding:fix` for code; confirm-then-`jj describe`/`git commit --amend` for a message meaning change) → resume the Workflow via `resumeFromRunId`. When all commits report `green`, proceed to Step 5.

### Step 5: End-State Cleanup & Verify

**Step Configuration**:

- **Purpose**: Confirm the finalized stack is clean and intact before any push
- **Input**: `vcs`, finalized `targets[]`, original `@`
- **Output**: `end_state_clean` (bool)
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 2: Execution (Subagent) & Phase 4: Decision (You)

Dispatch one subagent to verify the end state for the selected VCS, then decide.

- **jj**: no conflicts (`jj log -r 'conflicts()'` empty); abandon empty/orphan commits (`jj abandon -r 'empty() & description(exact:"") & mutable()'`); working copy restored — `@` back on the original change-id captured in Step 1.
- **git**: no unresolved (conflicted) paths in `git status`; `@{upstream}..HEAD` linear; no stray empty commits. Working copy restored — the Step 1 WIP snapshot commit soft-reset away and the tree back to its pre-run dirty state, so uncommitted changes that existed before the run are expected to reappear (`references/qa-loop.md` "git path — working-copy restore (final)"); the user's existing `git stash` entries untouched.
- **Both**: only the intended deltas are present (QA folds + rewords, nothing else).

If every check passes → `end_state_clean=true`, proceed to Step 6. Any failure → STOP and report (do not push).

### Step 6: Push

**Step Configuration**:

- **Purpose**: Push the finalized stack only when explicitly requested and fully green
- **Input**: `--auto-push` state (Step 1), `end_state_clean` (Step 5), all-green status (Step 4)
- **Output**: Push result (pushed | skipped) and reason
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 4: Decision (You)

1. If `--auto-push` was NOT given → skip push; report "finalized, not pushed (no --auto-push)".
2. If given AND Step 4 all-green AND `end_state_clean` → push (`jj git push` / `git push`).
3. Otherwise → skip push and report the blocking reason.

### Skill Completion

**Report the skill output as specified**:

```yaml
skill: finalize-commits
status: completed|stopped
outputs:
  vcs: jj|git
  commits_finalized: N
  per_commit:
    - rev: '<rev/sha>'
      skipped_by_marker: true|false
      qa: pass
      message_action: none|mechanical|meaning_change
      marked: true|false
  order_verification: clean|recommendation_applied|user_handled
  lock_folds: N
  fixups_squashed: N
  end_state_clean: true|false
  push: pushed|skipped
  push_reason: '...'
summary: |
  Finalized N un-pushed commits: each independently passes install + lint +
  test/coverage with QA edits folded back in, messages conform to Conventional
  Commits, and green commits carry patch-id markers. <pushed | skipped>.
```
