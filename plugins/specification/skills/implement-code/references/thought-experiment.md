# Step 11 — Thought-Experiment Gate

**When loaded**: After Step 10's spec-alignment review, when the run is NOT in any of the skip conditions below.

**Skip entirely** (record `thought_experiment_report.status=skipped` with one-line reason and proceed to Step 12) when any of:

- `mode ∈ {VERIFY_ONLY, DRAFT_THEN_ASK, REFUSE, FLAG_MISMATCH}`
- `--dry-run` is set
- `commits_landed` is empty

`AUDIT_AND_COMPLETE` **runs** this gate (it is NOT skipped): the mode finishes a real implementation, so tracing every intended usage through the landed code is exactly the integration confidence an audit needs. Recorded Step 5 soundness decisions and any DEVIATIONS keep the spec authoritative enough to trace against.

---

## Step Configuration

- **Purpose**: Paper-only integration validation against the landed code; catches silent integration breakage that tests missed by tracing every intended usage through the real file graph.
- **Input**: `repo_path`, `spec_bundle.root_path` plus a pre-computed pointer list of all Usage/Example/Scenario/Verification sections discovered across the bundle's flat `{kebab-title}-{32hex-id}.md` files (root + adjacent), `commits_landed`, `<repo_path>/DEVIATIONS.md`
- **Output**: `thought_experiment_report` with per-usage verdicts
- **Sub-skill**: None — single `Task` dispatch. The subagent **MUST** use `subagent_type=general-purpose`, `model=opus` (never Sonnet, never Haiku, no fallback), and **maximum reasoning effort / thinking budget**. These settings are mandatory whenever this step runs; do not downgrade for cost, latency, or quota reasons. If opus is unavailable, fail the step with `status=partial` and an advisory rather than substituting a weaker model.
- **Parallel Execution**: No — one sequential deep pass

## Phase 1: Planning (You)

1. Evaluate the skip list above. If any condition holds, record `thought_experiment_report.status=skipped` with a one-line reason and proceed to Step 12.
2. Otherwise assemble the inputs bundle: `spec_bundle.root_path` + pre-computed pointer list of Usage/Example/Scenario/Verification sections, absolute `repo_path`, `DEVIATIONS.md` path, and the list of `commits_landed` shas for context.
3. Update TodoWrite: add a `thought-experiment` todo set to `in_progress`.

## Phase 2: Execution (Subagent)

Dispatch a single `Task` with `subagent_type=general-purpose`, `model=opus`, maximum reasoning budget. Embed the prompt below verbatim.

    >>>
    (Dispatched on model=opus with maximum reasoning effort. This is the only place in the skill that guarantees deep paper-only integration review; no other step compensates if you under-think here.)

    You are the Thought-Experiment Reviewer. Apply maximum reasoning effort. Do NOT run code, run tests, or edit files — read only.

    **[IMPORTANT]** Enumerate the bundle via `Glob: <bundle_root>/*.md`. The root spec file is the one whose filename ends `-<ticket.id>.md` (32-hex suffix). Open only the files referenced in the pointer block. Do NOT re-fetch from Notion.

    **Inputs**
    - Spec bundle root: `<spec_bundle.root_path>` (flat directory of `{kebab-title}-{32hex-id}.md` files; identify root by filename suffix matching ticket id)
    - Spec pointer list (pre-computed by orchestrator): every Usage / Example / Scenario / PI Verification section discovered across the bundle's `*.md` files (root file + adjacent files)
    - Repo: <repo_path> (use Read / Grep / Glob)
    - Deviations log: <repo_path>/DEVIATIONS.md

    **Task**
    Identify every INTENDED USAGE in the spec (one usage = one externally-observable way the implementation is meant to be called or composed). For each:
    1. Trace it step-by-step through the actual landed code — imports, call graph, return shapes, error paths, async boundaries
    2. Verify the public surface the usage touches exists, has the right signature, and composes correctly with its dependencies
    3. Check every deviation in DEVIATIONS.md has been absorbed — the usage must still work despite the departure from draft
    4. Cross-check against adjacent usages to catch conflicting assumptions

    **Per-usage verdict**: `works` | `broken` | `unclear` — with 2-3 sentences of trace reasoning. If `broken`, cite `file:line`.

    **Overall verdict**: `pass` (all `works`) | `partial` (any `unclear`, no `broken`) | `fail` (any `broken`).

    **Report (YAML, <3000 tokens)**:

        status: pass|partial|fail
        outputs:
          thought_experiment_report:
            usages:
              - id: U-1
                description: '<one-liner>'
                verdict: works|broken|unclear
                trace: '<2-3 sentences>'
                cite: '<file:line or null>'
            deviations_absorbed: true|false
            summary: '<paragraph>'
        issues: []
    <<<

## Phase 3: Review (Subagents)

**SKIPPED** — This step is itself the review layer; its output feeds Step 12 and Step 13 directly.

## Phase 4: Decision (You)

- `status=pass` → proceed to Step 12 with `status=completed`
- `status=partial` → final `status=partial`, list unclear usages in the final report, do not block
- `status=fail` → append `D-<N>: thought-experiment-blocking / severity=blocking` to `DEVIATIONS.md`, final `status=partial`, recommend rerun after fix, proceed to Step 12
- Always attach the full `thought_experiment_report` to running context so Step 13 can emit it
