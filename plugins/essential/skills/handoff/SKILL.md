---
name: handoff
description: 'Create or execute a context-complete cross-domain plan as an orchestrator. Use when another agent must continue without prior context, or when a multi-domain plan needs coordinated execution while this skill retains decision ownership. For coding-session persistence, use coding:handover.'
---

# Handoff

Create or execute a context-complete cross-domain plan. This skill owns portable
planning and coordinated execution; `coding:handover` instead persists the current
coding session in continuation files.

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
