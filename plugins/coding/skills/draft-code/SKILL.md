---
name: draft-code
description: Draft TypeScript-compliant code skeletons with canonical TODO(implementation) placeholders. Use when starting an already-specified implementation or preparing typed production structure for later completion; do not implement business logic or create ambiguous plain TODO markers.
model: opus
context: fork
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task
argument-hint: "<instruction>"
---

# Draft Code Skeleton

Creates TypeScript-compliant production skeletons with explicit
`TODO(implementation):` markers, type definitions, and function signatures. It
may outline pending tests, but test markers belong to `coding:complete-test`;
production stubs belong to `coding:complete-code`.

## Boundaries

- Use for: starting an already-specified implementation, or preparing typed
  production structure and test scaffolds for later completion.
- Do not use for: implementing business logic or producing production-ready
  code (`coding:write-code`), writing complete tests with assertions beyond the
  scaffold (`coding:complete-test`), or modifying existing implementations
  (`coding:refactor` or `coding:fix`).
- Reject when: the instruction is too vague to create meaningful types, the
  request is for implementation rather than a skeleton, the target directory
  does not exist, or the skeleton would conflict with existing code structure.

## Inputs

- **Required**: `<instruction>` — the feature or module to skeleton, specific
  enough to derive types, interfaces, and function signatures.
- **Optional**: design and handover documents discovered in step 1 refine the
  skeleton's shape.
- **Prerequisites**: an existing target directory inside a TypeScript project.

Apply these constitution standards while drafting:

| Standard | Purpose |
|---|---|
| `documentation/write` | JSDoc structure and placeholder comments |
| `file-structure` | Project directory layout and organization |
| `function/write` | Function signatures, parameter types, return types |
| `naming/write` | Naming conventions for files, types, functions |
| `testing/write` | Test file structure, describe/it patterns |
| `typescript/write` | Type definitions, interfaces, generics |
| `universal/write` | General code authoring conventions |

## Workflow

1. Parse the instruction into required types, interfaces, functions, and file
   structure, then discover context with Glob (never `find` in Bash): design
   docs (`DESIGN.md`, architecture `**/*.md`) and handover files — extract
   current state, decisions, gotchas, and established patterns from
   `CONTEXT.md`; solved problems and insights from `NOTES.md`; goals, success
   criteria, and current phase from `PLAN.md`. Read neighboring modules for
   existing patterns and merge design with handover context.
2. Plan the structure before writing: file organization, type hierarchy, and
   test layout per the standards above.
3. Draft type definitions (interfaces, type aliases, enums) and function stubs
   with JSDoc, marking every incomplete body with the canonical placeholders in
   [references/drafting-patterns.md](references/drafting-patterns.md) —
   `TODO(implementation):` comments plus the `IMPLEMENTATION:` sentinel throw
   wherever a value is expected.
4. Draft the test structure: describe blocks per behavior, planned cases
   covering all functionality, and only the mock factories, fixtures, and
   helpers the skeleton needs. When no interface exists yet, use
   `describe.todo()`/`it.todo()`; once an interface exists, write real
   assertions that fail red until implementation — the desired TDD signal
   (details in references/drafting-patterns.md).
5. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker remains,
   then report the blocker instead of looping.

## Verification

- TypeScript compiles with no errors and all imports resolve (`npx tsc
  --noEmit` or the repository equivalent).
- `npm run lint` (or equivalent) passes; file organization and naming match the
  standards above.
- `npm run test` (or equivalent) runs without collection errors; scaffolded
  tests are pending or red exactly as designed.
- Every placeholder uses a canonical form from
  references/drafting-patterns.md — no bare `TODO:` markers, which
  `coding:complete-code` refuses to claim.

## Completion

Report the parsed instruction; context sources discovered; files created with a
one-line purpose each; counts of types defined, functions drafted, and markers
placed; verification commands with results; and next steps — complete
production stubs with `coding:complete-code`, then route pending test markers
to `coding:complete-test`.
