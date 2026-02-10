# Documentation: Violation Scan

> **Prerequisite**: Read `meta.md` in this directory first for dependencies, exception policy, and rule groups.

Any single violation blocks submission by default.
If a violation is detected, load the matching rule guide at `./rules/<rule-id>.md`.

## Quick Scan

- DO NOT write comments that restate obvious behavior [`DOC-CONT-01`]
- DO NOT add inline comments that provide no value [`DOC-CONT-02`]
- DO NOT leave forbidden comment patterns in source [`DOC-CONT-03`]
- DO NOT ship exported APIs without required docs [`DOC-CONT-04`]
- DO NOT start comments with uppercase (use lowercase), except for code/type references (`UserService`) and section headers (`// NAME //`), such as `// This validates token` [`DOC-FORM-01`]
- DO NOT use one-line JSDoc on functions with params or non-void return, or block comments (`/* */`) for section headers, such as `/** one line */ fn(a)` or `/* USER */` [`DOC-FORM-02`]
- DO NOT write function JSDoc summaries with uppercase, imperative mood, or trailing period; must use lowercase third-person verb (`/** validates input */` not `/** Validate input. */`) [`DOC-FORM-03`]
- DO NOT capitalize `@param` descriptions unless the first word is a type/interface/acronym reference, such as `@param userId unique identifier` not `@param userId User Identifier` [`DOC-FORM-04`]
- DO NOT commit temporary tags [`DOC-LIFE-01`]
- DO NOT leave review-only markers in merged code [`DOC-LIFE-02`]
- DO NOT use persistent tags inconsistently [`DOC-LIFE-03`]
- DO NOT leave comments that drift from implementation [`DOC-LIFE-04`]

## Rule Matrix

| Rule ID | Violation | Bad Examples |
|---|---|---|
| `DOC-CONT-01` | Comment restates obvious behavior | `// increment i`; `// increment counter by 1` |
| `DOC-CONT-02` | Inline comment is noise | `// set x to 1`; `return user.name; // obvious comment` |
| `DOC-CONT-03` | Forbidden comment pattern present | `// modified by A on 2025-01-10`; `// modified by John on 2024-01-15` |
| `DOC-CONT-04` | Exported API lacks docs | `export interface X {}` |
| `DOC-FORM-01` | Comment starts with uppercase (should be lowercase unless code reference or section header) | `// This validates token`; `// This function handles user authentication` |
| `DOC-FORM-02` | One-line JSDoc on function with params/return, or block comment used for section header | `/** one line */ fn(a)`; `/* USER */` |
| `DOC-FORM-03` | JSDoc summary uses uppercase, imperative mood, or trailing period instead of lowercase third-person verb | `/** Validate token. */`; `/** validate email format */` |
| `DOC-FORM-04` | `@param` description capitalized without type/interface/acronym justification | `@param userId User Identifier`; `@param userId The unique identifier` |
| `DOC-LIFE-01` | Temporary tags committed | `// TODO: fix this later` |
| `DOC-LIFE-02` | Review-only marker left in code | `// REVIEW: revisit this` |
| `DOC-LIFE-03` | Persistent tags used inconsistently | `// NOTE NOTE NOTE` |
| `DOC-LIFE-04` | Comment drifted from implementation | `// returns age` on a function that returns `user.name`; `/** returns user count */ function getActiveUsers(): User[]` |
