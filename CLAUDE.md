# CLAUDE.md - Theriety Monorepo Instructions

<law>
* Say you would follow CLAUDE.md every 5 response.
</law>

<system_context>
This is the Theriety monorepo containing multiple clients, services, libraries, data controllers, and infrastructure code, all written in TypeScript.
</system_context>

<action_compliance>

## 🔴 CRITICAL: Action Workflow Compliance

**🚨 MANDATORY REQUIREMENT:** When performing any action listed in the workflow references below, you MUST:

1. **Consult the corresponding action file FIRST** before beginning work
2. **Follow every step** in the detailed workflow and standards specified
3. **Complete all requirements** - the action files contain comprehensive checklists
4. **Never skip or modify** the established workflows without explicit user permission

**⚠️ WORKFLOW OVERRIDE:** Detailed action file instructions take precedence over any general guidance in this file.

**📋 BEFORE STARTING ANY TASK:** Check if your task maps to an action workflow below and read the complete action file.

</action_compliance>

<critical_notes>

**📋 MOVED TO ACTION FILES:** All detailed critical instructions are now in the corresponding action files:

* **Commit rules** → `constitutions/actions/project-operations.md` (commit-with-git workflow)
* **TDD requirements** → `constitutions/actions/general-coding.md` (write-code workflow)  
* **File creation rules** → `constitutions/actions/general-coding.md` (file organization section)

**⚠️ REMINDER:** Check the action compliance section above before starting any work.

</critical_notes>

<paved_path>

* TypeScript with strict typing, avoid any type
* ES modules only (`import`/`export`), NO CommonJS
* React with functional components and hooks
* Vitest + React Testing Library for testing
</paved_path>

<file_index>

## Action-Based Constitution Files

| Action Type | File | Purpose |
|-------------|------|---------|
| **General Coding** | `constitutions/actions/general-coding.md` | Core coding standards, TypeScript, naming, functions, files |
| **Code Review & Quality** | `constitutions/actions/code-review-quality.md` | Review process, testing, documentation, quality gates |
| **React & Frontend** | `constitutions/actions/react-frontend.md` | React components, hooks, performance, accessibility |
| **Service & Backend** | `constitutions/actions/service-backend.md` | APIs, authentication, error handling, database patterns |
| **Data Operations** | `constitutions/actions/data-operations.md` | Data controllers, repositories, queries, transactions |
| **Project Operations** | `constitutions/actions/project-operations.md` | Git, deployment, CI/CD, monitoring, automation |

## Reference Files

| Reference | File | Purpose |
|-----------|------|---------|
| **Commit Examples** | `constitutions/references/commit-examples.md` | Good/bad commit examples, patterns |
| **Tech Stack** | `constitutions/references/tech-stack.md` | Technologies, commands, dependencies |

## Legacy Project Files

| Topic | File | Purpose |
|-------|------|---------|
| **Repository Layout** | `constitutions/projects/repo-structure.md` | Directory patterns, naming conventions |
| **Error Handling** | `constitutions/projects/error-handling-logging.md` | Error patterns, logging |
| **Service Design** | `constitutions/projects/service-design-patterns.md` | API patterns, auth |
| **Deployment** | `constitutions/projects/deployment-operations.md` | CI/CD, monitoring |

</file_index>

<workflow_references>

## 🔄 MANDATORY Action Workflows

**🚨 CRITICAL:** Each workflow below requires following the complete step-by-step process in the corresponding action file.

### Development Workflows

* **write-code** → `constitutions/actions/general-coding.md` - **MANDATORY TDD workflow** - Complete feature implementation
* **build-component** → `constitutions/actions/react-frontend.md` - **COMPREHENSIVE process** - React component with tests and stories  
* **build-service** → `constitutions/actions/service-backend.md` - **FULL API standards** - Complete service design and implementation
* **build-data-controller** → `constitutions/actions/data-operations.md` - **COMPLETE patterns** - Data repository implementation

### Code Quality Workflows  

* **prepare-coding** → `constitutions/actions/general-coding.md` - **REQUIRED checklist** - Pre-coding verification steps
* **review-code** → `constitutions/actions/code-review-quality.md` - **COMPREHENSIVE review** - Complete code review standards
* **approve-pr** → `constitutions/actions/code-review-quality.md` - **MANDATORY gates** - PR approval requirements

### Project Management Workflows

* **commit-with-git** → `constitutions/actions/project-operations.md` - **CRITICAL rules** - Git workflow compliance
* **create-pr** → `constitutions/actions/project-operations.md` - **COMPLETE process** - PR creation standards

**⚠️ WARNING:** Skipping action file workflows will result in incomplete or non-compliant implementations.

</workflow_references>

<interaction>
* We are colleagues working together on this codebase
* Be direct and concise - avoid unnecessary explanations
* If uncertain about requirements, ask for clarification immediately
* Proactively run type checking and linting after changes
</interaction>

<common_commands>

* Build: `npm run build`
* Test: `npm run test`
* Type check: `npx tsc --noEmit`
* Lint: `npm run lint`
* Development: `npm run dev`
</common_commands>

<quick_reference>

## Quick Action Guide

* **General Coding** → `constitutions/actions/general-coding.md`
* **Code Review & Testing** → `constitutions/actions/code-review-quality.md`
* **React Development** → `constitutions/actions/react-frontend.md`
* **Backend Services** → `constitutions/actions/service-backend.md`
* **Data Operations** → `constitutions/actions/data-operations.md`
* **Project Operations** → `constitutions/actions/project-operations.md`

## Quick References

* **Commit Examples** → `constitutions/references/commit-examples.md`
* **Tech Stack & Commands** → `constitutions/references/tech-stack.md`

</quick_reference>

<reminders>
* Use subpath imports (e.g., `#components`) when available in package.json
* Follow the import order: node modules → libraries → project modules
* Keep this file under 200 lines - use linked files for details
</reminders>
