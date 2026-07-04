<!-- INSTRUCTION: This is the companion template for authoring a Dynamic Workflow — a plain-JS script run by the
     `Workflow` tool. It is a distinct mechanism from an Agent Team (templates/agent-team.md): a workflow is a
     deterministic, resumable script that dispatches agents and coordinates them in code; a team is a set of
     persistent teammates coordinating conversationally. Only the main session can launch a Workflow — a
     spawned subagent or a teammate never calls `Workflow` itself; if a nested step needs workflow-style
     fanout+verify, that decision is made once, at the top, by the main session. -->

# Dynamic Workflow — Template

## When to reach for this

A Dynamic Workflow earns its complexity when the task has: (a) work that decomposes into independently-runnable
slices, (b) a scoring/verification step that should not trust its own generator, and (c) a bounded correction
loop that needs to survive a crash or a mid-run pause for user input. If the task is a single linear chain with
no fanout and no adversarial check, this is over-engineering — use a plain sequential dispatch instead
(Mechanism B below is exactly that fallback, and is also the right choice when the `Workflow` tool is
unavailable or disabled).

The launch shape is two-phase: the main session first plans architecture and direction with explore agents, then
hands off to the workflow, which consts the goal and spec every later step reads (see The spec const). Planning is
not a workflow phase — it is the step that decides a workflow is the right substrate and fixes what its spec says.

## Meta block

Every workflow script exports a `meta` object naming itself and its args — this is what the main session passes
in when it initiates the run, and what `resumeFromRunId` replays against:

```js
export const meta = {
  name: '<workflow-name>',
  description: '<one line: what this workflow does, phase names included>',
  args: ['<arg1>', '<arg2>', 'resume_state', 'seed'],
};
```

- No `Date.now()` / `Math.random()` inside the workflow body — the runtime requires determinism so the cached
  prefix replays identically on resume. Pass timestamps and seeds in as args from the main session.
- `resume_state` is always one of the args if the workflow can be interrupted by a `pending_decision` — it
  carries whatever the workflow needs to pick up mid-run (round/step index, survivors, best-so-far).

## The spec const — the workflow's own contract

Before the phases, define a `spec` const (or accept it as an arg) that pins down what the phases below assume:
the slice/round unit, the fanout bounds, the stop conditions, and any immutable paths agents must not touch. This
is the single object every phase reads from — phases never hardcode a number the spec should own.

```js
const spec = {
  slicing: '<how work is decomposed into independently-runnable units>',
  fanout: { initial: 4, min: 2, max: 8 },
  budget: { max_rounds: 6 },          // or max_iterations, whichever unit fits
  stop: { target: '<threshold>', plateau: { rounds: 2, epsilon: 0.02 } },
  immutable_paths: ['<paths agents must never touch — a touch disqualifies the slice>'],
};
```

## Pipeline vs parallel — pick per phase, not once for the whole workflow

- **Parallel** (`parallel(items.map((x) => agent({...})))`) is the default for any phase whose units are
  independent and sibling-blind by design — generation across slots, N judges scoring one candidate, N
  implementation agents on N non-overlapping slices. Sibling-blindness is a correctness property, not an
  optimization: judges/generators that could see siblings would collapse the diversity the phase exists to
  produce.
- **Pipeline** (sequential, one step feeding the next) is required when steps share mutable state that races
  under parallelism — history rewrites replaying onto the previous step's result (`finalize-commits`'s per-commit
  walk), or any chain where step N's output is step N+1's only input. Default to pipeline when in doubt about a
  race; the cost is wall-clock, not correctness, and wall-clock is the cheaper thing to spend.
- A single workflow commonly mixes both: parallel Generate feeding a pipeline'd Verify-then-Evolve tail.

## Shared-context generator (first stage)

When the editor/verifier prompts depend on files or web context that every slice needs, don't bake that reading
into each worker — make the workflow's FIRST stage a generator subagent that reads the shared context once and
emits one ready-to-run prompt per slice. Later stages consume those prompts; the orchestrator never loads the raw
context itself, and every worker gets a self-contained prompt. This is the two-stage dispatch pattern
(`plugins/coding/CLAUDE.md`, "Two-Stage Dispatch") realized as a workflow phase: generate the prompts with a
subagent, keep the orchestrator's context clean, and let the deterministic script fan them out.

## Editor + verifier stages

The two-stage pattern that gives a workflow its adversarial teeth:

- **Editor stage** (Fanout / Generate / Implement): agents that produce — write code, draft a candidate, take an
  action. They never score their own output. On a slice needing a decision the spec does not resolve, an editor
  emits a `pending_decision` and returns `blocked` rather than guessing.
- **Verifier stage** (Verify / Score / Refute): agents whose ONLY job is to attempt to disprove the editor's
  claim of success — a missing case, a broken contract, gamed metric, a harness bug. A verifier receives the
  editor's artifact and the spec claim ONLY — never the editor's reasoning, so it cannot inherit the editor's
  blind spots. A verifier that cannot produce a concrete refutation (file:line, reproducible failure) must
  accept; suspicion alone never refutes. On refutation it returns the defect, the exact spec criterion the defect
  breaks (file:line), and the minimal fix — that triplet is what the bounded correction loop re-queues to the
  editor. Verifiers never see sibling candidates or sibling verifier verdicts — independence is structural (a
  separate `agent()` dispatch per verifier), not a promise made in the prompt.
- The orchestrator (the workflow script itself) never generates or verifies — it dispatches, persists, and
  computes the deterministic parts (ranking, stop-checks, next-round breeding). If the orchestrator is writing
  code or judging quality inline, that logic belongs in a dispatched agent instead.

## Bounded correction loop

Refuted/failed units are re-queued to the editor stage with the verifier's rationale attached, and retried — but
never unboundedly:

```js
for (let pass = 1; pass <= spec.budget.max_correction_passes; pass += 1) {
  const verdict = await agent({ model: 'opus', task: verifyPayload(unit) });
  if (verdict.verdict === 'accepted') break;
  log(`pass ${pass}: ${unit.id} refuted — ${verdict.rationale}`);
  disqualified.push({ id: unit.id, reason: verdict.rationale });
  if (pass === spec.budget.max_correction_passes) log(`correction-pass bound tripped for ${unit.id}`);
}
```

Every bound that trips — fanout clamp, `max_rounds`, `max_correction_passes`, plateau — is `log()`-ed. **No
silent caps**: a workflow that quietly stops short without saying which bound tripped and why is broken, not
lenient.

## Convergence predicates — whichever-first, always named

A workflow's stop check is always a named, checkable disjunction, never an implicit fallthrough:

```js
function stopCheck(spec, state) {
  if (state.best.score >= spec.stop.target) return { status: 'target_met', reason: `target ${spec.stop.target} reached` };
  if (state.round >= spec.budget.max_rounds) return { status: 'budget_exhausted', reason: `max_rounds=${spec.budget.max_rounds} spent` };
  if (plateaued(state, spec.stop.plateau)) return { status: 'plateau', reason: `no ${spec.stop.plateau.epsilon} improvement in ${spec.stop.plateau.rounds} rounds` };
  return null;
}
```

## The `pending_decision` contract — the one thing a workflow cannot do itself

Workflows cannot take mid-run user input. When any dispatched agent surfaces a decision the spec cannot resolve,
the workflow stops and returns rather than guessing:

```yaml
pending_decisions:
  - unit_id: '<id>'
    spec_loc: '<where in the spec this is ambiguous>'
    question: '<the decision needed>'
    options: ['<option A>', '<option B>']
    rationale: '<why the workflow cannot resolve this itself>'
```

The main session (never a subagent) asks the user via `AskUserQuestion`, records the answer wherever the task's
source of truth lives, then resumes via `Workflow resumeFromRunId` — the cached prefix replays completed
steps/rounds instantly.

## Structured return shape

Every workflow returns one shape regardless of which stop condition fired, so the caller never branches on
workflow internals:

```yaml
status: target_met|budget_exhausted|plateau|pending_decision
stop_reason: '<one line naming exactly which bound tripped>'
units_completed: [ ... ]
pending_decisions: []            # non-empty only when status: pending_decision
disqualified:
  - { id: '<unit id>', reason: '<verifier rationale>' }
```

## Illustrative skeleton

```js
export const meta = {
  name: '<workflow-name>',
  description: 'Fanout → Verify → Evolve until target/budget/plateau',
  args: ['input', 'resume_state', 'seed'],
};

export default async function ({ input, resume_state, seed }, { agent, parallel, log }) {
  let round = resume_state?.round ?? 1;
  let units = resume_state?.units ?? seedUnits(input, seed);
  const disqualified = [];

  while (round <= spec.budget.max_rounds) {
    // Editor stage — parallel, sibling-blind
    const produced = await parallel(units.map((u) => agent({ model: 'opus', task: editorPayload(u) })));

    // Verifier stage — independent dispatch per unit, never sees siblings
    const verified = await parallel(produced.map((p) => agent({ model: 'opus', task: verifierPayload(p) })));

    // Bounded correction loop for anything refuted (see above) — omitted here for brevity

    const stop = stopCheck(spec, { round, best: rank(verified)[0] });
    if (stop) { log(`stop: ${stop.reason}`); return { ...stop, units_completed: verified, pending_decisions: [], disqualified }; }

    units = evolveUnits(verified, spec);   // pure computation — the orchestrator may compute, never generate/score
    round += 1;
  }
  return { status: 'budget_exhausted', stop_reason: `max_rounds=${spec.budget.max_rounds}`, units_completed: [], pending_decisions: [], disqualified };
}
```

## Mechanism B — the fallback this template always needs a sibling for

Any Dynamic Workflow design in this template must ship with a Mechanism B: the identical Editor → Verifier →
bounded-correction → stop-check semantics, driven inline by the main session with `Task`/`Agent` dispatches
instead of `agent()`/`parallel()`, and `AskUserQuestion` used natively instead of a `pending_decision` stop/resume
round-trip. Mechanism B is selected when the `Workflow` tool is unavailable/disabled, or when the verifier
backend needs per-unit human input (a workflow round-trips a stop/resume per pause; inline asking natively is
strictly cheaper for that case).
