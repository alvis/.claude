---
name: skill-name
description: "[Description] — third person, what the skill does plus a 'Use when...' clause with concrete trigger phrases a user would actually type; 25-60 words; lead with the key use case."
---

<!-- AUTHOR GUIDE — delete every comment before shipping. Policy lives in
plugins/governance/constitution/references/authoring-invariants.md. This
template is a seed, not a heading contract: adapt headings to the capability.

Frontmatter
- name: kebab-case, identical to the skill directory name.
- description: third person, what + when, key use case first. Repository
  budget is 25-60 words (Claude Code allows up to 1024 characters). Name a
  neighboring exclusion only when it prevents a real trigger collision.
- Optional fields Claude Code supports: argument-hint, allowed-tools,
  disallowed-tools, model, effort, context (fork = fresh isolated subagent),
  agent, user-invocable, disable-model-invocation, paths, hooks. Add a field
  only when it changes behavior; coding:commit and coding:finalize-commits
  are worked examples.
-->

# [Skill Name]

[One or two sentences naming the owned outcome — and, when ownership is
contested, which neighboring skill owns the adjacent work.]

## Boundaries

- Use for: [specific triggers and owned outcomes].
- Do not use for: [neighboring responsibilities and their owning skills].

## Inputs

- **Required**: [minimum information needed to begin].
- **Optional**: [flags, scope, or defaults that change behavior].
- **Prerequisites**: [tools, credentials, or running state that must exist
  before the skill starts — delete this line when there are none].

## Workflow

<!-- Write steps a reader can execute without asking questions.
- State each step's input and output whenever the handoff between steps is
  not obvious from the step itself.
- Make execution intent explicit: "Run scripts/x.py" executes a script; "See
  references/x.md" loads instructions.
- Match freedom to fragility: exact commands or scripts for fragile and
  deterministic operations, heuristics for open-ended judgment. Offer one
  default tool with an escape hatch, not a menu of options.
- No magic numbers: give every bound or threshold its reason. List the
  packages any bundled script depends on.
- Keep the always-used path inline. Put bulky conditional instructions in
  references/<topic>.md and link them at the decision point; keep short
  conditions inline. References stay one level deep from SKILL.md; give a
  reference file over ~100 lines a table of contents. Condensing a skill must
  never drop skill-specific procedure — concrete bounds, dispatch rules,
  decision criteria, and command sequences move to `references/`, they are
  not deleted.
- Delegation is a context-economics decision: delegate a step when doing it
  directly would consume more session context than describing the task and
  reading the report — bulk file reads, noisy command output, many
  independent resources. Do small work inline. When a step does delegate,
  follow plugins/governance/constitution/references/delegation.md and state
  the dispatch bounds you adopt at that step.
- Wrap hard guardrails in <IMPORTANT>...</IMPORTANT> and machine-readable
  output contracts in <report>...</report> per the Content Boundary
  Convention in authoring-invariants.md; name tags for the content's role,
  never to echo a heading.
- Use consistent terminology throughout, forward slashes in paths, and no
  time-sensitive facts.
-->

1. Confirm the target and constraints.
2. Perform the smallest complete workflow that produces the owned outcome.
3. Handle explicit failure and ambiguity cases without widening scope.
4. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker remains,
   then report the blocker instead of looping.

## Verification

<!-- Keep the two repository checks. Add the skill-specific checks that prove
the promised outcome actually happened, not merely that steps ran. -->

- Run the checks that demonstrate the promised outcome.
- Validate frontmatter with `claude plugin validate --strict <plugin-path>`.
- Run repository policy checks with `quick_validate.py <skill-or-plugin-path>`.

## Completion

Report the outcome, verification performed, changed artifacts, and unresolved
issues. Do not require a fixed report envelope when plain language is clearer.

<!-- Name this skill's concrete success evidence: which artifacts exist, which
checks passed, and what a partial or blocked result must still state. Specify
exact output fields only when a caller parses them. -->
