# Team lifecycle, model, and effort

Read this when forming a team, spawning or retiring a teammate, or choosing
a worker's model and effort.

## Team lifecycle

- **Form a team when delegation carries signal** — large or high-output work;
  stay inline for trivial, conversational, or small tasks.
- **Keep teammates hot.** Route related work to an idle teammate whose loaded
  context still fits.
- **Terminate the unneeded.** Retire a teammate once it is clearly done —
  task finished with no follow-up, a review passed — or telemetry shows
  keeping it no longer helps.
- **Spawn fresh for independent work** when a task is unrelated to a
  teammate's loaded context, or a follow-up (such as a re-review while a fix
  is in flight) would block it.
- **Keep nested spawning one-off.** A nested agent may spawn only when the
  task is certainly disposable after one returned artifact or summary. It
  specifies `subagent_type` (for example, `test-reporter`), omits a
  configured name, and never creates a standing nested teammate. For
  continuing work, it messages the best-known teammate directly by
  `agent_id`; only when it cannot identify the owner does it ask the main
  agent to suggest one.
- **Bound exceptional fan-out.** Declare a task-wide child-spawn budget
  before the first one-off nested spawn; default to three. `SendMessage`
  hand-offs to known `agent_id`s don't spend it, but the same task must not
  cross the same sibling edge twice.
- **Hand off by reference.** The first message names the objective,
  acceptance criteria, and relevant absolute artifact paths within the
  4,096-character ceiling. Later messages carry only deltas. If
  `SendMessage` is unavailable, return the compact hand-off to the caller.
- **Keep agent definitions role-specific.** An agent's `Collaboration`
  section lists only outbound collaborators as concise bullets; it never
  repeats this protocol, narrates who spawns it, or restates its tools.

## Model and effort

Match the model to the task's cognitive demand — never default everything to
the largest, never starve a hard task with a small one:

| Model | Use for |
|-------|---------|
| **haiku** | Simple, routine, deterministic work with a known procedure — tests, lint, command output, mechanical file sweeps. |
| **sonnet** | Branching work — investigation whose next step depends on findings, triage, moderate edits with a few decision points. |
| **opus** | General coding — features, non-trivial bugs, refactoring with judgment. |
| **fable** | Advanced coding, deep reasoning, research, and review — where correctness hinges on subtle judgment or adversarial scrutiny. |

Effort is a second, independent dial (`low|medium|high|xhigh|max`; omit for
haiku, which has none). Set it by the task's difficulty, not its model. Pick
the cheapest model that clears the quality bar — a stronger model that
wouldn't change the output is wasted — then, to make a worker think harder,
raise its effort, not its model.
