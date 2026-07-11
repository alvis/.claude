---
name: implement-code
description: Execute an approved specification ticket from authoritative contract through implementation, review, and commit planning. Use after plan-code approval, when resuming partial ticket work, or when auditing a delivered ticket. Keep contract authoring in spec-code and generic feature work in coding:write-code.
model: opus
context: fork
allowed-tools: Task, Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion, Workflow, TodoWrite
argument-hint: "<notion-url-or-id> [--repo=<path>] [--dry-run] [--skip-approval] [--use-cache]"
---

# Implement specification

Orchestrate one ticket in the current working copy. Coding children own source edits; `coding:commit` owns every history mutation; `specification:mdc` is the only writer for `.code-spec/*.md`.

## Resolve the ticket and bundle

1. Normalize the Notion URL or 32-hex ID. Pull the ticket once with `notion-sync pull <id> --follow-children --follow-links --out <tmp>` and classify its status by status group plus label keywords:
   - `to_do` + idea/draft/skeleton/review → `not-ready`
   - `to_do` + pending/ready/approved/queued → `ready-to-code`
   - `in_progress` + implementing/in-progress/wip/coding → `implementing`
   - `in_progress` + audit/verify/qa → `auditing`
   - `complete` + implemented/done/shipped/merged → `done`
   - external/archive/wontfix → `out-of-scope`; unmatched → `unknown`
2. Materialize the authoritative bundle through `specification:sync-spec`. `--use-cache` is valid only when the bundle contains Markdown **and** the non-empty root filename ends with the ticket ID; otherwise record a cache miss and refresh. Refuse if the same root-file gate fails after refresh or immediately before coding.
3. Read local `DRAFT.md`, `PLAN.md`, existing code, and ticket stage. Select exactly one mode:

| Condition | Mode |
|---|---|
| ready-to-code + approved PLAN | `COMMIT_PLAN` |
| implementing + partial work | `PI_ITERATE` |
| ready-to-code + no approved PLAN | `DRAFT_THEN_ASK` |
| auditing | `AUDIT_AND_COMPLETE` |
| done | `VERIFY_ONLY` |
| stage and supplied flags contradict | `FLAG_MISMATCH` |
| not-ready, out-of-scope, or rejected | `REFUSE` |

For `unknown`, ask the user to map the stage before proceeding. Load only the selected child chain from [references/modes.md](references/modes.md).

## Pre-implementation gates

4. Produce one evidence map covering Spec ↔ DRAFT ↔ PLAN ↔ code and every acceptance feature. Cite bundle headings and code symbols; distinguish absent, partial, implemented, and contradictory behavior.
5. Review the proposed contract against current architecture. Fan out only if independent reviewers/workflow capability is actually available; otherwise perform one soundness pass. For every blocking ambiguity, stop and ask. Record the decision through `specification:mdc`, then re-read the changed spec. Never guess an architectural decision.
6. Require approval of the resolved mode, scope, feature map, and soundness decisions unless `--skip-approval`. `--dry-run` stops after reporting this plan.
7. Resolve `repo_path`, verify the working tree, and capture immutable `base_rev` before any child runs. Scaffold `DEVIATIONS.md` only for code-producing modes. Material deviations are appended using the policy in `references/modes.md`; trivial formatter, inferred-type, or documentation differences are not logged.

## Execute and verify

8. Select the mechanism by capability, not preference:
   - If `Workflow` is available and the mode is `COMMIT_PLAN`, `PI_ITERATE`, or `AUDIT_AND_COMPLETE`, load [references/execute-workflow.md](references/execute-workflow.md) and use its fan-out → adversarial verify → retry loop.
   - Otherwise load the selected sequential chain in [references/modes.md](references/modes.md).

   Pass the absolute repo, root spec pointer, acceptance map, mode, and deviation policy to every child. Capture `child_dispatch_log` and `commits_landed`. When execution returns `pending_decision`, stop, ask the user, persist the answer through `specification:mdc`, and resume the same workflow/run; do not start over or continue past it. Surface any iteration/token guard in `unresolved` and return partial with `coding:handover`.
9. When commits landed, load [references/stack-aware-sizing.md](references/stack-aware-sizing.md). Measure the aggregate diff from `base_rev`; route oversized splitting or semantic restacking to `coding:commit`. Never mutate history directly.
10. Run `specification:review-implementation` against the bundle. On P0/P1 alignment findings, dispatch `coding:fix` and retry alignment, at most three passes. Reconcile every material deviation. General and security review still run on every pass.
11. For landed code-producing modes, load [references/thought-experiment.md](references/thought-experiment.md). Run its read-only usage trace at the required capability; if that capability is unavailable, report partial rather than silently downgrade.
12. Detect a linked Git worktree by comparing common-dir and git-dir. A jj workspace is allowed. If a linked Git worktree contains the landed commits, ask whether to keep or relocate them; delegate relocation to `coding:commit`.

## Completion

Return one structured result:

```yaml
status: completed|partial|refused|flagged|dry_run
ticket: {id: '', title: '', stage: '', matched_by: ''}
mode: {selected: '', reason: ''}
spec_bundle: {root_path: '', cache_hit: false, files_count: 0}
workspace: {repo_path: '', base_rev: ''}
coverage: {satisfied: 0, total: 0, gaps: []}
soundness: {issues: [], decisions_recorded: []}
execution: {mechanism: workflow|sequential|none, workflow_runs: 0, pending_decisions_resolved: 0}
child_dispatch_log: []
commits_landed: []
stack: {dispatched: false, mode: null, prs: []}
alignment: {verdict: pass|fail|skipped, iterations: 0, remaining_p0: 0, remaining_p1: 0}
thought_experiment: {status: pass|partial|fail|skipped, summary: ''}
worktree_relocation: {detected: false, action: none|keep|relocate|skipped}
deviations: []
unresolved: []
```

`completed` requires an approved contract, verified acceptance evidence, clean general/security review, clean alignment, and no unresolved decision. `partial` names the exact failed gate and continuation artifact. `refused` names the stage, cache, approval, or capability rule that prevented execution.
