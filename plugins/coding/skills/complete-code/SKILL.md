---
name: complete-code
description: Complete explicit production implementation stubs in an existing scope. Use for canonical implementation TODOs, temporary production stubs, and draft-code sentinels; route bugs, test work, unstubbed functionality, new features, and ambiguous markers to their owning workflows.
model: opus
context: fork
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task
argument-hint: "<scope>"
---

# Complete Code

Finish only explicit production implementation stubs. The surrounding contract,
types, tests, and specification must already make the intended behavior clear.

## Inputs and boundaries

Accepted markers are:

- `TODO(implementation):` markers.
- A legacy implementation TODO only when its text unambiguously requests a
  production implementation.
- `TEMP:` stub implementations whose replacement behavior is explicit.
- The exact sentinel form `throw new Error('IMPLEMENTATION: ...')` emitted by
  `coding:draft-code`.

Do not claim neighboring work:

| Finding | Action |
|---|---|
| `FIXME` | Route to `coding:fix`. |
| Test-file TODO, `it.todo`, or `describe.todo` | Route to `coding:complete-test`. |
| Missing functionality without an explicit stub | Route to `coding:write-code`. |
| Newly requested feature | Route to `coding:write-code`. |
| Ambiguous marker | Leave untouched and report it as blocked. |
| `HACK` or `WORKAROUND` | Preserve unless the user explicitly routes it to `coding:fix` or `coding:refactor`. |

If `$ARGUMENTS` contains `--test-only`, stop immediately with exactly:

> `--test-only` was removed; use `coding:complete-test <scope>`.

This skill may read and run existing tests to discover and verify the established
contract. It does not author broad test suites, pursue coverage, create replacement
placeholders, or guess behavior that the repository does not specify.

## Workflow

1. Validate the scope and reject the removed flag before scanning.
2. Find accepted markers, then classify every nearby TODO-like marker using the
   routing table above.
3. Read the specification, types, call sites, siblings, and existing tests needed
   to establish each accepted stub's behavior.
4. If behavior remains ambiguous, leave the marker untouched and record the
   blocker. Do not infer a new feature contract.
5. Replace each accepted stub with the smallest production implementation that
   satisfies the established contract. Remove the marker; never replace it with a
   new placeholder.
6. Run focused existing tests, type checks, and mechanical lint checks appropriate
   to the changed scope.

## Completion

Report completed markers with file locations, routed findings, blocked ambiguous
markers, changed files, and exact verification commands and results.
