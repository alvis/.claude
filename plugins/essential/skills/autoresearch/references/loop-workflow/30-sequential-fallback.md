# Sequential fallback mechanism

## Mechanism B — sequential fallback

Identical round semantics, driven inline by the orchestrator. Per round:

1. **Generate** — dispatch all `fanout.current` generator agents as parallel `Task` calls in ONE message, each
   carrying the Candidate Generator prompt block with its own slot filled in (round 1: one slot per framing
   direction; later rounds: the genome Evolve bred per `references/evolution.md`). Same models, same worktree
   rules, same persisted outputs as Mechanism A.
2. **Score** — dispatch Score agents in parallel per `references/eval-backends.md`. Judges remain independent
   because each judge is a separate `Task` carrying the Independent Judge prompt block (rubric + one candidate,
   nothing else); independence is structural, not promised. **Human scoring** runs as native `AskUserQuestion`
   batteries per round, `eval.human.per_round_batch` candidates per battery, answers written to
   `rounds/round-NN/scores.yaml` — this is why B is preferred for the human backend.
3. **Verify** — the same refute pass: the Adversarial Refuter prompt block dispatched on the winner,
   disqualify-and-promote on refutation, max 3 passes, bound trip stated in the round-log and final report.
4. **Evolve** — the orchestrator computes it itself (it may compute — it never generates or scores): append the
   round-log, update the leaderboard, run the whichever-first stop checks, breed the next genome and fanout per
   `references/evolution.md`.

```
state = resume_state ?? seed_from(brief)            # round, slots, fanout, best
while state.round <= brief.budget.max_rounds:
    candidates = Task[](generate slots)             # ONE message, parallel, sibling-blind
    scores     = backend switch:
        programmatic → Task[](haiku eval per candidate, parallel)
        judges       → Task[](>=3 opus judges per candidate, parallel, minimal payloads)
        human        → AskUserQuestion batteries of eval.human.per_round_batch
    ranked     = refute_loop(rank(scores))          # max 3 passes; every trip logged
    persist candidates/, scores.yaml, verify.yaml, round-log.md
    if target ∨ budget ∨ plateau: break             # reason surfaced, never silent
    state.slots, state.fanout = evolve(ranked)      # orchestrator computes; never generates
    state.round += 1
```

Same stop checks, same persisted files under `rounds/round-NN/` — a Mechanism B run is resumable from `rounds/`
state via `--resume` exactly as a Mechanism A run is via `resumeFromRunId`.
