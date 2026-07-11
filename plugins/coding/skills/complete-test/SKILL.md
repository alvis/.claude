---
name: complete-test
description: Author and improve tests for pending test cases, coverage gaps, fixtures, and redundancy cleanup. Use for test TODOs, it.todo or describe.todo entries, explicit test-writing requests, or coverage work. Production implementation stubs belong to complete-code; diagnosed failures belong to fix.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Task, Read, Glob, Edit, Grep
argument-hint: "[scope] [--coverage=<percent>] [--framework=<name>]"
---

# Complete test

Own test authoring and test-suite maintenance. Do not implement production behavior, rewrite a failing application fix, or create placeholders for unspecified features.

## Inputs and boundaries

- Scope: files, package, feature, or explicit pending-test marker.
- Optional coverage target (default repository target), framework, and existing test paths.
- Read project test scripts/configuration and the source under test before editing.
- `FIXME` and production failures route to `coding:fix`; production stubs route to `coding:complete-code`; new behavior without a testable contract routes to `coding:write-code`.

## Workflow

1. Resolve the scope and test command from the project. Inventory existing tests, fixtures, pending markers, and coverage configuration. Capture a baseline with the repository's test/coverage script.
2. Define the smallest cases that prove the contract: happy path, meaningful boundaries, failure behavior, integration seams, and the pending marker's intended behavior. Reuse fixtures and helpers; remove redundant cases only when the replacement preserves signal.
3. Write tests first for the missing behavior. Keep tests deterministic, isolated, readable, and aligned with neighboring suite conventions. Do not weaken assertions to make a test pass.
4. Run the focused test command after each coherent batch, then the project's full test and coverage commands. Diagnose failures from their evidence; if the source is wrong, hand off to `coding:fix` instead of editing production code here.
5. Review the diff for duplicate fixtures, over-mocking, brittle timing, missing cleanup, and tests that pass without exercising the intended behavior. Re-run coverage and record any justified uncovered branch.

## Verification

Require passing focused tests, passing full suite, coverage at the requested target (or an explicit repository limitation), and no remaining owned `TODO`/`it.todo`/`describe.todo` markers. Report test files, cases added/removed, coverage, commands, and unresolved failures.

## Completion

Return a concise test report. Do not claim production implementation, bug fixes, or coverage for code outside the selected scope.
