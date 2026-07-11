---
name: complete-test
description: Author and improve tests for pending test cases, coverage gaps, fixtures, and redundancy cleanup. Use for test TODOs, it.todo or describe.todo entries, explicit test-writing requests, or coverage work. Production implementation stubs belong to complete-code; diagnosed failures belong to fix.
model: opus
context: fork
allowed-tools: Bash, Task, Read, Write, Edit, Glob, Grep
argument-hint: "[scope] [--coverage=<percent>] [--framework=<name>]"
---

# Complete test

Own test authoring and test-suite maintenance. Do not implement production behavior, rewrite a failing application fix, or create placeholders for unspecified features.

## Inputs and boundaries

- Scope: files, package, feature, or explicit pending-test marker.
- Optional coverage target (default: 100% statements, branches, functions, and lines unless an explicit repository policy sets another target), framework, and existing test paths.
- Read project test scripts/configuration and the source under test before editing.
- `FIXME` and production failures route to `coding:fix`; production stubs route to `coding:complete-code`; new behavior without a testable contract routes to `coding:write-code`.

## Workflow

1. Resolve scope and repository-native test/coverage commands. Inventory each source file, current tests, pending markers, fixture ownership, and configured exclusions. Capture per-source and aggregate coverage before editing.
2. Partition independent source/test pairs into coherent batches. Parallelize only disjoint files and fixtures; serialize shared fixtures, global setup, snapshots, and integration state. Record the batch-to-file map so no source is skipped.
3. For every proposed case apply **test → measure → keep**: add the smallest test, run its focused suite, measure the intended source/branch, and keep it only when it adds behavioral evidence or coverage. Delete tests that merely restate another assertion.
4. Cover happy paths, meaningful boundaries, failures, and integration seams until every selected source reaches 100% or the repository's explicit policy threshold. Report uncovered lines/branches per source; aggregate coverage cannot conceal a weak file.
5. Plan fixtures before changing them: identify consumers, lifecycle, mutation, and migration order. For a fixture rewrite, migrate every consumer, run focused suites, then the full suite. Do not leave old and new fixture systems in parallel.
6. Test redundancy cleanup by remove → measure → restore: remove one candidate, rerun focused tests and coverage, keep it removed only if signal and coverage are unchanged; otherwise restore it. Never infer redundancy from similar prose alone.
7. After each batch, run focused tests and coverage. If production behavior is wrong, route to `coding:fix`; do not edit source here. After all batches, run the complete repository test, coverage, type, and lint gates that apply.
8. Request one independent final test review covering missing behavior, weak assertions, fixture correctness, nondeterminism, and per-source coverage. Apply justified test-only corrections and rerun the affected and full gates.

## Verification

Require passing focused and full suites, coverage at the requested target (or a cited repository policy/technical limitation), and no remaining owned pending markers. Report batches, files/cases added and removed, fixture migrations, focused/full commands, independent-review result, aggregate metrics, and per-source statements/branches/functions/lines. Name every justified gap.

## Completion

Return a concise test report. Do not claim production implementation, bug fixes, or coverage for code outside the selected scope.
