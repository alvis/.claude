# Instructions for AI Agents

This monorepo powers multiple products at Theriety. It contains multiple shared clients, services, libraries, data controllers, and infrastructure code etc intended for reuse across multiple products, primarily written in TypeScript.

## Navigation Guide

**If a conflict exists, follow the _more‑specific_ file named in the index below**

| Topic                        | File                             | Contents                                                   |
| ---------------------------- | -------------------------------- | ---------------------------------------------------------- |
| **Repository Layout**        | `01-repo-structure.md`           | Directory structure, project layout patterns               |
| **Tech Stack & Commands**    | `02-tech-stack.md`               | Technologies, build/test/lint commands, package management |
| **Testing**                  | `03-testing.md`                  | Testing patterns, coverage goals, BDD, coverage workflow   |
| **Version Control**          | `04-commit-pr-process.md`        | Commit messages, branch naming, PR structure               |
| **Code Style**               | `05-code-style-conventions.md`   | TypeScript style, imports, naming conventions              |
| **React Conventions**        | `06-react-conventions.md`        | React components, hooks, performance, testing              |
| **Documentation**            | `07-documentation-guidelines.md` | JSDoc, comments, interface docs, README requirements       |
| **Code Review**              | `08-code-review.md`              | Review tone, checklist, feedback patterns                  |
| **Best Practices**           | `09-development-conventions.md`  | DRY, pure functions, patterns, security, pre-checks       |
| **Error Handling & Logging** | `10-error-handling-logging.md`   | Error patterns, logging guidelines, monitoring             |
| **Service Design**           | `11-service-design-patterns.md`  | Service patterns, authentication                           |
| **Performance**              | `12-performance-optimization.md` | Frontend/backend optimization, caching, monitoring         |
| **Deployment & Operations**  | `13-deployment-operations.md`    | CI/CD, infrastructure, monitoring, incident response       |

## Quick Reference

### When writing code

1. Check `02-tech-stack.md` for available technologies and commands
2. Follow `05-code-style-conventions.md` for style and naming
3. Follow `06-react-conventions.md` for React components
4. Apply `09-development-conventions.md` for best practices
5. Document per `07-documentation-guidelines.md`
6. Handle errors per `10-error-handling-logging.md`

### When building APIs

1. Follow patterns in `11-service-design-patterns.md`
2. Implement error handling from `10-error-handling-logging.md`
3. Apply security from `09-development-conventions.md`

### When optimizing

1. Follow `12-performance-optimization.md` for performance
2. Monitor per `10-error-handling-logging.md` and `13-deployment-operations.md`

### When testing

1. Follow patterns in `03-testing.md`
2. Run commands from `02-tech-stack.md`
3. Fix coverage issues using workflow in `03-testing.md`

### When deploying

1. Follow `13-deployment-operations.md` for CI/CD
2. Complete checks from `09-development-conventions.md`

### When committing

1. Follow `04-commit-pr-process.md` for messages and PRs
2. Complete checks from `09-development-conventions.md`

--- END ---
