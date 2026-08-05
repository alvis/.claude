---
name: pr
description: 'Use for GitHub pull-request workflows when the user asks to draft PR text, publish a branch, create, update, discover, check out, review, or merge a PR or linear stack. Trigger before running gh pr, inspecting GitHub stacks, or publishing PR-related changes.'
model: opus
argument-hint: "<author|create|update|review|stack|merge> [arguments]"
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
/coding:pr stack list
/coding:pr stack checkout <stack-number-or-pr-number-or-pr-url-or-local-branch>
/coding:pr merge <pr numbers...> [--method=rebase|squash|merge] [--force]
```

When the request omits a subcommand, names no clear action, or could select more
than one action, print the complete usage block above and stop. Do not infer a
remote mutation.

## Routing

For every request to create, inspect, update, restructure, publish, check out,
sync, navigate, unstack, or merge a GitHub PR stack, load
[references/github-stacks.md](references/github-stacks.md) before selecting an
operator. This applies even when the request arrives through `create`, `update`,
or `merge`, rather than the explicit `stack` route.

- `author` writes deterministic PR title and body text without publication.
  Follow only [Author the PR text](references/create-update.md#author-the-pr-text);
  `--base` selects the intended PR base instead of the first-parent default.
- `create` opens new draft PRs for one saved change or a conventional linear
  stack. Load and follow
  [references/create-update.md](references/create-update.md) with
  `ACTION=create`, and always load
  [references/stacked-prs.md](references/stacked-prs.md).
- `update` republishes existing PR heads for a conventional linear stack,
  refreshes their title, body, and bases, and drives CI to green. Load and follow
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
- `stack list` lists the current repository's GitHub PR stacks; `stack checkout`
  checks out one explicitly selected stack and requires `gh stack`. Follow
  [references/github-stacks.md](references/github-stacks.md#list-or-check-out).
  Checkout may fetch and create local tracking branches, but this route does
  not own commits, history rewriting, pushes, or PR publication.
- `merge` validates and merges a conventional linear stack bottom-up. For a
  GitHub PR stack, use the GitHub operator map loaded above instead. Otherwise
  load and follow
  [references/stacked-prs.md](references/stacked-prs.md), then
  [references/merge.md](references/merge.md).

<IMPORTANT>
Execute exactly one subcommand per invocation. A workflow may instruct a later
`coding:pr` invocation, but it must name that subcommand explicitly.
</IMPORTANT>
