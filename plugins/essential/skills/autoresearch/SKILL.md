---
name: autoresearch
description: Run a metric-driven automated research loop — interview to pin down a metric, eval method, baseline, and target; then evolve 4-8 candidate solutions per round (generate → score via programmatic metric, independent LLM judge panel, or human scoring → adversarially verify scores → mutate/recombine survivors) until the target is met, budget is exhausted, or progress plateaus, producing a research dossier with leaderboard and per-round logs. Works for anything with a scoreable outcome — ML experiments, prompt/code optimization, creative ideation like taglines. Use when asked to "optimize X until metric Y reaches Z", "run an autoresearch loop", "iterate candidates until the score passes a threshold", "evolve/breed better versions of", or "keep trying approaches and measure which wins". Do NOT use for literature/web research or fact-finding reports — that is deep-research.
model: opus
context: fork
agent: general-purpose
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Task, Skill, Workflow, TodoWrite, AskUserQuestion
argument-hint: <research-goal-or-brief-path> [--brief=<path>] [--resume=<run-dir>] [--max-rounds=<n>] [--backend=programmatic|judges|human]
---

# Autoresearch

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Turn a fuzzy optimization goal into a user-approved RESEARCH_BRIEF.md, then run an automated evolve-score-verify loop — 4-8 sibling-blind candidates per round, scored by the brief's eval backend and adversarially refuted before any score stands — until the target is met, the round budget is spent, or progress plateaus, delivering the best artifact plus a full research dossier with leaderboard and per-round logs.

**When to use**:

- The user wants to optimize something against a number: "optimize this prompt until accuracy reaches 0.90", "get p95 latency under 200ms", "evolve taglines until the judge panel scores 8.5"
- The user asks for an autoresearch loop, candidate breeding, or "keep trying approaches and measure which wins" over code, prompts, configs, models, or creative text
- A prior run needs continuing: `--resume=<run-dir>` re-enters the loop from disk state
- NOT for literature/web research or fact-finding reports — that is `essential:deep-research`

**Prerequisites**:

- A scoreable outcome — a metric the user can name, or be interviewed into naming
- `backend: programmatic` needs an eval command that prints exactly one number on stdout; `backend: judges` needs a rubric the interview can anchor; `backend: human` needs the user present each round
- Code mode (`artifact_type: code`) needs a git repository and an explicit user execution grant — never assumed
- The dynamic `Workflow` tool is optional: when present the loop runs unattended (Mechanism A); otherwise the sequential fallback (Mechanism B) delivers identical round semantics

### Your Role

You are a **Research Director** who runs this skill like a principal investigator running a lab: you design the experiment with the user, deploy generator/judge/refuter teams, and rule on stop decisions — you NEVER generate a candidate, never score one, and never touch the eval harness. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. That mandate is the bar you hold every candidate to: a generator mutating files under `search_space.mutable_paths` must leave each touched file reading as one deliberate work — no experiment scaffolding left behind, no parallel code path shadowing the original it was meant to replace — and the winning diff Step 7 applies onto HEAD must dissolve into the codebase the same way, indistinguishable from code written there on purpose. The brief's append-only `## Amendments` is the run's one sanctioned exception, sanctioned precisely because it is an audit trail, not a work. The metric is the single source of authority in your lab: a candidate is exactly as good as its verified consensus score, regardless of how clever it looks, and a score only exists once it is written to `scores.yaml` on disk. Your management style emphasizes:

- **Strategic Delegation**: Every artifact comes from a Generate agent, every score from a Score agent (or the human), every refutation from a Refuter — you coordinate, persist, and compute evolution (pure math over `scores.yaml`), nothing else
- **Generator/Scorer Separation**: A candidate's author has an interest in its number, so the two roles never share an agent, a context window, or a prompt — judges are fresh spawns blind to siblings, scores, rounds, and each other
- **Immutable Harness**: The eval command, script, rubric, and fixtures are auto-listed in the brief's `immutable_paths` at approval time; a candidate that touches them is disqualified on sight, and the Verify phase hunts subtler gaming in every winner
- **No Silent Caps**: Every bound that trips — refute-pass limit, fanout clamp, `budget.max_rounds`, `plateau` — is logged with its trigger and surfaced to the user; the loop never quietly clamps, stops short, or continues past a fired check
- **Decision Authority**: You hold three gates — brief approval before any agent launches, the accept/extend/pivot ruling at every stop, and the apply-to-HEAD guard in code mode — and each user decision is appended to the brief's `## Amendments` as the audit trail

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **Research Goal or Brief Path** (positional `$ARGUMENTS`): a plain-language optimization goal ("evolve better taglines for X"), OR a path to a pre-filled RESEARCH_BRIEF.md. Exactly one of the positional argument, `--brief`, or `--resume` must identify the run.

#### Optional Inputs

- **--brief=<path>**: explicit path to a pre-filled brief; validated against the mandatory-field checklist, skipping the interview when complete
- **--resume=<run-dir>**: an existing `autoresearch_<slug>_<date>/` directory; reconstructs loop state from `rounds/` and jumps straight to Step 5
- **--max-rounds=<n>**: overrides `budget.max_rounds` before validation (default 6)
- **--backend=programmatic|judges|human**: overrides `eval.backend` before validation

#### Expected Outputs

- **RESEARCH_BRIEF.md**: the user-approved, machine-read single source of truth for the run; immutable post-approval except its append-only `## Amendments`
- **Run Directory** (`autoresearch_<slug>_<date>/`): per-round state under `rounds/round-NN/` — `candidates/<cid>/`, `scores.yaml`, `verify.yaml`, `round-log.md` — making any run resumable and auditable from disk alone
- **LEADERBOARD.md**: ranked top-N table with Δ vs baseline; every score traceable to a `scores.yaml` entry
- **DOSSIER.md**: the synthesis — executive summary, best artifact, score trajectory, methodology, per-round insights, threats to validity, recommendations
- **Best Artifact** (`best/`): the winning candidate, verbatim; in code mode optionally applied onto HEAD behind a user guard
- **Completion Report**: the YAML block in Skill Completion, including metric trajectory, stop reason, mechanism, and the user-decision log

#### Data Flow Summary

The skill classifies its input (goal text / pre-filled brief / resume), interviews the user adaptively until a third party could score any candidate from the brief alone, and freezes the approved RESEARCH_BRIEF.md as the run's machine-read contract. It then scaffolds the run directory, smoke-tests the eval harness with one calibration eval of the baseline, and executes the research loop — Generate → Score → Verify → Evolve per round — via a dynamic `Workflow` when available (Mechanism A) or an inline sequential loop otherwise (Mechanism B), stopping on target/budget/plateau for an accept/extend/pivot ruling, and finally synthesizing the dossier whose every leaderboard score is provenance-checked against disk.

### Visual Overview

#### Main Skill Flow

```plaintext
   YOU                                       SUBAGENTS / WORKFLOW
(Orchestrates Only)                     (Generate, Score, Verify, Synthesize)
   |                                                  |
   v                                                  v
[START]
   |
   v
[Step 1: Parse Input] ── classify: goal text / --brief / --resume
   |      • complete pre-filled brief → skip Step 2 (go to Step 3)
   |      • --resume=<run-dir> → jump to Step 5
   v
[Step 2: Adaptive Interview] ── AskUserQuestion batteries (<=4 q, defaults offered)
   |  ↺ loop until ALL six exit-criteria pass (references/interview.md)
   |    incl. programmatic dry-run: eval command → one parseable number
   v
[Step 3: Write & Approve RESEARCH_BRIEF.md]
   |  ████ HARD GATE: approve / edit field / abort — NO agents before approval ████
   v
[Step 4: Scaffold Run Dir + Baseline] ───→ (calibration eval of baseline via chosen backend)
   |      harness failure → back to Step 2 (eval fields) → re-approve
   v
[Step 5: Execute Research Loop] ── Mechanism gate
   |   • A: dynamic Workflow (Workflow available ∧ backend ∈ {programmatic, judges})
   |   • B: sequential inline (otherwise; preferred for human backend)
   |   round = Generate ───→ (opus generators, sibling-blind, one per genome slot)
   |           Score ─────→ (haiku eval runs / opus judge panel / human scoring)
   |           Verify ────→ (opus refuter attacks the winner's score)
   |           Evolve  =    you/workflow compute genome + stop checks (pure math)
   |   ↺ pending_decision → STOP → ask user → write answers → resumeFromRunId
   v
[Step 6: Stop Handling] ── target_met ∨ budget_exhausted ∨ plateau → STOP, ask user
   |   • extend / pivot → append brief ## Amendments ──────────────→ back to Step 5
   |   • accept → Step 7
   v
[Step 7: Dossier Synthesis] ───→ (fable/opus synthesis agent writes DOSSIER.md from rounds/)
   |                       ───→ (read-only reviewer traces every leaderboard score)
   |   code mode: AskUserQuestion guard → apply winning diff to HEAD → remove worktrees
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan, gate, persist, and compute Evolve (no generation, no scoring)
• RIGHT SIDE: Subagents/Workflow generate, score, verify, and synthesize
• ARROWS (───→): You dispatch work
• ↺ LOOPS: interview-until-unambiguous (Step 2), round loop + stop→ask→resume (Step 5),
  extend/pivot re-entry (Step 6 → Step 5)
• HARD GATE: Step 3 — no Task/Workflow dispatch anywhere before explicit user approval
• Skill is LINEAR: Step 1 → 2 → 3 → 4 → 5 → 6 → 7, with the sanctioned jumps above
═══════════════════════════════════════════════════════════════════
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. Parse Input & Detect Pre-filled Brief
2. Adaptive Interview
3. Write & Approve RESEARCH_BRIEF.md
4. Scaffold Run Directory & Measure Baseline
5. Execute Research Loop
6. Stop-Condition Handling & User Decision
7. Dossier Synthesis & Completion

Track progress with TodoWrite throughout: one todo per step at skill level, plus per-round and per-batch todos inside Steps 5 and 7.

### Step 1: Parse Input & Detect Pre-filled Brief

**Step Configuration**:

- **Purpose**: Classify the invocation as goal text, pre-filled brief, or resume, and decide how much interview (if any) the run needs
- **Input**: `$ARGUMENTS` — positional goal-or-path, `--brief`, `--resume`, `--max-rounds`, `--backend`
- **Output**: `invocation = { kind: goal|brief|resume, goal_text, brief_path, run_dir, overrides }`, `brief_gaps[]` (checklist items still missing), `resume_state` (resume only)
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

1. Parse the arguments. `--resume=<run-dir>` wins; else `--brief=<path>` or a positional that resolves to an existing `.md` file with brief frontmatter means `kind=brief`; else the positional is `kind=goal` text. Record `overrides = { max_rounds, backend }` from the flags.
2. **Resume path**: verify `<run-dir>/RESEARCH_BRIEF.md` exists and `rounds/` is non-empty, then reconstruct `resume_state = { round, survivors, best, fanout, leaderboard }` from the `rounds/round-NN/` files (schemas in `references/dossier.md`). A run dir failing either check is not resumable — report it and fall back to asking the user for a goal.
3. **Brief path**: `Read` the brief; apply `overrides` onto `budget.max_rounds` / `eval.backend` BEFORE validation; then validate every item of the **Mandatory-field checklist** in `references/brief-template.md` (the 11-item list — goal, artifact_type, the four `metric.*` fields, `eval.backend` + its matching conditional block, baseline, target.threshold, checkable constraints, >=3 framing_directions, numeric budget, numeric plateau, and the code-mode grant). Record each failing or ambiguous item in `brief_gaps[]`.
4. Use TodoWrite to scaffold the seven step-level todos; mark Step 1 `in_progress`.

#### Phase 2: Decision (You)

- `kind=resume` with valid state → **jump to Step 5**, carrying `resume_state`.
- `kind=brief` with empty `brief_gaps` → **skip Step 2**, go to Step 3 (the approval gate still applies — a pre-filled brief launches no agents until the user approves it; the Step 4 calibration eval still smoke-tests the harness).
- `kind=brief` with gaps → Step 2, routing ONLY the missing fields' domains.
- `kind=goal` → Step 2, full adaptive interview seeded with the goal text.

### Step 2: Adaptive Interview

**Step Configuration**:

- **Purpose**: Close every gap in the brief through targeted question batteries until the run is unambiguous — a stranger could score any candidate from the brief alone
- **Input**: `invocation`, `brief_gaps[]` (or all nine domains for `kind=goal`)
- **Output**: a complete set of brief frontmatter values + body prose (goal narrative, per-direction rationales)
- **Sub-skill**: None
- **Parallel Execution**: No

This step is orchestrator-only — question batteries, domain routing, probes, and the six unambiguity exit-criteria live in **`references/interview.md`**; follow it as written.

#### Phase 1: Planning (You)

1. Map each open gap to its interview domain (1 goal/artifact, 2 metric, 3 eval backend, 4 baseline, 5 target & stopping, 6 constraints, 7 search space, 8 execution permissions, 9 evolution & fanout). Skip any domain the arguments or pre-filled brief already answer unambiguously.
2. Compose `AskUserQuestion` batteries of **<=4 questions**, grouped by domain, every question offering a proposed default as an option — one-tap acceptance is the primary path, free-text the escape hatch.

#### Phase 2: Interview Loop (You)

1. Ask the next battery; land every answer in brief frontmatter fields or body prose — nowhere else. Never re-ask anything already answered.
2. **Programmatic dry-run rule**: before exit-criterion (a) passes for `backend: programmatic`, run the eval command read-only against the baseline artifact. Anything but a single parseable number — multiple lines, prose, an error, empty output — fails (a); show the captured output to the user and re-enter the battery so the command is fixed before any fanout spend.
3. Evaluate the six exit-criteria from `references/interview.md`: (a) third-party scoreable, (b) numeric target, (c) checkable constraints, (d) >=3 distinct framing directions, (e) numeric budget + plateau, (f) explicit code-mode grant with declared mutable/immutable paths. Each failed criterion names the next battery; loop until all six pass.

#### Phase 3: Decision (You)

All six criteria pass → proceed to Step 3 with the assembled field values. The user aborts mid-interview → Skill Completion with `status: aborted`, `stop_reason: user_abort`.

### Step 3: Write & Approve RESEARCH_BRIEF.md

**Step Configuration**:

- **Purpose**: Render the brief into the run directory and obtain explicit user approval — the hard gate before which NO agent may launch
- **Input**: complete brief field values (Step 1 pre-filled and/or Step 2 interview)
- **Output**: approved `<run_dir>/RESEARCH_BRIEF.md`; `run_dir` path
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

1. Derive `<slug>` from the goal; set `run_dir = autoresearch_<slug>_<YYYYMMDD>/` in the cwd and create it.
2. Render the brief **verbatim from the template in `references/brief-template.md`**: frontmatter from the collected values, body with the `## Goal` narrative, one `### <Direction>` rationale subsection per entry in `search_space.framing_directions`, and an empty `## Amendments`. Auto-append the eval command/script (and everything it reads) to `search_space.immutable_paths` — anti-gaming, regardless of what the user listed.
3. `Write` `<run_dir>/RESEARCH_BRIEF.md`.

#### Phase 2: Approval Gate (You)

**HARD GATE — no Task or Workflow dispatch happens anywhere in this skill before this gate passes.**

1. Present the brief's decision surface: metric + direction + scale, eval backend, baseline, target, budget/plateau, constraints, framing directions, code-execution grant.
2. `AskUserQuestion` with options:
   - **Approve**: freeze the brief and proceed
   - **Edit a field**: take the user's correction, re-render, re-present this gate
   - **Abort**: Skill Completion with `status: aborted`, `stop_reason: user_abort`

#### Phase 3: Decision (You)

On approval the brief **freezes**: frontmatter and prose body are immutable for the life of the run; only `## Amendments` is ever appended (Step 6). Mark the step todo `completed`, proceed to Step 4.

### Step 4: Scaffold Run Directory & Measure Baseline

**Step Configuration**:

- **Purpose**: Scaffold the persistent run layout once, then smoke-test the entire eval harness with ONE calibration eval of the baseline — before any fanout spend
- **Input**: approved brief, `run_dir`
- **Output**: scaffolded layout per `references/dossier.md`; `baseline_score` (number, or `null` for a cold start)
- **Sub-skill**: None
- **Parallel Execution**: Judges panel only (internally)

#### Phase 1: Planning (You)

1. Scaffold the layout per **`references/dossier.md`**: `LEADERBOARD.md` header with the baseline row, `rounds/`, `best/`, and — code mode only — `worktrees/`. You scaffold headers **once**; Step 7 rewrites `LEADERBOARD.md` fully from final state, never hand-patched mid-run.
2. If `baseline.artifact: 'none'` (cold start): skip calibration, set `baseline_score = null` (round 1's best initializes the trajectory), and proceed to Step 5 — for `backend: programmatic` the Step 2 dry-run already validated the command.
3. If the brief carries a user-asserted `baseline.score`, still run the calibration: it is the harness smoke test, not just a measurement.

#### Phase 2: Execution (Subagents — calibration eval)

Dispatch the calibration through the **chosen backend exactly as a round would score** (full procedures in `references/eval-backends.md`):

- **`backend: judges`** → dispatch the full judge panel (`eval.judges.count` independent `opus` judges) against the baseline artifact using the verbatim Independent Judge prompt block from `references/loop-workflow.md` (Shared agent prompt blocks); median consensus is the baseline score.
- **`backend: human`** → no agent: one native `AskUserQuestion`, the brief's anchored scale as options.
- **`backend: programmatic`** → one `haiku` agent:

    >>>
    **ultrathink: adopt the Eval Harness Runner mindset**

    - You're an **Eval Harness Runner** with deep expertise in deterministic command execution who follows these principles:
      - **One Number**: stdout must parse to exactly one number on the metric's scale — anything else is a harness error, not something to repair
      - **Verbatim Capture**: on failure, the raw stdout/stderr excerpt IS the deliverable
      - **No Repairs**: never edit the command, the eval script, or the artifact — run and report

    **Assignment**
    Run the brief's eval harness once against the baseline:

    - command: `<eval.programmatic.command>`, timeout: `<eval.programmatic.timeout_s>`s
    - baseline artifact: `<baseline.artifact>` (code mode: run `<eval.programmatic.setup_command>` once first, if set)

    **Steps**

    1. Run `setup_command` once if set
    2. Run the eval command under the timeout; capture stdout, stderr, exit code
    3. Parse stdout to a single number (whitespace-stripped; one trailing newline is fine); on any failure retry ONCE, then report the captured output verbatim

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<500 tokens):

    ```yaml
    status: success|failure
    summary: 'baseline scored <n>' # or 'harness error: <one line>'
    outputs:
      score: <number|null>
      raw:
        - { run: 1, score: <number|null>, reasoning: 'exit 0, stdout parsed clean' }
      captured_output: '' # stdout/stderr excerpt, only on failure
    issues: []
    ```
    <<<

#### Phase 3: Review (Subagents)

**SKIPPED** — the calibration result is deterministic (a number parsed, or a captured failure); the Phase 4 routing IS the review.

#### Phase 4: Decision (You)

1. **Single parseable score** → record it as the `LEADERBOARD.md` baseline row and as `baseline_score` in run state. The brief's `baseline.score: null` stays null — the brief is immutable post-approval; the leaderboard owns the measured value. Proceed to Step 5.
2. **Harness failure** (non-numeric after retry, command error, judge panel unable to apply the rubric) → the harness is broken, NOT the run: do not fan out. Return to **Step 2 targeting the eval fields** (exit-criterion (a)) with the captured output shown to the user, then re-render and re-approve via Step 3, and repeat Step 4.

### Step 5: Execute Research Loop

**Step Configuration**:

- **Purpose**: Run Generate → Score → Verify → Evolve rounds until a stop check fires, via the mechanism the gate selects
- **Input**: approved brief, `run_dir`, `baseline_score`, optional `resume_state` (Step 1 resume, or Step 6 extend/pivot re-entry with effective bounds)
- **Output**: loop return `{ status, stop_reason, rounds_completed, best, leaderboard, pending_decisions, disqualified }`
- **Sub-skill**: `Workflow` (Mechanism A)
- **Parallel Execution**: Yes — generators and scorers fan out within each round

Loop internals — the four round phases, the shared agent prompt blocks (Candidate Generator, Independent Judge, Adversarial Refuter — used verbatim by BOTH mechanisms, so neither owns them), the structured return, the `pending_decision` contract, and the workflow script skeleton — live in **`references/loop-workflow.md`**; scoring procedure per backend in **`references/eval-backends.md`**; genome breeding, fanout adaptation, and stop checks in **`references/evolution.md`**.

#### Phase 1: Planning (You)

1. **Mechanism gate** — choose exactly one:
   - **Mechanism A (dynamic Workflow)** when BOTH hold: the `Workflow` tool is available (not disabled) AND `eval.backend ∈ {programmatic, judges}` — these backends score without user input, so whole rounds run unattended.
   - **Mechanism B (sequential inline)** otherwise — `Workflow` unavailable/disabled, OR `eval.backend: human` (human scoring needs per-round input; under A every round would stop and resume, so B is preferred for this backend even when `Workflow` exists).
2. Use TodoWrite: one todo per round (extended as rounds proceed), plus per-phase todos under Mechanism B.

#### Phase 2: Execution — Mechanism A (dynamic Workflow)

Initiate the fanout workflow with the design in `references/loop-workflow.md` (Generate → Score → Verify → Evolve per round; deterministic script — seed and timestamps passed in as args). Pass it: the parsed brief frontmatter as data, `run_dir`, `baseline_score`, `resume_state` (or null), `seed`, `started_at`. The workflow persists every round artifact under `rounds/round-NN/` the moment it exists (schemas in `references/dossier.md`) and returns the structured shape `{ status, stop_reason, rounds_completed, best, leaderboard, pending_decisions, disqualified }`. Model assignments inside it: `opus` generators (`sonnet` acceptable for mechanical parameter sweeps), `haiku` eval runners, `opus` judges and refuter.

#### Phase 3: Execution — Mechanism B (sequential inline, fallback)

Drive the identical round semantics inline, per the **"Mechanism B — sequential fallback"** section of `references/loop-workflow.md`: each round dispatches the shared agent prompt blocks defined there — **Candidate Generator** (`opus`, parallel `Task` calls in ONE message, sibling-blind), **Independent Judge** (`opus`, one `Task` per judge per candidate), **Adversarial Refuter** (`opus`, max 3 passes per round) — the very blocks Mechanism A's payloads are rendered from. Human scoring runs as native `AskUserQuestion` batteries written to `rounds/round-NN/scores.yaml` (why B is preferred for that backend), and Evolve you compute yourself per `references/evolution.md` — pure math over `scores.yaml`, never an agent, every bound trip stated with its trigger.

#### Phase 4: Decision (You)

1. **`status: pending_decision`** (Mechanism A stop contract) — handle each entry, then resume:
   - `type: human_scoring` → `AskUserQuestion` per listed candidate (id + artifact path + one-line summary, the brief's anchored scale as options); write the answers into `rounds/round-NN/scores.yaml` as `{ judge: human, score, ... }` entries.
   - `type: constraint_ambiguity` → `AskUserQuestion` with the contract's question + options; append the ruling as a dated entry to the brief's `## Amendments`.
   - Resume via `Workflow resumeFromRunId` — the cached prefix replays completed rounds instantly. Repeat until a terminal status.
2. **Terminal status** (`target_met` | `budget_exhausted` | `plateau`) → proceed to Step 6 carrying `stop_reason`, `rounds_completed`, `best`, `leaderboard`, `disqualified`.
3. **Generator/scorer failures mid-round (Mechanism B)**: a failed generator slot is retried once, then its slot is logged as forfeited (the round runs thinner — logged, never silently backfilled); a non-scoreable candidate is `disqualified: <reason>` in `scores.yaml`, never silently dropped.

### Step 6: Stop-Condition Handling & User Decision

**Step Configuration**:

- **Purpose**: Convert a fired stop check into a user ruling — the decision to stop, extend, or pivot belongs to the user, never the loop
- **Input**: loop return from Step 5 (`stop_reason`, `best`, `rounds_completed`, leaderboard)
- **Output**: ruling ∈ {accept, extend, pivot} appended to `user_decisions[]` AND to the brief's `## Amendments`
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Stop & Ask (You)

The loop has STOPPED — nothing runs while you ask. Present: stop reason, rounds completed of `budget.max_rounds`, best score vs baseline vs `target.threshold`, and the top-3 leaderboard. Then `AskUserQuestion`:

- **Accept**: take the current best → Step 7 (`status: target_met` when the target fired, else `accepted_below_target`)
- **Extend**: raise `budget.max_rounds` and/or the plateau bound (`plateau.rounds`) by user-chosen amounts → resume Step 5
- **Pivot**: amend the brief — new/changed framing directions, constraints, or target — via a mini Step 2/3 cycle (targeted interview batteries on the changed fields only, then re-present for approval) → resume Step 5

#### Phase 2: Decision (You)

1. **Append every ruling to the brief's `## Amendments`** as a dated entry — what changed, why, and the user's verbatim choice. The frontmatter is never rewritten; the amendment is the audit record, and the **resume args carry the effective bounds** (raised budget/plateau, amended directions) into Step 5 explicitly.
2. Record the ruling in `user_decisions[]` for the completion report.
3. **Extend/pivot** → re-enter Step 5 with `resume_state` reconstructed from `rounds/` (Mechanism B) or `Workflow resumeFromRunId` (Mechanism A), passing the amended bounds. **Accept** → Step 7.

### Step 7: Dossier Synthesis & Completion

**Step Configuration**:

- **Purpose**: Synthesize DOSSIER.md from disk, provenance-check the leaderboard, land the winning artifact (guarded, code mode), clean up, and report
- **Input**: `run_dir`, accepted `best`, loop return, `user_decisions[]`
- **Output**: `DOSSIER.md`, final `LEADERBOARD.md`, `best/` artifact, the Skill Completion YAML
- **Sub-skill**: `coding:commit` (code mode only, to save the applied diff)
- **Parallel Execution**: No

#### Phase 1: Planning (You)

Confirm every `rounds/round-NN/` directory carries its `scores.yaml`, `verify.yaml`, and `round-log.md`; queue one synthesis dispatch and one review dispatch as todos.

#### Phase 2: Execution (Subagent — synthesis)

Dispatch ONE `fable` or `opus` synthesis agent:

    >>>
    **ultracode: adopt the Research Dossier Author mindset**

    - You're a **Research Dossier Author** who follows these principles:
      - **Disk Is Truth**: synthesize from the `rounds/` files only — never from anyone's memory of the run
      - **Insight Over Inventory**: each round earns one finding, not a transcript
      - **Honest Threats**: every refutation and the residual Goodhart risk go in the dossier, not under the rug

    **Assignment**

    - run_dir: `<run_dir>` — read `RESEARCH_BRIEF.md` (including `## Amendments`) and every `rounds/round-NN/` file (`round-log.md`, `scores.yaml`, `verify.yaml`, `candidates/*/candidate.yaml`)

    **Steps**

    1. Read the brief and all round files
    2. Write `<run_dir>/DOSSIER.md` with the seven sections, in order, per the format in `references/dossier.md` (Executive Summary → Best Artifact → Score Trajectory → Methodology Recap → Per-Round Insights → Threats to Validity → Recommendations)
    3. Rewrite `<run_dir>/LEADERBOARD.md` fully from the final leaderboard state (never hand-patch the scaffold)
    4. Copy the winning artifact verbatim into `<run_dir>/best/`

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure
    summary: '<dossier headline: best vs baseline vs target>'
    modifications: ['DOSSIER.md', 'LEADERBOARD.md', 'best/<artifact>']
    outputs:
      best: { candidate_id: '...', score: ..., artifact_path: 'best/<artifact>' }
    issues: []
    ```
    <<<

#### Phase 3: Review (Subagent — provenance audit)

Dispatch ONE read-only `haiku` reviewer — every leaderboard score must trace to a `scores.yaml` entry (the completion gate from `references/dossier.md`):

    >>>
    **ultrathink: adopt the Provenance Auditor mindset**

    - You're a **Provenance Auditor** who follows these principles:
      - **Trace or Fail**: every LEADERBOARD.md score must trace to a `rounds/round-NN/scores.yaml` entry with matching cid, round, and consensus value
      - **Read-Only**: you modify nothing
      - **No Benefit of the Doubt**: a row without provenance is a fatal, not a warning

    **Review Assignment**
    Verify, in `<run_dir>`:

    - `LEADERBOARD.md` against every `rounds/round-NN/scores.yaml`
    - `DOSSIER.md` headline numbers (best, baseline, target) against the same files
    - `best/` contains the rank-1 artifact

    **Review Steps**

    1. For each leaderboard row, locate the scores.yaml entry with the same cid + round and confirm the consensus value matches exactly
    2. Confirm `best/` holds the rank-1 candidate's artifact
    3. Confirm DOSSIER.md's Executive Summary numbers match disk

    **Report**
    **[IMPORTANT]** You MUST return the following review report (<500 tokens):

    ```yaml
    status: pass|fail
    summary: '<N rows traced, M fatals>'
    checks:
      leaderboard_provenance: pass|fail
      best_artifact_matches_rank1: pass|fail
      dossier_numbers_match_disk: pass|fail
    fatals: [] # rows with no scores.yaml provenance
    warnings: []
    recommendation: proceed|retry
    ```
    <<<

#### Phase 4: Decision (You)

1. Review `fail` → re-dispatch the synthesis agent with the fatals attached, then re-review; max 2 retries, the trip logged (a leaderboard row with no provenance fails the run's completion gate — never ship it).
2. **Code mode landing (guarded)**: `AskUserQuestion` — "Apply the winning diff onto HEAD?" with the diff stat and verified score. On yes, apply ONLY the winning candidate's diff onto HEAD of the main working copy — worktrees are ephemeral experiment sandboxes, NEVER committed from — then save the applied change through `coding:commit`. On no, the diff stays available in `best/`.
3. **Remove `worktrees/`** (code mode) — the sandboxes are spent.
4. Mark all todos `completed` and emit the Skill Completion report.

### Skill Completion

**Report the skill output as specified**:

```yaml
status: target_met|accepted_below_target|aborted
metric: { name: ..., baseline: ..., best: ..., target: ..., direction: ... }
rounds_completed: <n>
candidates_evaluated: <n>
stop_reason: target|budget|plateau|user_abort
mechanism: A|B
output_dir: autoresearch_<slug>_<date>/
best_artifact: <path>
user_decisions: [<extend/pivot/accept log>]
```
