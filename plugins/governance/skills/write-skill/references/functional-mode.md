# Transient Functional and Trigger Checks

Loaded by the `verify` action (from `verify.md`) for `mode=functional` or
`mode=full`. These checks use representative prompts as temporary working data.

<IMPORTANT>
- Keep cases in context. If written notes help, use a Markdown table based on
  `../../../constitution/references/check.md` in an OS temporary directory and
  delete it before staging or committing.
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

## Optionally exercise isolated runtime prompts

Run executable cases only when `runtime: true`. Name the harness, use one fresh
session per prompt, and load only the affected plugin. Avoid explicit invocation
for trigger checks because Claude Code's `/skill-name`, Codex's `$skill-name`,
and ChatGPT's `@skill-name` select a skill directly instead of exercising
implicit discovery.

For Claude Code trigger-only checks, a suitable starting command is:

```bash
claude --bare --print --plugin-dir <plugin-root> \
  --output-format stream-json --verbose --no-session-persistence \
  --tools Skill "<representative prompt>"
```

Inspect the structured stream for target-skill invocation on positive prompts
and its absence on near misses. If the skill needs tools or writes files, run
the prompt in a disposable directory or detached worktree with only the
minimum required tools, then compare the resulting output and filesystem state
with the case expectation. Treat the plugin and its commands as untrusted.

Do not fall back to a non-isolated Claude session when `--bare` authentication,
required tools, credentials, or sandboxing are unavailable. For Codex, run only
an isolated evaluation mechanism documented and available in the target
environment; this repository defines no general Codex runtime evaluator, so do
not translate the Claude command or use explicit `$skill-name` as discovery
evidence. Report runtime as `blocked` with the exact missing prerequisite;
otherwise report `observed` per case. Runtime failure may justify a targeted
fix, but never weakening the case expectation merely to pass.

## Report and clean up

Return one row per case with prompt, expected owner/behavior, evidence kind
(`reasoned` or `observed`), outcome, and rationale. Include runtime status as
`exercised`, `not requested`, or `blocked`. Delete any temporary case matrix.
