# Execute Mode — mechanism detail

This reference holds the two execution mechanisms Step 8 of `implement-code` selects between. SKILL.md owns the
mechanism gate (Phase 1), the pre-coding hard-copy gate, the stop→ask→patch→resume orchestration loop, and the
post-execution wiring (`child_dispatch_log`, `commits_landed`, trailing `DEVIATIONS.md` commit). This file holds the
conditional bulk each mechanism needs. Read only the section matching the mechanism the gate selected.

Both mechanisms share one contract:

- **Orchestrator never holds the pen.** Every `Write`/`Edit` happens inside a dispatched `coding:*` child; every `jj`
  mutation happens inside `coding:commit`. In Mechanism A the workflow's agents dispatch those same children — the
  workflow script itself coordinates, it does not edit files.
- **Deviation policy travels with every dispatch.** Embed the verbatim "Deviation Policy Block" from
  `references/modes.md` in every `coding:*` payload (workflow agents include it too). Material departures are logged to
  `<repo>/DEVIATIONS.md`; trivial ones (JSDoc, inferred types, lint/format) are silent.
- **Spec is read-only to coding agents; decisions are recorded only via `specification:mdc`.** `.code-spec/*.md` files
  are MDC and are mutated ONLY through the `specification:mdc` skill, from the main thread — never by a coding agent and
  never via direct `Write`/`Edit`.
- **No silent caps.** Any iteration / token bound that ends the loop early MUST be surfaced (`log()` inside the
  workflow, and carried into `execution` / `unresolved[]` for the final report).

---

## Mechanism A — Dynamic-workflow fan-out (preferred when `Workflow` available + code-producing mode)

This is the in-skill `ultracode` equivalent: a dynamic workflow orchestrates many subagents in three repeating phases —
*Fanout* → *Verify* → loop — and **returns structured results** to the skill. The skill (not the workflow) handles any
user decision, because workflows cannot take mid-run input.

Initiate the workflow with the design below. Pass it: `repo_path`, the spec pointer block (flat
`{kebab-title}-{32hex-id}.md` layout, root file = filename suffix matching `ticket.id`), `mode`, `features_coverage`,
and the verbatim `deviation_policy` block.

### Slicing (by mode)

The workflow first builds a slice list — one independently-implementable unit of work per slice:

- **`COMMIT_PLAN`** — one slice per PLAN.md phase / commit blueprint.
- **`PI_ITERATE`** — one slice per pending-TODO-and-failing-test cluster.
- **`AUDIT_AND_COMPLETE`** — one slice per audit gap surfaced by a baseline `coding:review`.

Each slice carries its spec requirement(s), the target file(s), and a stable slice id.

### Phase Fanout — parallel implementation agents

Each slice goes to one implementation agent that:

1. Reads its spec requirement(s) and the current code for its target file(s).
2. **If the slice needs an architectural decision not resolvable from the spec, it does NOT guess** — it emits a
   structured `pending_decision` (see contract below) and returns its slice as `blocked`, implementing nothing.
3. Otherwise dispatches the mode-appropriate `coding:*` child for its slice (`coding:write-code` /
   `coding:complete-code` / `coding:fix`) with the `deviation_policy` embedded, then `coding:review`; on review failure
   it runs `coding:fix` and re-reviews (max 3 internal iterations).
4. On success, dispatches `coding:commit` for its slice and records the SHA.

### Phase Verify — adversarial advisor verifiers

Each landed slice is handed to N verifier agents whose job is to **refute** that the slice satisfies its spec
requirement: prove the requirement is unmet, the contract drifted, an invariant weakened, or an acceptance criterion is
broken. A slice is **accepted** only if no verifier can refute it. Verifiers:

1. Re-read the slice's spec requirement, the landed code (`file:line`), and surrounding context.
2. Attempt a concrete refutation (a missing case, a wrong shape, a broken criterion).
3. Return `accepted` or `refuted` with a one-line rationale (and, if `refuted`, what is missing).

### Loop-until-done

Repeat Fanout → Verify: refuted slices are re-queued (with the verifier's rationale fed back to the implementation
agent) and verified slices are retired. The loop ends when every slice is `accepted`, or when a bounded
max-iteration / token guard trips — in which case unretired slices are returned in `unresolved[]` and the bound is
`log()`-ed.

### `pending_decision` contract (the stop signal)

When any agent records a `pending_decision`, the workflow **stops early** and returns rather than running past an
unanswered architectural question. Each entry:

```yaml
pending_decisions:
  - slice_id: '<id>'
    spec_loc: '<bundle-file>:<heading>'
    question: '<the architectural decision needed>'
    options: ['<option A>', '<option B>', '...']
    rationale: '<why the spec does not resolve this>'
```

### Structured return shape

```yaml
verified_slices: ['<slice_id>', ...]
pending_decisions: [ ... ]          # empty when the run finished without needing input
commits_landed:
  - sha: '<sha>'
    message: '<conventional message>'
child_dispatch_log:
  - skill: 'coding:<name>'
    status: 'pass|fail|partial'
    summary: '<one-liner>'
unresolved: ['<slice_id>', ...]     # non-empty only if the iteration/token guard tripped
```

### After the workflow returns (handled by SKILL.md Step 8 Phase 2)

On a stopped run with `pending_decisions`, the skill (main thread) asks the user via `AskUserQuestion`, records each
answer into the owning `.code-spec/*.md` via `specification:mdc`, then resumes the run with `Workflow resumeFromRunId`
(cached prefix replays completed slices). The recorded spec edits ARE the patch — agents re-read the spec on resume.
Repeat until `pending_decisions` is empty and `unresolved` is empty (or the guard trips → `coding:handover`, partial).

---

## Mechanism B — Sequential `coding:*` chain (fallback when `Workflow` unavailable/disabled or `--dry-run`)

This is the original, unchanged behavior. Run the per-mode child chain from `references/modes.md` "Step 8 — Per-Mode
Child Chains" sequentially in the live session, where `AskUserQuestion` works natively. When a child surfaces an
architectural decision needing user input, ask inline and record the answer into the local spec via `specification:mdc`
(never edit the MDC bundle directly) before continuing the chain. All other rules (deviation policy, review→fix→review
max 3, `commits_landed` capture, trailing `DEVIATIONS.md` commit) are identical to Mechanism A's per-slice rules.
