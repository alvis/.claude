# Workflows Directory

**Purpose**: Comprehensive collection of step-by-step processes for common development tasks, organized by role and responsibility. Each workflow provides detailed orchestration instructions following Claude's delegation model with 5-phase execution patterns.

**When to use**: Reference this directory when you need to execute specific development tasks, understand workflow dependencies, or find the appropriate process for your current role and objectives.

**How workflows operate**: All workflows follow Claude's orchestration model where Claude acts as project director, delegating tasks to specialized subagents and making decisions based on their reports. Each workflow step follows a 5-phase pattern: Planning → Execution → Review → Verification → Decision.

## Quick Access by Role

### 👨‍💻 **Frontend Engineers**

- **[Build React Component](@./frontend/build-component.md)** - Complete component development with tests and stories
- **[Review Code](@./quality/review-code.md)** - Code review process and standards
- **[Approve PR](@./quality/approve-pr.md)** - Final quality gates before merge

### 🔧 **Backend Engineers**

- **[Build Data Controller](@./backend/build-data-controller.md)** - Repository pattern with caching and transactions
- **[Create Service Operation Manifest](@./backend/create-service-operation-manifest.md)** - Define and implement new service operations with manifest schemas and type-safe implementations
- **[Implement Data Operation](@./backend/implement-data-operation.md)** - Create database operations from Notion specifications
- **[Verify Auth Scope](@./backend/verify-auth-scope.md)** - JWT verification and role-based authorization
- **[Review Code](@./quality/review-code.md)** - Code review process and standards
- **[Approve PR](@./quality/approve-pr.md)** - Final quality gates before merge

### 📋 **All Engineers**

- **[Write Code (TDD)](@./coding/write-code.md)** - Test-driven development workflow
- **[Prepare for Coding](@./coding/prepare-coding.md)** - Pre-coding verification steps
- **[Create Command](@./project/create-command.md)** - Generate new slash command files from templates
- **[Create Screen Design](@./project/create-screen-design.md)** - Create comprehensive screen design documentation on Notion with responsive variations
- **[Update Command](@./project/update-command.md)** - Update command files to align with template
- **[Review Code](@./quality/review-code.md)** - Code review process and standards
- **[Approve PR](@./quality/approve-pr.md)** - Final quality gates before merge

## Workflow Categories

### 🎨 Frontend Development

| Workflow                                         | Purpose                                                     | When to Use                |
| ------------------------------------------------ | ----------------------------------------------------------- | -------------------------- |
| [Build Component](@./frontend/build-component.md) | Create React components with full testing and documentation | Building new UI components |

### ⚙️ Backend Development

| Workflow                                                                                | Purpose                                                                   | When to Use                        |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------- |
| [Build Data Controller](@./backend/build-data-controller.md)                             | Implement data access with repository pattern                             | Creating data access layers        |
| [Create Service Operation Manifest](@./backend/create-service-operation-manifest.md)     | Define and implement new service operations with manifest schemas and type-safe implementations | Creating new service operations    |
| [Implement Data Operation](@./backend/implement-data-operation.md)                       | Implement database operations based on Notion specifications               | Creating data operations (get/set/list/drop) |
| [Verify Auth Scope](@./backend/verify-auth-scope.md)                                     | Add authentication and authorization                                       | Securing API endpoints             |

### 💻 General Coding

| Workflow                                         | Purpose                         | When to Use                     |
| ------------------------------------------------ | ------------------------------- | ------------------------------- |
| [Write Code (TDD)](@./coding/write-code.md)   | Test-driven development process | All feature development         |
| [Prepare for Coding](@./coding/prepare-coding.md) | Environment and context setup   | Before starting any coding task |

### 🔍 Quality Assurance

| Workflow                                | Purpose                           | When to Use             |
| --------------------------------------- | --------------------------------- | ----------------------- |
| [Linting](@./quality/linting.md)       | Apply documentation, TypeScript, and error-handling standards | Before committing major changes |
| [Review Code](@./quality/review-code.md) | Comprehensive code review process | Reviewing pull requests |
| [Review Test](@./quality/review-test.md) | Optimize tests for coverage and maintainability | After test creation or when coverage drops |
| [Approve PR](@./quality/approve-pr.md)   | Final approval quality gates      | Before merging code     |

### 📦 Project Operations

| Workflow                                        | Purpose                    | When to Use             |
| ----------------------------------------------- | -------------------------- | ----------------------- |
| [Commit with Git](@./project/commit-with-git.md) | Quality-gated git workflow | Committing code changes |
| [Create Command](@./project/create-command.md) | Generate new slash command files from templates | Creating new CLI commands |
| [Create Screen Design](@./project/create-screen-design.md) | Create comprehensive screen design documentation on Notion with responsive variations | Documenting UI/UX screen designs |
| [Ensure Project](@./project/ensure-project.md) | Validate and bootstrap project structure | Setting up new projects or validating existing ones |
| [Update Agent](@./project/update-agent.md) | Update agent files to align with latest template | Maintaining and updating agent definitions |
| [Update Command](@./project/update-command.md) | Update command files to align with template | When commands need template alignment |

### 🔄 Theriety Platform

| Workflow                                                            | Purpose                                                                   | When to Use                                                |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------- |
| [Declare Service Operation](@./theriety/declare-service-operation.md) | Create service operation specifications in Notion                        | Defining new service operations                           |
| [Implement Data Operation](@./theriety/implement-data-operation.md)   | Implement database operations from Notion specifications                  | Creating data operations                                  |
| [Implement Data Schema](@./theriety/implement-data-schema.md)        | Implement data schemas from specifications                                | Creating data models                                      |
| [Review Service Operation](@./theriety/review-service-operation.md)   | Validate service operations in Notion for completeness and standards compliance | Reviewing existing service operations for quality assurance |
| [Update Screen Design](@./theriety/update-screen-design.md)         | Update design documentations for interactive screens on Notion to conform to latest template | Updating existing screen designs to current standards |

## How to Use Workflows

### 1. **Select Your Role**

Choose the section that matches your primary role or the task you're performing.

### 2. **Find the Right Workflow**

Look for the workflow that matches your current task or goal.

### 3. **Follow the Steps**

Each workflow provides:

- **Purpose** - What the workflow accomplishes
- **When to use** - Situational guidance
- **Prerequisites** - What you need before starting
- **Detailed steps** - Step-by-step instructions
- **Quality gates** - Required checks and validations
- **Standards references** - Links to related standards

### 4. **Reference Standards**

Workflows link to relevant standards documents for detailed technical requirements.

## Workflow Architecture Principles

### Claude Orchestration Model

- **Strategic Delegation**: Claude breaks complex tasks into parallel subtasks assigned to specialized subagents
- **Quality Oversight**: Claude reviews all subagent outputs without executing tasks directly
- **Decision Authority**: Claude makes go/no-go decisions based on subagent reports and verification results
- **Standards Enforcement**: All workflows require adherence to comprehensive coding and quality standards

### 5-Phase Execution Pattern

Each workflow step follows this consistent pattern:

1. **Planning** - Claude analyzes requirements and creates task assignments
2. **Execution** - Specialized subagents perform assigned work in parallel when possible
3. **Review** - Claude collects and analyzes execution reports
4. **Verification** - Independent verification subagents check quality when needed
5. **Decision** - Claude decides to proceed, retry, or rollback based on criteria

### Workflow Quality Standards

- **Completeness**: Each workflow includes all necessary steps from start to finish
- **Repeatability**: Workflows produce consistent results when followed by different teams
- **Parallel Efficiency**: Independent tasks execute simultaneously to maximize productivity
- **Quality Gates**: Comprehensive verification ensures standards compliance before proceeding

## Need Help?

- **Can't find the right workflow?** Check the [Standards](@../standards/) directory for technical requirements
- **Looking for examples?** See the [Patterns](@../patterns/) directory for templates and examples
- **Need quick reference?** Check the [References](@../references/) directory for lookup information
- **Workflow unclear?** Refer to linked standards documents for detailed technical guidance

## Contributing to Workflows

When updating workflows:

1. **Keep them focused** - One clear purpose per workflow
2. **Make steps actionable** - Each step should be concrete and executable
3. **Include quality gates** - Define what success looks like
4. **Link to standards** - Reference detailed technical requirements
5. **Test the workflow** - Ensure it produces the expected outcome

Remember: Workflows are the "HOW" - they tell you the process to follow. Standards are the "WHAT" - they define the technical requirements and rules.
