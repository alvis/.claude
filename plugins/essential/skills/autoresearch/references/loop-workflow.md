# Research Loop — mechanism detail

This reference holds the two loop mechanisms Step 5 of `autoresearch` selects between. SKILL.md owns the mechanism
gate and the Step 6 stop→ask→resume handling; this file owns the loop internals — the shared agent prompt blocks,
the four round phases, the structured return, the `pending_decision` contract, and the inline fallback. Read the
shared prompt blocks plus the section matching the mechanism the gate selected.

Both mechanisms share one contract:

- **The orchestrator NEVER generates or scores candidates.** Every artifact comes from a Generate agent; every
  score from a Score agent (or the human). The orchestrator — and in Mechanism A the workflow script — coordinates,
  persists, and computes Evolve. Nothing else.
- **Judge independence is absolute.** A scorer sees the rubric and ONE candidate — never sibling candidates,
  sibling scores, other judges' verdicts, or the leaderboard. Full rules in `references/eval-backends.md`.
- **The eval harness is immutable to candidates.** The eval command/script is auto-appended to
  `search_space.immutable_paths` at brief time; any candidate that touches it is disqualified on sight.
- **No silent caps.** Every bound that trips — refute-pass limit, fanout clamp, `budget.max_rounds`, `plateau` —
  is `log()`-ed (Mechanism A) or stated inline (Mechanism B) and surfaced in the return (`stop_reason`,
  `disqualified[]`). The loop never quietly stops short.
- **Every round artifact persists under `rounds/round-NN/` the moment it exists** (schemas in
  `references/dossier.md`), so any run — crashed, stopped, or exhausted — is resumable from disk alone.

## Mechanism gate

- **Mechanism A — dynamic `Workflow` tool**: when the `Workflow` tool is available AND `eval.backend` ∈
  {`programmatic`, `judges`}. These backends score without user input, so whole rounds run unattended.
- **Mechanism B — sequential inline**: when `Workflow` is unavailable/disabled, OR `eval.backend: human`. Human
  scoring needs per-round user input; under A every round would stop and resume — workable via `pending_decision`
  but strictly worse, so B is preferred for the human backend even when `Workflow` exists.

---

## Detailed mechanism files

Read the shared prompts first, then the selected mechanism:

1. [Shared generator, judge, and refuter prompts](loop-workflow/10-agent-prompts.md)
2. [Mechanism A — dynamic Workflow](loop-workflow/20-dynamic-workflow.md), or
   [Mechanism B — sequential fallback](loop-workflow/30-sequential-fallback.md)

Both mechanisms use the same prompts and persistence contract. Do not combine
their orchestration procedures in one run.
