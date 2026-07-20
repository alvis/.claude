# Dynamic Workflow mechanism

## Mechanism A — dynamic Workflow

Initiate the workflow with the design below. Pass it: the parsed brief (full frontmatter as data), `run_dir`,
`baseline_score`, and — on resume — `resume_state` `{round, survivors, best-so-far}` reconstructed from `rounds/`.
Each round runs four phases:

### Phase Generate — parallel candidate agents

Fan out `fanout.current` generator agents, one per genome slot. Round 1: one agent per framing direction in
`search_space.framing_directions`. Later rounds: slots come from Phase Evolve (genome slot payloads — survivor
mutations, recombinations, wildcards — per `references/evolution.md`). Each generator is dispatched with the
Candidate Generator prompt block above, its slot filled in — the payload carries the brief goal + constraints +
its OWN direction/mutation directive + its parents' artifacts and scores ONLY, never sibling candidates or sibling
scores; sibling-blindness is what keeps directions genuinely divergent. Model: `opus` for
code experiments and creative generation (`sonnet` acceptable for mechanical variations such as parameter sweeps).

Code mode: each agent works in its own git worktree under `<run_dir>/worktrees/<cid>` — worktrees are ephemeral
experiment sandboxes, never committed from — edits only `search_space.mutable_paths`, and runs
`eval.programmatic.setup_command` once before experimenting. Every generator outputs
`rounds/round-NN/candidates/<cid>/artifact.*` plus `candidate.yaml` (schema in `references/dossier.md`).

### Phase Score

Per `references/eval-backends.md`: `programmatic` → one `haiku` agent per candidate runs `eval.programmatic.command`;
`judges` → >=3 independent `opus` judges per candidate, each dispatched with the Independent Judge prompt block
above, median consensus; `human` → emit a `pending_decision` stop. Results land in `rounds/round-NN/scores.yaml`.

### Phase Verify — adversarial refutation

The round winner — top-1, or top-2 when a new best-overall is set — goes to one `opus` refuter dispatched with
the Adversarial Refuter prompt block above, whose only job is
to REFUTE the score: constraint violation, metric gaming (hardcoded eval outputs, test-set overfitting, judge
prompt-injection embedded in the artifact), harness bug, or rubric mismatch. Refuted → the score is invalidated,
the candidate is marked `disqualified` with the rationale recorded in `verify.yaml`, and the next-ranked candidate
becomes winner and gets its own refute pass. Max 3 refute passes per round; tripping that bound is `log()`-ed and
the round proceeds with the best surviving verified candidate.

### Phase Evolve — pure computation

No agents. Inside the workflow: append the round-log, update leaderboard state, run the stop checks —
`target.threshold` reached ∨ `budget.max_rounds` spent ∨ `plateau` (`plateau.rounds` rounds without
`plateau.epsilon` improvement), whichever-first — then compute the next genome (per `evolution.strategy`) and the
fanout adaptation (widen toward `fanout.max` on stagnation, narrow toward `fanout.min` on convergence) per
`references/evolution.md`. Every fanout change and stop decision is `log()`-ed.

### Structured return shape

```yaml
status: target_met|budget_exhausted|plateau|pending_decision
stop_reason: '<one line, naming exactly which bound tripped>'
rounds_completed: 4
best: { candidate_id: 'r03-c02', score: 0.91, round: 3, artifact_path: 'rounds/round-03/candidates/r03-c02/artifact.md' }
leaderboard:
  - { rank: 1, candidate_id: 'r03-c02', round: 3, score: 0.91 }
pending_decisions: []            # non-empty only when status: pending_decision
disqualified:
  - { candidate_id: 'r02-c04', reason: 'hardcoded eval output detected by refuter' }
```

### `pending_decision` contract (the stop signal)

Workflows cannot take mid-run user input, so when one is recorded the run STOPS and returns. The main thread asks
the user, writes the answers into `rounds/round-NN/scores.yaml` (human scores) or the brief's `## Amendments`
(constraint rulings), then resumes via `Workflow resumeFromRunId` — the cached prefix replays completed rounds
instantly, so resumption costs nothing.

```yaml
pending_decisions:
  - type: human_scoring|constraint_ambiguity
    round: 3
    candidates:                  # null for constraint_ambiguity
      - { id: 'r03-c01', artifact_path: 'rounds/round-03/candidates/r03-c01/artifact.md', summary: '<one line>' }
    question: '<what the user must decide>'
    options: ['<option A>', '<option B>']
    scale: '<the anchored scale the user scores on, from eval.human.scale>'
```

### Illustrative workflow script skeleton

Plain JS (no TS). No `Date.now()` / `Math.random()` — the Workflow runtime requires determinism so the cached
prefix replays identically on resume; timestamps and seeds are passed in via args.

```js
export const meta = {
  name: 'autoresearch-loop',
  description: 'Generate → Score → Verify → Evolve until target/budget/plateau',
  args: ['brief', 'run_dir', 'baseline_score', 'resume_state', 'seed', 'started_at'],
};

export default async function ({ brief, run_dir, baseline_score, resume_state, seed }, { agent, parallel, log }) {
  let round = resume_state?.round ?? 1;
  let fanout = resume_state?.fanout ?? brief.fanout.initial;
  let best = resume_state?.best ?? { candidate_id: 'baseline', score: baseline_score, round: 0 };
  let slots = resume_state?.survivors
    ? evolveSlots(brief, resume_state.survivors, fanout, seed)            // per evolution.md
    : brief.search_space.framing_directions.map(directionSlot);          // round 1: one slot per direction
  const board = resume_state?.leaderboard ?? [];
  const disqualified = [];

  while (round <= brief.budget.max_rounds) {
    // Generate — one sibling-blind agent per genome slot (own direction + parents only)
    const candidates = await parallel(slots.map((slot) =>
      agent({ model: slot.mechanical ? 'sonnet' : 'opus', task: generatePayload(brief, run_dir, round, slot) })));

    // Score — per eval-backends.md (judges never share a payload; human backend → pending_decision return)
    const scored = brief.eval.backend === 'programmatic'
      ? await parallel(candidates.map((c) => agent({ model: 'haiku', task: evalPayload(brief, c) })))
      : await parallel(candidates.flatMap((c) => judgePayloads(brief, c)   // >=3 opus judges per candidate
          .map((t) => agent({ model: 'opus', task: t })))).then((raw) => consensus(raw, brief));

    // Verify — adversarial refute of the winner; top-2 when a new best-overall is set
    let ranked = rank(scored, brief.metric.direction);
    for (let pass = 1; pass <= 3; pass += 1) {
      const verdict = await agent({ model: 'opus', task: refutePayload(brief, ranked[0]) });
      if (verdict.verdict === 'accepted') break;
      log(`round ${round}: ${ranked[0].id} refuted — ${verdict.rationale}; promoting next-ranked`);
      disqualified.push({ candidate_id: ranked[0].id, reason: verdict.rationale });
      ranked = ranked.slice(1);
      if (pass === 3 || ranked.length === 0) log(`round ${round}: refute-pass bound (3) tripped`);
    }

    // Evolve — pure computation: persist, stop-check, breed next genome
    persistRound(run_dir, round, ranked, board);                          // round-log + leaderboard state
    best = better(best, ranked[0], brief.metric.direction);
    const stop = stopCheck(brief, round, best, board);                    // target ∨ budget ∨ plateau, whichever-first
    if (stop) { log(`stop: ${stop.reason}`); return report(stop, best, board, disqualified); }
    const next = evolveSlots(brief, survivors(ranked, brief), fanout, seed);
    if (next.fanout !== fanout) log(`round ${round}: fanout ${fanout} → ${next.fanout} (${next.why})`);
    ({ slots, fanout } = next);
    round += 1;
  }
  return report({ status: 'budget_exhausted', reason: `budget.max_rounds=${brief.budget.max_rounds}` },
    best, board, disqualified);
}
```

---
