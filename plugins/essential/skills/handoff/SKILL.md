---
name: handoff
description: >
  Write a hand-off-ready plan and drive its execution as an orchestrator. Use when
  producing a plan that another agent — without your current context or mental
  model — must pick up without getting lost, or when executing a multi-phase plan
  that should run as a workflow while you stay the orchestrator and decision maker.
---

# Handoff

Write the plan with as much detail and context as possible such that it can be
handed over to another agent — without your context and idea about what you're
working on — to take over without getting lost.

## Before writing the plan

- Ask as many clarifying questions as possible until nothing is left to guess.
  With every question give your recommended answer and the reason for it, so the
  user can confirm quickly and whoever executes never has to guess intent.

## The plan

- Open every plan with a clear, self-contained **Goal** — a single block the user
  can copy and paste verbatim to initiate the work. It must state the intended
  outcome fully on its own, without relying on your context.

## Executing the plan

- For multi-phase execution, run the plan as a **Workflow** — one phase per stage,
  fanning out to subagents where a phase allows — instead of doing the work inline.
- Act as the **orchestrator and decision maker only**: route each phase to the right
  agent, hand over complete context, synthesize the results, and make the calls.
  Delegate all execution — reading, writing, running, testing — to subagents. Never
  do the work yourself.
