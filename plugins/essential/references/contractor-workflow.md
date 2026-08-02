# Contractor workflow

Use this contract for material implementation or artifact work. Treat a wrong
assumption as rework you must prevent and an unnecessary question as cost paid
by the user.

## Applicability

<IMPORTANT>
Use the full gate for a new module, schema, authentication, money, migration,
deletion, or any change whose blast radius is not obvious. A typo, rename, or
change under roughly 20 lines may use the short path only after investigating
the relevant source, tests, configuration, dependency manifests, and existing
abstractions; checking for repository contradictions; and establishing one
obvious low-blast-radius form. The short path skips the full Goal, Blocking
questions, Assumptions, and Plan packet and its approval pause, then implements
only that form directly within the stated request and performs proportionate
validation. If investigation finds ambiguity, contradiction, or a larger blast
radius, use the full gate and pause before implementation. The threshold is a
blast-radius heuristic, not a correctness exemption. Be more suspicious than
usual of assumptions around one-way or destructive changes.
</IMPORTANT>

Review-only work keeps its read-only charter and does not wait on an
implementation approval packet, but it still investigates before asking about
facts discoverable in the repository.

## Investigate before asking

Read the relevant source, tests, configuration, dependency manifests, and
existing abstractions first. Any fact discoverable in under a minute is
research owed by the agent, not a user question. Do not ask about the test
framework, language version, lint rules, error-handling conventions, directory
layout, or existing abstractions when the repository already answers it. Raise
contradictions in the repository as findings.

## Approval packet

<report>

### Goal

Write one paragraph in your own words. Include the acceptance criteria you will
use to decide whether the work is complete.

### Blocking questions (0–3)

Ask only when a wrong answer would throw work away rather than require a local
adjustment. Give every question a recommended default so the user can answer
“yes to all”; never ask an open question where a proposed answer would do. If
nothing is genuinely blocking, write `0 — none`.

### Assumptions

Number assumptions so each is specific and falsifiable. Cover only categories
the task touches:

- **Data:** shape, volume, trust, encoding, and malformed-input behavior.
- **Failure:** timeout, partial write, and downstream failure behavior—retry,
  fail loudly, or degrade.
- **Boundaries:** callers, public versus internal surface, and compatibility.
- **State:** concurrency, idempotency, transactionality, and ordering.
- **Environment:** runtime, deployment, reachable systems, and permissions.
- **Scope:** deliberate non-goals and deferred work.
- **Testing:** cases to cover and cases intentionally left uncovered.

### Plan

Name files or artifacts to create or modify, key function/type signatures or
equivalent contracts and metrics, and the order of work. For each real choice,
name the alternative rejected and why in one clause.

</report>

Then stop. Do not implement, delegate execution, or quietly turn a missing
answer into an assumption before the owning approver accepts the packet.

## Role gates

### Project Manager

Investigate before asking the user, present the approval packet, and wait before
delegating a material change. After approval, route the accepted goal and
criteria to the appropriate domain lead and own any change to the user
contract.

### Domain lead

Investigate the domain before asking the Project Manager, present the packet for
the initiative, and wait for approval before decomposing execution into
delegated work. After approval, decide the approach, assign bounded slices, and
re-plan when evidence changes the premise.

### Implementer

Investigate the assigned slice before asking its owner. A mission capsule that
explicitly names an approved plan satisfies the pause; otherwise return the
packet and wait. After approval, implement only the accepted plan and report a
deviation before changing its design.

## After approval

Implement the plan as approved. If an assumption is wrong or the plan does not
survive contact with the repository, stop and report the evidence, the affected
decision, and the recommended re-plan. Do not quietly improvise a different
design or continue with an approach you no longer believe is correct.
