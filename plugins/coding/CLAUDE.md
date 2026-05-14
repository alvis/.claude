## File Discovery

- At the beginning of each session, greet the user with summary of the project context, including handover and design documents, as well as all relevant skills and standards files that may apply to the project

## Delegation Rule

**When delegating tasks to subagents, you MUST pass the full file paths of relevant skill and standard files to the subagent.**

Each skill documents its own applicable standards internally. Route actions to the appropriate skill:

| Action | Route to |
|--------|----------|
| Writing new code | `/coding:write-code` or `/coding:draft-code` |
| Setting up project | `/coding:setup-project` |
| Completing TODOs | `/coding:complete-code` |
| Fixing issues | `/coding:fix` |
| Reviewing code | `/coding:review` |
| Linting code | `/coding:lint` |
| Refactoring | `/coding:refactor` |
| Committing | `/coding:commit` |
| Creating tests | `/coding:complete-test` |
| Handing over work | `/coding:handover` |
| Resuming work | `/coding:takeover` |
| Finding dead code | `/coding:find-unused` |
| Modernizing syntax | `/coding:modernize` |

## Change Tracking with `jj`

1. **`jj` is the primary change-tracking tool** — every op snapshots the working copy, so a dirty HEAD is never a blocker. Do NOT create a `git worktree` to "isolate" a task; coding skills work in place.

2. **Work in place on a dirty HEAD** — new changes layer onto existing uncommitted work; no isolation strategy to decide.

3. **Atomic commits go through `coding:commit`** — it commits via `git` (expected in a jj-colocated repo; `jj` still tracks every change). Don't hand-run `git commit` / `jj describe`.

4. **All jj organization goes through `coding:stack-code`** — bookmarks, `jj split`, `jj rebase`, `jj workspace`, `gh pr create` are owned exclusively by `/coding:stack-code` (per `GIT-PR-STACK-*`). Never run `jj split` / `jj bookmark set` directly.

5. **Git-worktree guard** — a `git worktree` is NOT a `jj workspace`. If a coding task was carried out inside a linked `git worktree`, you MUST `AskUserQuestion` whether the work should be moved back onto HEAD.

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
