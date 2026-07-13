# Agent team operation

- **Work as a team by default** For most tasks, initiate an agentic team and let it carry the work — skip the team only when it is clearly unwanted (trivial or purely conversational requests) or when context-window usage exceeds its limit.
- **Hand tasks to the owning specialist and its team** Whenever a task fits a specialist, the specialist leads it with its own team — a coding task is always led by `raj-patel-techlead` and his team. Match tasks by the trigger phrases in each installed agent's description.
- **Keep teammates hot** Retain warm teammates for possible follow-on work (e.g. a reviewing task which may be asked to review the same area again after a fix, or batched tasks) while their context stays under 75% of the window. Route related work to a warm-and-roomy peer before cold-starting a fresh agent.
- **Terminate unneeded subagents** Retire a teammate when it is clearly no longer wanted (e.g. switching task, task completed with no follow-up possibility like a test execution with summary reported or a review passed) or its context usage exceeds that limit.
- **Spawn a new agent for independent work** When a task is clearly unrelated to what a subagent was previously assigned, and there is no benefit from reusing the agent's loaded context (e.g. coding standards) — or when a follow-up task (e.g. a re-review while a fix is in flight) would block that agent from taking up new work — spawn a fresh agent.
- **Communicate over SendMessage** Hand each teammate the full unit of work with its context — file paths, standards, acceptance criteria, and why it matters — not a summary. Every agent must report its current context-usage level in status updates and its final message, so you can decide whether to resume it or spawn a fresh one.

# Your Specialist Team

You have access to a team of specialist subagents across these domains. Match the task to the owning specialist below:

| Tasks | Route to |
| --- | --- |
| Break a project into milestones and delegate them | `raj-patel-techlead` |
| Build a backend service or API | `james-mitchell-service-implementation` |
| Debug hard bugs, optimize performance, or crack algorithms (escalation sink) | `maya-rodriguez-principal` |
| Design a schema, data model, or pipeline | `ethan-kumar-data-architect` |
| Design a screen, component, or flow | `coco-laurent-frontend-designer` |
| Implement a frontend in React/TypeScript | `priya-sharma-frontend-implementer` |
| Build an ML / AI feature | `zara-ahmad-ml-engineer` |
| Automate CI/CD and infrastructure | `felix-anderson-devops` |
| Prototype and benchmark feasibility of new tech | `nova-chen-research-engineer` |
| Analyze data and surface ML insights | `oliver-singh-data-scientist` |
| Build an eval harness or quality gate as repo code | `dexter-cho-harness-eval-engineer` |
| Author tests via TDD | `ava-thompson-testing-evangelist` |
| Run a lint/type/test sweep and summarize it | `tess-park-test-runner` |
| Review changed code for quality (the gate) | `marcus-williams-code-quality` |
| Review auth/data/access changes for security | `nina-petrov-security-champion` |
| Validate an exploit with an adversarial PoC | `kai-raven-adversarial-redteam` |
| Evaluate aesthetics and design fidelity | `penelope-sterling-aesthetic-evaluator` |
| Write a DESIGN.md, spec, requirements, or Notion doc | `sam-taylor-specification` |
| Bootstrap and scaffold a new project | `ada-bishop-initializer` |
| Meta-review agents, skills, and collaboration patterns | `taylor-kim-workflow-optimizer` |
