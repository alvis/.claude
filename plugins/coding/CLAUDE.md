If you intend to write, modify, or review code, you MUST first read `references/CODING.md` (in this plugin directory) for the full coding workflow, standards routing, and orchestration rules.

## Pull Requests

Creating or updating a pull request MUST go through the `write-pr` and `push-pr` skills, not a hand-rolled `git`/`gh` sequence. `write-pr` composes the conventional-commit title and unified body from the commit; `push-pr` publishes it and drives CI to green. This applies even when the request looks like a small, one-off PR.

In a git-only repository (no `jj` colocation), `push-pr`'s jj-specific bookmark and worktree mechanics don't apply — that is not an exemption from this mandate. The compliant path is: still resolve the title/body from `write-pr`'s output verbatim, still publish and update via `gh pr create`/`gh pr edit` (using plain `git push` in place of `jj git push`), and still confirm CI state before reporting success — treating a repository with no discoverable checks as trivially green rather than skipping verification.

## Coding specialist routing

| Tasks | Route to |
| --- | --- |
| Bootstrap and scaffold a new project | `ada-bishop-initializer` |
| Author tests via TDD | `ava-thompson-testing-evangelist` |
| Automate CI/CD and infrastructure | `felix-anderson-devops` |
| Validate an exploit with an adversarial PoC | `kai-raven-adversarial-redteam` |
| Review changed code for quality | `marcus-williams-code-quality` |
| Debug hard bugs, optimize performance, or crack algorithms | `maya-rodriguez-principal` |
| Review auth, data, or access changes for security | `nina-petrov-security-champion` |
| Run a lint, type, and test sweep and summarize it | `tess-park-test-runner` |
