---
name: pr
description: 'Use for GitHub pull-request workflows when the user asks to draft PR text, publish a branch, create or update a PR, monitor CI, review PR changes or comments, or merge a PR or linear stack. Trigger before running gh pr or publishing PR-related changes.'
model: opus
argument-hint: "<author|create|update|review|merge> [arguments]"
---

# Pull Requests

Before any script call, set `CODING_PR_SKILL_DIR` to the absolute directory
containing this loaded `SKILL.md`. This works in both harnesses; ordinary Codex
shell calls do not receive a plugin-root environment variable.

Route every remote pull-request operation through one explicit subcommand. Local
history mutation remains owned by `coding:commit`; local pre-commit review remains
owned by `coding:review-code`.

## Usage

```text
/coding:pr author [<commit-ref>] [--base <ref>]
/coding:pr create [<commit-ref>] [--branch-prefix <name>] [--skip-local-test] [--no-review] [--publish-only] [--dry-run]
/coding:pr update [<pr-number-or-url> | <commit-ref>] [--branch-prefix <name>] [--skip-local-test] [--no-review] [--publish-only] [--dry-run]
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
- `review` publishes one external review per PR, or one holistic review unit for
  a linear stack with findings attributed to its PR surfaces. As the
  context-owning caller,
  load [references/review-workflow.md](references/review-workflow.md), provision
  any owned tree, and retain its cleanup lease. Run the read-only steps in a
  fresh `code-quality-critic` subagent with no inherited implementation context,
  close the lease after any return or cancellation, and never delegate again
  from that dedicated reviewer. A fresh critic dispatched by
  [references/review-loop.md](references/review-loop.md) with an explicit
  preprovisioned stack capsule is already that dedicated reviewer: it runs the
  review phase directly instead of nesting another dispatch.
- `merge` validates and merges a linear stack bottom-up. Load and follow
  [references/stacked-prs.md](references/stacked-prs.md), then
  [references/merge.md](references/merge.md).

<IMPORTANT>
Execute exactly one subcommand per invocation. A workflow may instruct a later
`coding:pr` invocation, but it must name that subcommand explicitly.
</IMPORTANT>
