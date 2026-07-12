---
name: handoff
description: 'Create or execute a context-complete cross-domain plan as an orchestrator. Use when another agent must continue without prior context, or when a multi-domain plan needs coordinated execution while this skill retains decision ownership. For coding-session persistence, use coding:handover.'
---

# Handoff

Create or execute a context-complete cross-domain plan. This skill owns
portable planning and coordinated execution; `coding:handover` instead
persists the current coding session in continuation files.

## Boundaries

- Use for: writing a plan another agent can execute without any of this
  session's context, and orchestrating a multi-domain plan's execution while
  retaining decision ownership.
- Do not use for: persisting a coding session for later continuation
  (`coding:handover`), or doing the planned work inline — execution is always
  delegated.

## Inputs

- **Required**: the work to plan, or an existing plan to execute.
- **Optional**: the `Workflow` tool for multi-phase execution; `coding:*`
  skills when available — confirm availability before routing to one,
  otherwise name the equivalent action or files without invoking it.

## Workflow

1. **Clarify until nothing is left to guess.** Ask as many clarifying
   questions as needed; with every question give your recommended answer and
   the reason for it, so the user can confirm quickly and whoever executes
   never has to guess intent.
2. **Write the plan.** Open with a self-contained **Goal** block the user can
   copy and paste verbatim to initiate the work — it states the intended
   outcome fully on its own, without relying on your context. Then write the
   plan with enough detail and context that an agent with no idea what you
   are working on can take over without getting lost: concrete file paths,
   constraints, decision criteria, and success checks per phase.
3. **Execute as orchestrator** (when execution is requested). Run a
   multi-phase plan as a `Workflow` — one phase per stage, fanning out to
   subagents where a phase allows — instead of doing the work inline. Act as
   the orchestrator and decision maker only: route each phase to the right
   agent with complete context, synthesize the results, and make the calls.
   Delegate all execution — reading, writing, running, testing — to
   subagents; never do the work yourself.
4. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker remains,
   then report the blocker instead of looping.

## Verification

- The Goal block stands alone: pasted into a fresh session, it fully states
  the intended outcome.
- A reader without this session's context could execute the plan — no step
  depends on unstated knowledge.
- When executed: every phase was delegated with complete context, and each
  phase's results were checked against the plan's success criteria before the
  next phase started.

## Completion

Report the plan's location and its Goal block, the decisions made while
planning, and — when executed — each phase's outcome and any open questions
or deviations from the plan. A blocked execution names the phase, what was
attempted, and what decision or input is needed to continue.
