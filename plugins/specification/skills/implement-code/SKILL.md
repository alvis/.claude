---
name: implement-code
description: Execute an approved specification ticket from authoritative contract through implementation, review, and commit planning. Use after plan-code approval, when resuming partial ticket work, or when auditing a delivered ticket. Keep contract authoring in spec-code and generic feature work in coding:write-code.
model: opus
context: fork
allowed-tools: Task, Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion, Workflow, TodoWrite
argument-hint: "<notion-url-or-id> [--repo=<path>] [--dry-run] [--skip-approval] [--use-cache]"
---

# Implement Specification

Orchestrate one specification ticket in the current working copy. Coding
children own source edits; `coding:commit` owns local history shaping,
`coding:push-pr` owns publication and remote restacking, and
`specification:mdc` is the only writer for `.code-spec/*.md`.

## Boundaries

- Use for: executing an approved specification ticket end to end — mode
  resolution, pre-implementation gates, delegated implementation, alignment
  review, and commit planning — plus resuming partial ticket work or auditing
  a delivered ticket.
- Do not use for: authoring or amending the contract itself
  (`specification:spec-code`), generic feature work with no ticket
  (`coding:write-code`), direct commits or history edits (`coding:commit`),
  or hand-editing `.code-spec/*.md` (`specification:mdc`).

## Inputs

- **Required**: `<notion-url-or-id>` — the ticket page, as full URL or 32-hex
  id.
- **Optional**: `--repo=<path>` target repository; `--dry-run` stops after
  the plan report; `--skip-approval` bypasses the human gate; `--use-cache`
  reuses an existing bundle only when it passes the root-file gate below.
- **Prerequisites**: `notion-sync` CLI on PATH with `NOTION_TOKEN` exported,
  and a resolvable working tree for the target repository.

## Workflow

1. Normalize the Notion URL or 32-hex id. Pull the ticket once with
   `notion-sync pull <id> --follow-children --follow-links --out <tmp>` and
   classify its stage by status group plus label keywords — never by exact
   option names, which drift per database:
   - `to_do` + idea/draft/skeleton/review → `not-ready`
   - `to_do` + pending/ready/approved/queued → `ready-to-code`
   - `in_progress` + implementing/in-progress/wip/coding → `implementing`
   - `in_progress` + audit/verify/qa → `auditing`
   - `complete` + implemented/done/shipped/merged → `done`
   - external/archive/wontfix → `out-of-scope`; unmatched → `unknown`
2. Materialize the authoritative bundle through `specification:sync-spec`.
   `--use-cache` is valid only when the bundle contains Markdown **and** the
   non-empty root filename ends with the ticket id; otherwise record a cache
   miss and refresh. Refuse if the same root-file gate fails after refresh or
   immediately before coding.
3. Read local `DRAFT.md`, `PLAN.md`, existing code, and the ticket stage.
   Select exactly one mode; for `unknown`, ask the user to map the stage
   before proceeding. Load only the selected child chain from
   [references/modes.md](references/modes.md).

   | Condition | Mode |
   |---|---|
   | ready-to-code + approved PLAN | `COMMIT_PLAN` |
   | implementing + partial work | `PI_ITERATE` |
   | ready-to-code + no approved PLAN | `DRAFT_THEN_ASK` |
   | auditing | `AUDIT_AND_COMPLETE` |
   | done | `VERIFY_ONLY` |
   | stage and supplied flags contradict | `FLAG_MISMATCH` |
   | not-ready, out-of-scope, or rejected | `REFUSE` |

4. Produce one evidence map covering Spec, DRAFT, PLAN, code, and every
   acceptance feature. Cite bundle headings and code symbols; distinguish
   absent, partial, implemented, and contradictory behavior.
5. Review the proposed contract against current architecture. Fan out only
   when independent reviewer or workflow capability is actually available;
   otherwise perform one soundness pass. For every blocking ambiguity, stop
   and ask. Record the decision through `specification:mdc`, then re-read the
   changed spec. Never guess an architectural decision.
6. Require approval of the resolved mode, scope, feature map, and soundness
   decisions unless `--skip-approval`. `--dry-run` stops after reporting this
   plan.
7. Resolve `repo_path`, verify the working tree, and capture immutable
   `base_rev` before any child runs. Scaffold `DEVIATIONS.md` only for
   code-producing modes. Material deviations are appended using the policy in
   `references/modes.md`; trivial formatter, inferred-type, or documentation
   differences are not logged. After every material deviation, revalidate the
   remaining PLAN dependencies and acceptance map before dispatching dependent
   work. A low-impact reversible departure may continue and be logged; a
   deviation affecting architecture, public API, data model, security/privacy,
   destructive migration, user-visible semantics, or acceptance criteria must
   return `pending_decision` and stop the stale branch.
8. Select the execution mechanism by capability, not preference:
   - When `Workflow` is available and the mode is `COMMIT_PLAN`,
     `PI_ITERATE`, or `AUDIT_AND_COMPLETE`, load
     [references/execute-workflow.md](references/execute-workflow.md) and use
     its fan-out, adversarial-verify, retry loop.
   - Otherwise load the selected sequential chain in
     [references/modes.md](references/modes.md).

   Pass the absolute repo path, root spec pointer, acceptance map, mode, and
   deviation policy to every child; both references carry the dispatch and
   report bounds. Capture `child_dispatch_log` and `commits_landed`. When
   execution returns `pending_decision`, stop, ask the user, persist the
   answer through `specification:mdc`, and resume the same workflow run — do
   not start over or continue past it. Surface any iteration or token guard
   as unresolved and return partial with `coding:handover`.
9. When commits landed, load
   [references/stack-aware-sizing.md](references/stack-aware-sizing.md).
   Measure the aggregate diff from `base_rev`; route oversized splitting
   through the `coding:commit --create-pr` compatibility entrypoint and
   semantic restacking to `coding:push-pr`. Never mutate history or publish
   directly.
10. Run `specification:review-implementation` against the bundle. On P0/P1
    alignment findings, dispatch `coding:fix` and retry alignment — at most
    three passes, after which remaining findings are reported instead of
    looped on. General and security review still run on every pass.
11. For landed code-producing modes, load
    [references/thought-experiment.md](references/thought-experiment.md).
    Run its read-only usage trace at the required capability; if that
    capability is unavailable, report partial rather than silently
    downgrade.
12. Detect a linked Git worktree by comparing common-dir and git-dir. A jj
    workspace is allowed. If a linked Git worktree contains the landed
    commits, ask whether to keep or relocate them; delegate relocation to
    `coding:commit`.
13. Run the verification below; when a check fails, fix the cause and re-run
    that check. Repeat until every check passes or a concrete blocker
    remains, then report the blocker instead of looping.

## Verification

- The root-file gate held at every checkpoint: a non-empty bundle root whose
  filename ends with the ticket id existed before coding began.
- `base_rev` was captured before any child ran, and every diff measurement
  and stack decision derives from it.
- Acceptance evidence exists for every mapped feature; alignment, general,
  and security reviews are clean or their remaining findings are reported.
- Every material deviation records repository or runtime evidence and disposition, and the
  remaining plan was revalidated before dependent work resumed.
- No local history shaping happened outside `coding:commit`, no publication or
  remote restacking happened outside `coding:push-pr`, and no `.code-spec`
  write happened outside `specification:mdc`.

## Completion

Report the outcome in plain language with these facts: final status
(`completed`, `partial`, `refused`, `flagged`, or `dry_run`); ticket id,
stage, and the selected mode with its reason; bundle root path and cache
behavior; `repo_path` and `base_rev`; acceptance coverage with named gaps;
soundness decisions recorded; execution mechanism, children dispatched, and
commits landed; stack-sizing action; alignment verdict with remaining
P0/P1 counts; thought-experiment result; worktree-relocation action; material
deviations; and unresolved items.

`completed` requires an approved contract, verified acceptance evidence,
clean general/security review, clean alignment, and no unresolved decision.
`partial` names the exact failed gate and the continuation artifact.
`refused` names the stage, cache, approval, or capability rule that prevented
execution.
