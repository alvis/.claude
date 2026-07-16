# Orchestration & delegation

Delegate on signal, not reflex. Keep conversational, trivial, and bounded work inline; delegate when a specialist owns the outcome, the output would materially consume your context, independent work can run in parallel, or a separate reviewer is required. Route every coding change through `tech-lead` (Tech Lead — decomposes engineering work into milestones) with the implementing specialist. Delegation never transfers accountability: review and synthesize what comes back. When work crosses this boundary, stop and route it to the best current specialist — zero tolerance.

## Choosing the topology

Classify the task and pick the substrate once, up front, then name the success or convergence criteria before you launch — a run with no stop condition is not ready:

- **Inline** — don't dispatch when dispatching would save no context, add no independence, and only cost latency or a lossy hand-off.
- **Parallel slices** — independent, dispatch-and-score work whose siblings needn't talk → parallel `Agent` calls in a SINGLE message, one slice each.
- **Agent Team** — ongoing multi-role back-and-forth where roles hold context together and see each other's reasoning live → persistent teammates around a warm core.
- **Dynamic Workflow** — high-volume structured iteration toward a measurable target: fan-out plus adversarial verify plus a bounded, resumable correction loop, e.g. linting 100 projects with a fix → lint → re-fix-or-pass loop. A subagent never launches `Workflow` itself — it composes the input and asks the main agent to run it.

## Delegating well

- **Route to the best runtime specialist.** Inspect each available agent's description immediately before every spawn. First classify the requested action and deliverable from its verbs and acceptance criteria; only then match subject area, tools, independence, and context. Shared nouns do not establish ownership — for example, a request to implement a React component belongs to the frontend implementer, while a request to design that component belongs to the frontend designer. Do not add an unrequested prerequisite stage merely because a specialist's preferred workflow mentions one. Named routing rows and collaboration edges are proven defaults, not limits; never invent an unavailable agent, and honor the "Must use" and "Use proactively" triggers in each agent's own description.
- **Pass complete context.** Give each subagent the mission, constraints, acceptance criteria, and why the work matters, plus full file paths to every relevant standard, skill, and design document — not a summary. Communicate the stakes and trust it to own the solution.
- **You own skills.** Follow a skill yourself and delegate only the tasks within its steps — subagents do not run your skills. Know where every standard and skill lives; never ask others to find them.
- **Parallel first.** Map the task set as a dependency graph, drawing an edge only where one task truly needs another's output; batch the edge-free tasks into a SINGLE message of multiple `Agent` calls, and serialize only along real edges.
- **One bounded task per subagent.** Give each worker exactly one task; before launching, estimate its context load — base, files, tool output, generated output — and keep the unit bounded. Never hand more work to a worker whose measured remaining context cannot safely hold it.
- **Only the main agent names teammates.** For a persistent teammate, choose one of the three preferred short names at the end of the selected role's description, combine it with the role and task, and choose a different suggestion when the short name would collide with a living teammate. Nested agents never assign configured names.
- **Reuse a warm peer by ID.** Route a small task that needs a large base context to the `agent_id` of a live teammate that already carries it rather than cold-starting a fresh agent — separate spawns do not share a cached base.
- **Delegate continuing work directly when the owner is known.** If a subagent knows the best teammate and its `agent_id`, it messages that teammate directly. If it knows the teammate but not the ID, it asks the main agent to resolve the ID. Only when it does not know who should own the work does it ask the main agent to suggest someone; the main agent prefers a living teammate that has worked on the same folder or feature, otherwise it spawns a new named teammate that meets the requested criteria and returns its `agent_id`.
- **Message only by `agent_id`.** Direct agent-to-agent communication always targets the runtime `agent_id`; a role, `subagent_type`, configured name, or label is never a message address.
- **Synthesize.** Collect what returns, identify patterns, and consolidate it into actionable results.

## Working with uncertainty

Treat the prompt and plan as working hypotheses that repository and runtime evidence may revise. Label consequential claims as user-stated intent, observed fact, inference, accepted assumption, or unresolved question. A possible blindspot is a hypothesis to investigate, never a discovered fact merely because it sounds plausible.

Before a long-horizon or materially ambiguous decision, inspect the relevant code, runtime behavior, and integration surface and ask what evidence, latent preference, constraint, failure mode, or historical choice may be missing. Use `essential:discover` when this needs a dedicated blindspot, options, interview, reference, prototype, or readiness pass; use `essential:decide` only after the evidence is sufficient to converge on one approach.

Proceed without user input only when the assumption is low-impact and reversible; choose the conservative path and record it. Escalate architecture, public API, data model, security or privacy, destructive migration, user-visible semantics, and anything that changes acceptance criteria. When evidence disproves a plan premise, stop the stale branch, re-evaluate dependent work, and either re-plan or request the material decision.

The main session owns the authoritative uncertainty ledger and user decisions. A subagent that encounters a material unknown returns the observed evidence, inference, unresolved question, deviation from the assigned map, recommended disposition, affected scope, options, and independent work that can continue.

## Team lifecycle

- **Form a team when delegation carries signal** — large or high-output work; stay inline for trivial, conversational, or small tasks.
- **Keep teammates hot.** Route related work to an idle teammate whose loaded context still fits.
- **Terminate the unneeded.** Retire a teammate once it is clearly done — task finished with no follow-up, a review passed — or telemetry shows keeping it no longer helps.
- **Spawn fresh for independent work** when a task is unrelated to a teammate's loaded context, or a follow-up (such as a re-review while a fix is in flight) would block it.
- **Keep nested spawning one-off.** A nested agent may spawn only when the task is certainly disposable after one returned artifact or summary. It specifies `subagent_type` (for example, `test-reporter`), omits a configured name, and never creates a standing nested teammate. For continuing work, it messages the best-known teammate directly by `agent_id`; only when it cannot identify the owner does it ask the main agent to suggest one.
- **Bound exceptional fan-out.** Declare a task-wide child-spawn budget before the first one-off nested spawn; default to three. `SendMessage` hand-offs to known `agent_id`s don't spend it, but the same task must not cross the same sibling edge twice.
- **Hand off the whole unit.** Over `SendMessage`, pass full context — paths, standards, acceptance criteria, why it matters — never a summary. If `SendMessage` is unavailable, return the hand-off to the caller.
- **Keep agent definitions role-specific.** An agent's `Collaboration` section lists only outbound collaborators as concise bullets; it never repeats this protocol, narrates who spawns it, or restates its tools.

## Runtime teammate naming

Only the main agent assigns a configurable teammate `name` or label. Use `<short-name>-<role>-<task>` in lowercase kebab-case:

- Select the short name from the three preferences at the end of the role's description: `tech-lead` with preferred name Raj becomes `raj-tech-lead-fix-auth`.
- Keep the role equal to the role-only definition name and use an ultra-short verb-object task. Give parallel slices distinct task qualifiers (`…-audit-auth-api`, `…-audit-auth-ui`).
- If the chosen short name is already used by a living teammate, use another preferred name; use a numeric suffix only after all three suggestions would still collide.
- Nested agents omit configured names entirely. A permitted one-off nested spawn supplies only its `subagent_type`, task, and context.
- Configured names are human-readable labels, not addresses. Capture the returned `agent_id` and use only that ID for direct communication.

## Model and effort

Match the model to the task's cognitive demand — never default everything to the largest, never starve a hard task with a small one:

| Model | Use for |
|-------|---------|
| **haiku** | Simple, routine, deterministic work with a known procedure — tests, lint, command output, mechanical file sweeps. |
| **sonnet** | Branching work — investigation whose next step depends on findings, triage, moderate edits with a few decision points. |
| **opus** | General coding — features, non-trivial bugs, refactoring with judgment. |
| **fable** | Advanced coding, deep reasoning, research, and review — where correctness hinges on subtle judgment or adversarial scrutiny. |

Effort is a second, independent dial (`low|medium|high|xhigh|max`; omit for haiku, which has none). Set it by the task's difficulty, not its model. Pick the cheapest model that clears the quality bar — a stronger model that wouldn't change the output is wasted — then, to make a worker think harder, raise its effort, not its model.

## Nesting

- Nesting is exceptional and one-off: an agent may consider it only when `Agent` is available at runtime and the helper's single returned artifact or summary ends the delegation. A leaf-by-charter does not spawn even when the runtime exposes `Agent`.
- The nested call specifies an agent type such as `test-reporter`, never a configured name. The parent passes the relevant standard and skill paths, surrounding conventions, discovered constraints, acceptance criteria, and remaining child-spawn budget — a nested agent starts blind.
- For continuing or collaborative work, message the best-known teammate directly by `agent_id`. If that teammate is known but its ID is not, ask the main agent to resolve the ID; only when the owner is unknown should the main agent suggest a warm peer by prior folder/feature history or spawn a new named teammate.
- Rely on the native nesting ceiling; do not keep a second depth counter, delegate to an ancestor, or reuse a sibling edge.

## Two-stage dispatch

Use a prompt-generation subagent only when building the worker prompt would itself consume substantial context or noisy output. Read small, bounded context inline.

## Review responsibility

Whoever spawns an agent owns the quality of its output. For consequential output or changed code, inspect the roster and choose the best independent domain critic; give it only the artifact, constraints, and acceptance criteria — never the producer's reasoning — and have it return an `ok` or `blocked` verdict with concrete findings.

If no domain critic fits, use a general-purpose agent as a criteria-based reviewer; if no internal reviewer is available, any agent may ask an already-configured external review tool, permission policy allowing. Never install or authenticate a reviewer, broaden permissions, or bypass deny rules — the internal agent owns the verdict, and external output is evidence, not authority. If every review path is unavailable, completion is allowed only with an explicit warning that independent review did not occur.

Record changed-code completion exactly as `REVIEWED: source=<specialist|general|external|none> reviewer=<agent-id|tool-name|none> verdict=<ok|blocked|unavailable> round=<n>`.

## Context discipline

Report context usage only when the runtime measures it; otherwise report task affinity and whether enough remains — never invent a percentage or token count. Rotate work to a fresh or roomier teammate before measured capacity becomes unsafe, and delegate bulk reads and noisy output rather than ingesting them.

## Essential specialist routing

| Tasks | Route to |
| --- | --- |
| Break a project into milestones and delegate them | `tech-lead` |
