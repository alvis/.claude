# Push PR CI Convergence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `coding:push-pr` as the publishing and CI-convergence owner while preserving `commit --create-pr` and `--branch-prefix` as delegating compatibility entrypoints.

**Architecture:** `coding:commit` owns history and delegates PR publication. `coding:push-pr` performs local CI parity, uses `coding:write-pr` for PR text, publishes the single PR or stack, and schedules small-agent CI monitoring until every PR is green; `coding:stack-code` handles out-of-scope fixes that require a lower stacked PR.

**Tech Stack:** Claude Code skills, Markdown references, YAML behavior/trigger evaluations, `jj`, `gh`, `/loop` scheduled tasks.

---

### Task 1: Capture PR lifecycle behavior

**Files:**
- Create: `plugins/coding/skills/push-pr/evals/evals.yaml`

- [x] **Step 1: Run the failing baseline pressure scenario**

Dispatch one read-only subagent against the existing `commit --create-pr` flow with deadline pressure, pending CI, an out-of-scope failure, and a suggestion to weaken the test. Record that the current flow ends after PR creation and does not guarantee green CI.

- [x] **Step 2: Write objective/process evaluations**

Create three cases: default local-check/publish/monitor behavior, `--skip-local-test`, and red CI requiring retrospective repair plus `stack-code` when the root cause belongs below the PR. Each expectation must assert root-cause repair and prohibit unjustified test weakening.

Add at least five trigger prompts for publishing/babysitting PR CI and five near misses for commit-only history work, PR-body composition, and stack construction.

- [x] **Step 3: Verify the eval file has no placeholders**

Run:

```bash
rg -n 'TBD|TODO|\[.*\]' plugins/coding/skills/push-pr/evals/evals.yaml
```

Expected: no placeholder matches.

### Task 2: Add the push-pr owner

**Files:**
- Create: `plugins/coding/skills/push-pr/SKILL.md`
- Create: `plugins/coding/skills/push-pr/references/repair-red-ci.md`
- Move and harden: `plugins/coding/skills/commit/scripts/restack.sh` to
  `plugins/coding/skills/push-pr/scripts/restack.sh`
- Create: `plugins/coding/skills/push-pr/scripts/test-restack.sh`
- Delete after inlining:
  `plugins/coding/skills/commit/references/workflow-stacked-pr.md`

The publication and poll contracts were inlined in `SKILL.md` so the
always-used path cannot be missed. Only the conditional red-CI repair branch
remains in a reference. Review also required an executable fail-closed stack
sync helper and test rather than a prose-only restack contract.

- [x] **Step 1: Write the always-used skill contract**

Use frontmatter equivalent to:

```yaml
---
name: push-pr
description: 'Publish a saved change or stack as GitHub pull requests and drive every check to green. Use when creating, pushing, updating, or babysitting PRs; use coding:write-pr for text only and coding:stack-code to reshape a stack.'
argument-hint: '[<commit-ref>] [--branch-prefix <name>] [--skip-local-test] [--dry-run]'
---
```

The inline workflow must resolve the target, discover feasible local equivalents from GitHub workflows and repository scripts, dispatch one read-only small test runner unless skipped, repair failures through relevant agents, invoke `coding:commit --retrospective`, publish with `jj`/`gh`, and start `/loop 5m`.

- [x] **Step 2: Relocate and adapt publication instructions**

Move the existing stacked publication procedure without leaving a second implementation under `commit`. Keep `jj git push`, `coding:write-pr`, draft PRs, bookmark/base ordering, restacking, and existing error behavior.

- [x] **Step 3: Write conditional CI convergence instructions**

Define the poll contract around:

```bash
gh pr checks <pr> --json bucket,completedAt,link,name,startedAt,state,workflow
```

Green cancels monitoring and reports success. Pending waits. Red collects failed logs, has the small poller dispatch one relevant fixer, returns evidence to the parent, then the parent runs `coding:commit --retrospective` and republishes. An out-of-scope fix becomes an earlier commit and routes through `coding:stack-code`. After repush, schedule one check at the previous CI wall time plus one minute; if pending, start `/loop 1m`.

Wrap the prohibition against weakening correct tests, adding ignores, or suppressing failures in `<IMPORTANT>`; allow test edits only when evidence shows the test itself is the root cause.

- [x] **Step 4: Run policy validation**

Run:

```bash
python3 plugins/governance/skills/verify-skill/scripts/quick_validate.py plugins/coding/skills/push-pr
```

Expected: zero policy errors and zero policy warnings.

### Task 3: Delegate commit publication and verify ownership

**Files:**
- Modify: `plugins/coding/skills/commit/SKILL.md`
- Modify: commit, finalize-commits, write-code, write-pr, specification, and
  coding ownership references that previously named commit as the publication
  owner.
- Modify: `README.md` and `plugins/coding/references/CODING.md` catalogs.

- [x] **Step 1: Replace implementation with delegation**

Keep `--create-pr` and `--branch-prefix` in frontmatter, inputs, routing, and completion. Replace the create-PR route with a short required handoff to `coding:push-pr`, forwarding the resolved change/stack, branch prefix, `--dry-run`, and verification intent. Remove `commit` claims that it invokes `gh`, pushes bookmarks, or owns the per-PR loop.

- [x] **Step 2: Prove single ownership**

Run:

```bash
rg -n 'gh pr create|jj git push|workflow-stacked-pr' plugins/coding/skills/commit
```

Expected: no matches outside a concise `coding:push-pr` delegation explanation.

- [x] **Step 3: Run structural and behavior verification**

Run the quick validator on both changed skills and the whole coding plugin. Run `claude plugin validate --strict plugins/coding`; accept only the two recorded baseline warnings, with no new warning or error. Exercise the positive and near-miss eval prompts with an independent verifier.

- [x] **Step 4: Review and commit**

Review the diff for coherent ownership, exact flag forwarding, executable scheduling instructions, and preservation of the publication workflow. Run `git diff --check`, then commit with a Conventional Commit message.

- [x] **Step 5: Publish the implementation PR**

Push `feat/push-pr-ci-convergence`, invoke `coding:write-pr` semantics for the title/body, and create a draft PR against `master`. Report the PR URL and verification evidence.
