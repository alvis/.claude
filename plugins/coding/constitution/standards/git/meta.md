# Git Workflow Standards

_Standards for commit messages, branch naming, and pull requests using Conventional Commits._

## Dependent Standards

You MUST also read the following standards together with this file:

- Naming Standards (standard:naming) - scope naming aligns with package naming conventions

## What's Stricter Here

This standard enforces requirements beyond typical Conventional Commits practices:

| Standard Practice                          | Our Stricter Requirement                                              |
|--------------------------------------------|-----------------------------------------------------------------------|
| Freeform scope naming                      | **Scope must be short package name — drop catalog prefix**            |
| Mixed footer keywords (`Fixes`, `Closes`)  | **Footer uses `Closes` only**                                         |
| Unlimited scopes per commit                | **Maximum 2 comma-separated scopes**                                  |
| PR created when ready                      | **Always start with a draft PR**                                      |

## Exception Policy

Allowed exceptions only when:

- False positive
- No viable workaround exists now

Required exception note fields:

- `rule_id`
- `reason` (`false_positive` or `no_workaround`)
- `evidence`
- `temporary_mitigation`
- `follow_up_action`

If exception note is missing, submission is rejected.

## Rule Groups

- `GIT-MSG-*`: Commit message format, type, scope, title length, body, and footer rules.
- `GIT-BRN-*`: Branch naming format and scope convention rules.
- `GIT-PR-*`: Pull request format, description structure, and review rules.
