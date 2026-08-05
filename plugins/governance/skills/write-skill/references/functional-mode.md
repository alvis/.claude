# Transient Functional and Trigger Checks

Loaded by the `verify` action (from `verify.md`) for `mode=functional` or
`mode=full`. These checks use representative prompts as temporary working data.

<IMPORTANT>
- Keep cases in context. If written notes help, use a Markdown table in an OS
  temporary directory and delete it before staging or committing.
- Label paper-only conclusions as `reasoned`. Reserve `observed` for commands
  that actually executed in an isolated runtime.
</IMPORTANT>

## Build the representative-case matrix

Use caller-supplied prompts first, then derive only the missing coverage from
the skill's owned outcome, description, boundaries, workflow, and neighboring
skills. Keep the matrix small and change-focused:

- one direct positive request for the owned outcome;
- one paraphrased positive request when discovery wording changed;
- one nearby negative request owned by a neighboring skill;
- one behavior, missing-input, failure, or verification-shortcut case relevant
  to the changed workflow.

For each case record the prompt, expected owner, expected behavior, evidence to
inspect, and whether the result is reasoned or observed. `mode=functional` may
omit discovery-only cases; `mode=full` includes both trigger and behavior
coverage.

## Run the paper-only blindspot check

Compare every prompt with the target description, explicit boundaries, and the
closest competing skill descriptions. Then trace the expected behavior through
the target workflow and verification contract. A reasoned pass requires:

- positive prompts clearly belong to the target;
- near misses clearly belong elsewhere and are not stolen by broad wording;
- required inputs and failure behavior are explicit;
- shortcuts cannot bypass required verification;
- the expected outcome is supported by instructions or deterministic scripts,
  not by an unstated assumption.

Fix a discovered blindspot in the owning instruction, rerun the affected cases,
and bound the loop to two iterations. Paper reasoning does not establish actual
skill invocation or runtime output in any harness.

## Optionally exercise an available harness

Run executable cases only when `runtime: true` and the target harness provides
a documented isolated evaluation mechanism. Use one fresh session per prompt
and a natural-language request that expresses the representative intent without
naming or explicitly selecting the skill. Compare observed activation and
output with the case expectation. If no such evaluator is available, report
runtime as `blocked` with the missing prerequisite; do not translate another
harness's command by analogy or weaken the expected result.

## Report and clean up

Return one row per case with prompt, expected owner/behavior, evidence kind
(`reasoned` or `observed`), outcome, and rationale. Include runtime status as
`exercised`, `not requested`, or `blocked`. Delete any temporary case matrix.
