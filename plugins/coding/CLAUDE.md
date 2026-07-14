If you intend to write, modify, or review code, you MUST first read `references/CODING.md` (in this plugin directory) for the full coding workflow, standards routing, and orchestration rules.

## Pull Requests

Creating or updating a pull request MUST go through the `write-pr` and `push-pr` skills, not a hand-rolled `git`/`gh` sequence. `write-pr` composes the conventional-commit title and unified body from the commit; `push-pr` publishes it and drives CI to green. This applies even when the request looks like a small, one-off PR.

`push-pr` requires a jj-colocated repository and never substitutes plain `git push` for `jj git push` — that is its contract, not a detail this mandate may override. A git-only repository is therefore not exempt from this mandate; it is out of `push-pr`'s supported shape and must be brought into it. Attempt colocation with `jj git init` (non-destructive — it layers jj metadata onto the existing git history and objects; confirm with the user before running it on a repo they haven't already set up with jj), then verify it actually took effect with a functional check, not a directory-existence check: a `.jj` and a `.git` directory can both be present without being colocated (e.g. a `.jj` created independently of an unrelated `.git`), so `.jj`/`.git`/`jj st` presence alone proves nothing. Instead confirm `git rev-parse HEAD` equals `jj log -r @- --no-graph -T 'commit_id'` — only a match proves jj and git share the same backing repository; treat any mismatch, or a failing `git rev-parse HEAD`, as colocation having failed. Only when colocation genuinely fails or is declined, publish directly with `gh pr create`/`gh pr edit` using `write-pr`'s title/body verbatim and confirm CI state (or its documented absence) before reporting success — and record this explicitly as a one-off exception to `push-pr`, never as an equivalent path through it.

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
