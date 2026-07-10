---
name: verify-skill
description: "Use when validating a new or changed Claude Code skill, checking structural and repository policy compliance, testing whether descriptions trigger accurately, or grading representative skill outputs before deployment."
model: opus
context: fork
agent: general-purpose
---

# Verify Skill

## Boundaries

- Claude Code's validator owns manifest and frontmatter schema correctness.
- `quick_validate.py` owns repository policies only; it must not duplicate the
  evolving Claude schema.
- Functional and trigger checks are required when behavior or discovery changed,
  not for a wording-only edit with unchanged meaning.

Shared authoring policy lives in
`../../constitution/references/authoring-invariants.md`.

## Inputs

- Required: a `SKILL.md`, skill directory, plugin, marketplace, or plugins path.
- Optional mode: `structural`, `functional`, or `full` (default `full`).
- Optional evaluation data: `evals/evals.yaml` and representative prompts.

## Workflow

1. Resolve the target and enumerate affected skills and plugin roots.
2. Run official strict validation for every affected plugin. Report Claude's
   errors verbatim enough to identify their source; do not reinterpret valid
   fields through a private schema.
3. Run `scripts/quick_validate.py` on the target. Review body length,
   description budget, unresolved local references, and placeholders.
4. For functional or full mode, load existing evals or derive a small set from
   the owned outcome. Follow `references/functional-mode.md` for execution and
   grading details.
5. Test positive trigger prompts and nearby negative prompts. A pass requires
   the intended skill to trigger without stealing work from its neighbors.
6. Aggregate evidence by skill. When fixes are requested, change only reported
   causes and rerun the failed checks.

The validator does not require fixed headings, personas, diagrams, subagent
prompts, XML report envelopes, or a section literally named “Skill Completion.”

## Verification commands

```bash
claude plugin validate --strict <plugin-path>
python3 scripts/quick_validate.py <skill-or-plugin-path>
python3 scripts/run_trigger_eval.py --help
```

Run the first two commands after every fix iteration. Trigger and functional
results must include the prompt, observed behavior, and pass/fail rationale.

## Completion

Return a concise per-skill verdict with official validation status, policy
issues, functional/trigger evidence when applicable, and actionable failures.
