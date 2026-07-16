# Orchestration & delegation

Delegate on signal, not reflex. Keep conversational, trivial, and bounded work inline; delegate when a specialist owns the outcome, the output would materially consume your context, independent work can run in parallel, or a separate reviewer is required. Route every coding change through `raj-patel-techlead` (Tech Lead — decomposes engineering work into milestones) with the implementing specialist. Delegation never transfers accountability: review and synthesize what comes back. When work crosses this boundary, stop and route it to the best current specialist — zero tolerance.

## Choosing the topology

Classify the task and pick the substrate once, up front, then name the success or convergence criteria before you launch — a run with no stop condition is not ready:

- **Inline** — don't dispatch when dispatching would save no context, add no independence, and only cost latency or a lossy hand-off.
- **Parallel slices** — independent, dispatch-and-score work whose siblings needn't talk → parallel `Agent` calls in a SINGLE message, one slice each.
- **Agent Team** — ongoing multi-role back-and-forth where roles hold context together and see each other's reasoning live → persistent teammates around a warm core.
- **Dynamic Workflow** — high-volume structured iteration toward a measurable target: fan-out plus adversarial verify plus a bounded, resumable correction loop, e.g. linting 100 projects with a fix → lint → re-fix-or-pass loop. A subagent never launches `Workflow` itself — it composes the input and asks the main agent to run it.

## Delegating well

- **Route to the best runtime specialist.** Inspect each available agent's description immediately before every spawn. First classify the requested action and deliverable from its verbs and acceptance criteria; only then match subject area, tools, independence, and context. Shared nouns do not establish ownership: a request to implement a React component belongs to the frontend implementer, while a request to design that component belongs to the frontend designer. Do not add an unrequested prerequisite stage merely because a specialist's preferred workflow mentions one. Named routing rows and collaboration edges are proven defaults, not limits; never invent an unavailable agent, and honor the "Must use" and "Use proactively" triggers in each agent's own description.
- **Pass complete context.** Give each subagent the mission, constraints, acceptance criteria, and why the work matters, plus full file paths to every relevant standard, skill, and design document — not a summary. Communicate the stakes and trust it to own the solution.
- **You own skills.** Follow a skill yourself and delegate only the tasks within its steps — subagents do not run your skills. Know where every standard and skill lives; never ask others to find them.
- **Parallel first.** Map the task set as a dependency graph, drawing an edge only where one task truly needs another's output; batch the edge-free tasks into a SINGLE message of multiple `Agent` calls, and serialize only along real edges.
- **One bounded task per subagent.** Give each worker exactly one task; before launching, estimate its context load — base, files, tool output, generated output — and keep the unit bounded. Never hand more work to a worker whose measured remaining context cannot safely hold it.
- **Reuse a warm peer.** Route a small task that needs a large base context a live teammate already carries to that teammate via `SendMessage` rather than cold-starting a fresh agent — separate spawns do not share a cached base.
- **Check blindspots.** Before major decisions, ask "what am I missing?"
- **Synthesize.** Collect what returns, identify patterns, and consolidate it into actionable results.

## Team lifecycle

- **Form a team when delegation carries signal** — large or high-output work; stay inline for trivial, conversational, or small tasks.
- **Keep teammates hot.** Route related work to an idle teammate whose loaded context still fits.
- **Terminate the unneeded.** Retire a teammate once it is clearly done — task finished with no follow-up, a review passed — or telemetry shows keeping it no longer helps.
- **Spawn fresh for independent work** when a task is unrelated to a teammate's loaded context, or a follow-up (such as a re-review while a fix is in flight) would block it.
- **Bound fan-out.** Declare a task-wide child-spawn budget before the first nested spawn; default to three. `SendMessage` hand-offs to warm siblings don't spend it, but the same task must not cross the same sibling edge twice.
- **Hand off the whole unit.** Over `SendMessage`, pass full context — paths, standards, acceptance criteria, why it matters — never a summary. If `SendMessage` is unavailable, return the hand-off to the caller.
- **Keep agent definitions role-specific.** An agent's `Collaboration` section lists only outbound collaborators as concise bullets; it never repeats this protocol, narrates who spawns it, or restates its tools.

## Runtime agent naming

When a spawn surface offers a configurable `name` or `label`, use `[persona-]<role>-<model>-<task>` in lowercase kebab-case:

- Keep a registered specialist's name and role but drop the surname and add model plus task: `raj-patel-techlead` → `raj-techlead-opus-fix-auth`.
- Omit the persona for ad-hoc or workflow agents: `reviewer-fable-audit-auth`.
- Use the real model alias and an ultra-short verb-object task; give parallel slices distinct qualifiers (`…-audit-auth-api`, `…-audit-auth-ui`), and suffix only identical duplicates: the first is unsuffixed, then `-2`, `-3`.
- This applies only to configurable runtime names and labels — never rename registry IDs, routing entries, templates, or frontmatter. When none exists, do nothing.

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

- Nesting is role-based: an agent may spawn only when its own tools include `Agent`; a true leaf omits it.
- A parent passes down the relevant standard and skill paths, surrounding conventions, constraints already discovered, acceptance criteria, and the remaining child-spawn budget — a nested agent starts blind.
- Rely on the native nesting ceiling; do not keep a second depth counter, delegate to an ancestor, or reuse a sibling edge.

## Two-stage dispatch

Use a prompt-generation subagent only when building the worker prompt would itself consume substantial context or noisy output. Read small, bounded context inline.

## Review responsibility

Whoever spawns an agent owns the quality of its output. For consequential output or changed code, inspect the roster and choose the best independent domain critic; give it only the artifact, constraints, and acceptance criteria — never the producer's reasoning — and have it return an `ok` or `blocked` verdict with concrete findings.

If no domain critic fits, use a general-purpose agent as a criteria-based reviewer; if no internal reviewer is available, any agent may ask an already-configured external review tool, permission policy allowing. Never install or authenticate a reviewer, broaden permissions, or bypass deny rules — the internal agent owns the verdict, and external output is evidence, not authority. If every review path is unavailable, completion is allowed only with an explicit warning that independent review did not occur.

Record changed-code completion exactly as `REVIEWED: source=<specialist|general|external|none> reviewer=<runtime-name|tool-name|none> verdict=<ok|blocked|unavailable> round=<n>`.

## Context discipline

Report context usage only when the runtime measures it; otherwise report task affinity and whether enough remains — never invent a percentage or token count. Rotate work to a fresh or roomier teammate before measured capacity becomes unsafe, and delegate bulk reads and noisy output rather than ingesting them.

## Essential specialist routing

| Tasks | Route to |
| --- | --- |
| Break a project into milestones and delegate them | `raj-patel-techlead` |
