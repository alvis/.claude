## File Discovery

- At the beginning of each session, greet the user with summary of the project context, including handover and design documents, as well as all relevant workflows and standards files that may apply to the project

## Delegation Rule

**When delegating tasks to subagents, you MUST pass the full file paths of relevant workflow and standard files to the subagent.**

**When performing the following actions, you MUST pass all workflow and standard files as specified below:**

- **When Writing New Code**

  YOU MUST FOLLOW:
  **Workflow**: write-code
  **Standards**: documentation/write, observability/write, file-structure, function/write, universal/write, naming/write, testing/write, typescript/write

- **When Creating Tests**

  YOU MUST FOLLOW:
  **Workflow**: create-test
  **Standards**: documentation/write, universal/write, naming/write, testing/write, typescript/write

- **When Reviewing**

  YOU MUST FOLLOW:
  **Workflow**: review
  **Standards**: code-review, documentation/scan, environment-variables, observability/scan, function/scan, universal/scan, naming/scan, testing/scan, typescript/scan

- **When Fixing Tests**

  YOU MUST FOLLOW:
  **Workflow**: write-code (Steps 3-4 only)
  **Standards**: universal/scan, naming/scan, testing/scan, typescript/scan

  **NOTE**: The fix-test workflow has been merged into write-code. When fixing tests, execute Steps 3 and 4 of the write-code workflow.
  **NOTE**: When a specific rule violation is detected, load its fix guidance from `testing/rules/<rule-id>.md`.

- **When Linting Code**

  YOU MUST FOLLOW:
  **Workflow**: lint
  **Standards**: documentation/scan, observability/scan, function/scan, universal/scan, naming/scan, testing/scan, typescript/scan

- **When Setting Up Project**

  YOU MUST FOLLOW:
  **Workflow**: ensure-project
  **Standards**: file-structure, universal/write, typescript/write

- **When Committing Code**

  **Workflow**: None (use `/coding:commit` command)
  **Standards**: git

## Your Actions

<IMPORTANT>

- Prefer using **READ**, **WRITE**, **UPDATE**, **LS**, **GREP** as your primary editing tools instead of using **BASH**
- **Prepared Scripts**: **[IMPORTANT]** You MUST always use scripts defined in the project config (e.g. `package.json`) over running tools directly via bash. This applies to ALL agents and subagents.
  - **DO**: `npm run lint -- <path>`, `npm run test -- <path>`, `npm run build`
  - **DON'T**: `npx eslint <path>`, `npx jest <path>`, `npx tsc`
  - Only fall back to direct tool invocation when no project script exists for the purpose
- **Project Overview**: **[IMPORTANT]** Before attempting writing or fixing any codes, you MUST gain understanding about the current implementation and any issues by any one of the following methods ordered by preferences (but you only need to run once)
  - `get_project_overview` mcp tool
  - `ide__getDiagnostics` mcp tool
  - running `npm run build`
  - running `npx tsc --noEmit`
- **Diagnostics**: You MUST run run `lsp_get_diagnostics` or `ide__getDiagnostics` mcp tools before and after code changes (you only can skip if `get_project_overview` has just run)
- **Complete Check**: **[IMPORTANT]**  After completing your coding or test writing task, you MUST run all of the following under the project root (not monorepo root) to make sure no issues are introduced by your changes
    1. `lsp_get_diagnostics` mcp tool
    2. running `npx tsc --noEmit`
    3. running `npm run lint`
- **Dependency Check**: **[IMPORTANT]**  After modifying any functions/classes that are publicly exported, look for all consumer projects in the monorepo and run the following in their project root
    1. running `npm run build`
- **Type Safety**: No `any` types allowed (& preferably no `unknown` unless absolute necessarily)
- **Test Coverage**: Maintain 100% coverage for all code
- **TDD**: Follow Red-Green-Refactor cycle for new features
- **Standards**: All code must follow TypeScript, naming, and documentation standards
- **Check Documentation**: Before using an external library, consult **context7**  to confirm the correct import or call signature from the documentation, and **grep** to search for real world github usage
- **Runtime Exploration**: When you need to understand the runtime behaviour of a library or API, write a test file (or add a test case to an existing spec) instead of running ad-hoc commands like `node -e "..."`, `npx ts-node -e "..."`, or equivalent. Test files are version-controlled, repeatable, and serve as living documentation.

</IMPORTANT>
