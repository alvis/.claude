If you intend to write, modify, or review code, you MUST first read `references/CODING.md` (in this plugin directory) for the full coding workflow, standards routing, and orchestration rules.

## Pull Requests

Creating or updating a pull request MUST go through the `write-pr` and `push-pr` skills, not a hand-rolled `git`/`gh` sequence. `write-pr` composes the conventional-commit title and unified body from the commit; `push-pr` publishes it and drives CI to green. This applies even when the request looks like a small, one-off PR.

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
