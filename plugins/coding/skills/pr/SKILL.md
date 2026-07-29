---
name: pr
description: 'Author, create, update, review, or merge GitHub pull requests, including linear stacks. Use for deterministic PR text, publication and CI convergence, external review comments and verdicts, or bottom-up stack merges; the first argument selects the subcommand.'
model: opus
allowed-tools: Bash(git:*), Bash(jj:*), Bash(gh:*), Bash(sleep:*), Bash(jq:*), Bash(mktemp:*), Bash(rm:*), Bash(command:*), Bash(bash ${CLAUDE_PLUGIN_ROOT}/skills/pr/scripts/*), Read, Grep, Glob, Agent, Skill, AskUserQuestion, CronCreate, CronDelete
argument-hint: "<author|create|update|review|merge> [arguments]"
---

# Pull Requests

Route every remote pull-request operation through one explicit subcommand. Local
history mutation remains owned by `coding:commit`; local pre-commit review remains
owned by `coding:review-code`.

## Usage

```text
/coding:pr author [<commit-ref>] [--base <ref>]
/coding:pr create [<commit-ref>] [--branch-prefix <name>] [--skip-local-test] [--dry-run]
/coding:pr update [<pr-number-or-url> | <commit-ref>] [--branch-prefix <name>] [--skip-local-test] [--dry-run]
/coding:pr review [<pr-number-or-url> | <source-tree-path>] [--repo <owner/name>] [--area=<list>] [--dry-run]
/coding:pr merge <pr numbers...> [--method=rebase|squash|merge] [--force]
```

When the request omits a subcommand, names no clear action, or could select more
than one action, print the complete usage block above and stop. Do not infer a
remote mutation.

## Routing

- `author` writes deterministic PR title and body text without publication.
  Follow only [Author the PR text](references/create-update.md#author-the-pr-text);
  `--base` selects the intended PR base instead of the first-parent default.
- `create` opens new draft PRs for one saved change or a linear stack. Load and
  follow [references/create-update.md](references/create-update.md) with
  `ACTION=create`, and always load
  [references/stacked-prs.md](references/stacked-prs.md).
- `update` republishes existing PR heads, refreshes their title, body, and bases,
  and drives CI to green. Load and follow
  [references/create-update.md](references/create-update.md) with
  `ACTION=update`, and always load
  [references/stacked-prs.md](references/stacked-prs.md).
- `review` publishes one external review per PR. As the context-owning caller,
  load [references/review-workflow.md](references/review-workflow.md), provision
  any owned tree, and retain its cleanup lease. Run the read-only steps in a
  fresh `code-quality-critic` subagent with no inherited implementation context,
  close the lease after any return or cancellation, and never delegate again
  from that dedicated reviewer.
- `merge` validates and merges a linear stack bottom-up. Load and follow
  [references/stacked-prs.md](references/stacked-prs.md), then
  [references/merge.md](references/merge.md).

<IMPORTANT>
Execute exactly one subcommand per invocation. A workflow may instruct a later
`coding:pr` invocation, but it must name that subcommand explicitly.
</IMPORTANT>
