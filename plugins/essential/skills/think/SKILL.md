---
name: think
description: 'Structure pre-implementation reasoning for ambiguous problems. Use when the requested outcome, constraints, or safe solution are unclear and deliberate options, objections, dependencies, edge cases, and rollback need to be resolved before any modification or creation begins.'
model: opus
allowed-tools: Read, Glob, Grep, Bash
argument-hint: "[problem-or-question]"
---

# Think

Structured deliberate reasoning before acting: force explicit reasoning about
an ambiguous problem before any code, file, or configuration is touched. The
output is a decision, not an artifact — implementation is handed off to the
right skill only after explicit approval.

## Boundaries

- Use for: tasks with multiple valid approaches where the best is not obvious,
  underspecified requirements with hidden constraints, irreversible changes
  needing validation first, and grounding a fresh Plan Mode plan in real
  constraints.
- Do not use for: problems with a crystal-clear solution path — go straight to
  the implementing skill.

## Inputs

- **Required**: the problem or question (`$ARGUMENTS`); when empty, surface
  the ambiguous problem from the conversation context.
- **Optional**: `coding:*` skills for the handoff step — confirm availability
  before recommending one, otherwise describe the implementation step
  generically.

<IMPORTANT>
- Never execute, create, or modify files during steps 1-5.
- Never delegate to subagents at any point in this skill — all thinking is
  done here.
- Be opinionated: commit to one recommendation and resolve every "it depends"
  before presenting.
</IMPORTANT>

## Workflow

1. **Understand.** Read up to 3 relevant files (existing patterns, prior
   decisions, related skills or standards) to establish real constraints —
   not imagined ones; the cap keeps this a reasoning pass, not an audit. Then
   write 1-2 sentences answering: what exactly is being asked, why it is
   non-trivial (what makes a naive answer wrong), and what a bad answer looks
   like. Output: a crisp problem statement anchored in observed constraints.
2. **Generate approaches.** Produce 2-3 distinct options — not variations of
   one idea — always including a minimal option: the smallest change that
   could work. For each, state what it does, cost/complexity, reversibility,
   and what it breaks or ignores. Mark your recommended option and the
   evidence supporting it from step 1 observations, not intuition alone.
3. **Challenge.** Write the 2-3 strongest objections to your own
   recommendation. For each, state whether it changes the recommendation and,
   if not, specifically why not. Then name the falsification signal: what
   evidence would cause you to switch recommendations.
4. **Validate completeness.** Check the recommendation against every item;
   fix it before proceeding when one fails:
   - No placeholders, "TBD", or deferred decisions.
   - All upstream dependencies identified (what must exist or be true first).
   - At least one edge case or failure mode named.
   - Rollback path identified — or explicitly confirmed unnecessary and why.
5. **Present and stop.** Present the recommendation in this format and wait:

   <report>

   ```text
   RECOMMENDATION: [one-sentence summary]

   Approach: [chosen option name]
   Reasoning: [2-3 sentences — what you observed + why this wins]
   Tradeoffs accepted: [what you're giving up]
   Edge cases handled: [named]
   Rollback: [path or "not needed because X"]

   WAITING FOR APPROVAL — not implementing until confirmed.
   ```

   </report>

   On rejection: narrow the specific objection and return to step 2 with the
   new constraint. On approval: proceed to step 6.
6. **Hand off** (only after explicit approval). Discover available skills
   with `Glob: plugins/*/skills/*/SKILL.md`, read the `name` and
   `description` frontmatter of the 1-2 most relevant candidates, select the
   best fit for what the approved recommendation requires, and invoke it with
   full context: the approved recommendation, the observed constraints from
   step 1, and any relevant file paths.
7. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker remains,
   then report the blocker instead of looping.

## Verification

- No file was created or modified before approval, and no subagent was
  dispatched at any point.
- The presented recommendation passes every step 4 completeness item and
  names its falsification signal.
- The handoff (when reached) passed the approved recommendation, observed
  constraints, and relevant file paths to the invoked skill.

## Completion

Report the recommendation and the user's decision. After an approved handoff,
name the invoked skill and the context handed to it. When the user rejects and
no option survives the added constraint, report the constraint that eliminated
each option instead of forcing a recommendation.
