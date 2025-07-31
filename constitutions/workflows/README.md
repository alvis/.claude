# Workflows Directory

*Step-by-step processes for common development tasks*

This directory contains executable workflows organized by role and responsibility. Each workflow provides detailed steps to complete specific tasks.

## Quick Access by Role

### 👨‍💻 **Frontend Engineers**
- **[Build React Component](./frontend/build-component.md)** - Complete component development with tests and stories
- **[Review Code](./quality/review-code.md)** - Code review process and standards
- **[Approve PR](./quality/approve-pr.md)** - Final quality gates before merge

### 🔧 **Backend Engineers**  
- **[Build Data Controller](./backend/build-data-controller.md)** - Repository pattern with caching and transactions
- **[Verify Auth Scope](./backend/verify-auth-scope.md)** - JWT verification and role-based authorization
- **[Review Code](./quality/review-code.md)** - Code review process and standards
- **[Approve PR](./quality/approve-pr.md)** - Final quality gates before merge

### 📋 **All Engineers**
- **[Write Code (TDD)](./coding/write-code-tdd.md)** - Test-driven development workflow
- **[Prepare for Coding](./coding/prepare-coding.md)** - Pre-coding verification steps
- **[Commit with Git](./project/commit-with-git.md)** - TDD-compliant git workflow
- **[Review Code](./quality/review-code.md)** - Code review process and standards
- **[Approve PR](./quality/approve-pr.md)** - Final quality gates before merge

## Workflow Categories

### 🎨 Frontend Development
| Workflow | Purpose | When to Use |
|----------|---------|-------------|
| [Build Component](./frontend/build-component.md) | Create React components with full testing and documentation | Building new UI components |

### ⚙️ Backend Development  
| Workflow | Purpose | When to Use |
|----------|---------|-------------|
| [Build Data Controller](./backend/build-data-controller.md) | Implement data access with repository pattern | Creating data access layers |
| [Verify Auth Scope](./backend/verify-auth-scope.md) | Add authentication and authorization | Securing API endpoints |

### 💻 General Coding
| Workflow | Purpose | When to Use |
|----------|---------|-------------|
| [Write Code (TDD)](./coding/write-code-tdd.md) | Test-driven development process | All feature development |
| [Prepare for Coding](./coding/prepare-coding.md) | Environment and context setup | Before starting any coding task |

### 🔍 Quality Assurance
| Workflow | Purpose | When to Use |
|----------|---------|-------------|
| [Review Code](./quality/review-code.md) | Comprehensive code review process | Reviewing pull requests |
| [Approve PR](./quality/approve-pr.md) | Final approval quality gates | Before merging code |

### 📦 Project Operations
| Workflow | Purpose | When to Use |
|----------|---------|-------------|
| [Commit with Git](./project/commit-with-git.md) | Quality-gated git workflow | Committing code changes |

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

## Workflow Principles

### ✅ **Completeness**
Each workflow includes all necessary steps from start to finish.

### 🔄 **Repeatability** 
Workflows produce consistent results when followed by different people.

### 🎯 **Focus**
Each workflow has a single, clear purpose and outcome.

### 📝 **Actionable**
Every step is concrete and executable.

### 🔗 **Connected**
Workflows reference related standards and other workflows as needed.

## Need Help?

- **Can't find the right workflow?** Check the [Standards](../standards/) directory for technical requirements
- **Looking for examples?** See the [Patterns](../patterns/) directory for templates and examples
- **Need quick reference?** Check the [References](../references/) directory for lookup information
- **Workflow unclear?** Refer to linked standards documents for detailed technical guidance

## Contributing to Workflows

When updating workflows:

1. **Keep them focused** - One clear purpose per workflow
2. **Make steps actionable** - Each step should be concrete and executable  
3. **Include quality gates** - Define what success looks like
4. **Link to standards** - Reference detailed technical requirements
5. **Test the workflow** - Ensure it produces the expected outcome

Remember: Workflows are the "HOW" - they tell you the process to follow. Standards are the "WHAT" - they define the technical requirements and rules.