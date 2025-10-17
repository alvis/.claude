**🚨 CRITICAL: Delegation Rule**

**When delegating tasks to subagents, you MUST pass the full file paths of relevant workflow and standard files to the subagent.**

**When performing the following actions, you MUST read all workflow and standard files as specified.**

- **When Writing New Code**

  YOU MUST FOLLOW:
  **Workflow**: write-code
  **Standards**: documentation, error-handling-logging, file-structure, functions, general-principles, naming, testing, typescript

- **When Creating Tests**

  YOU MUST FOLLOW:
  **Workflow**: create-test
  **Standards**: documentation, general-principles, naming, testing, typescript

- **When Reviewing Code**

  YOU MUST FOLLOW:
  **Workflow**: review-code
  **Standards**: code-review, documentation, environment-variables, error-handling-logging, functions, general-principles, naming, testing, typescript

- **When Reviewing Tests**

  YOU MUST FOLLOW:
  **Workflow**: review-test
  **Standards**: code-review, general-principles, testing, typescript

- **When Fixing Tests**

  YOU MUST FOLLOW:
  **Workflow**: fix-test
  **Standards**: general-principles, naming, testing, typescript

- **When Linting Code**

  YOU MUST FOLLOW:
  **Workflow**: lint
  **Standards**: documentation, error-handling-logging, functions, general-principles, naming, typescript

- **When Setting Up Project**

  YOU MUST FOLLOW:
  **Workflow**: ensure-project
  **Standards**: file-structure, general-principles, typescript

- **When Committing Code**

  **Workflow**: None (use `/coding:commit` command)
  **Standards**: git

<IMPORTANT>
**Universal Requirements**

These apply to ALL coding actions:

- **Prepared Scripts**: You MUST always use relevant defined package manager scripts instead of running tools directly in bash, unless none is defined for the purpose
- **Project Overview**: You MUST run `get_project_overview` mcp tool before planning or making any code change (but you only need to run once)
- **Diagnostics**: You MUST run run `lsp_get_diagnostics` or `ide__getDiagnostics` mcp tools before and after code changes (you only can skip if `get_project_overview` has just run)
- **Type Check**: Run `npx tsc --noEmit` after implementation to verify compilation
- **Type Safety**: No `any` types allowed (& preferably no `unknown` unless absolute necessarily)
- **Test Coverage**: Maintain 100% coverage for all code
- **TDD**: Follow Red-Green-Refactor cycle for new features
- **Standards**: All code must follow TypeScript, naming, and documentation standards

</IMPORTANT>
