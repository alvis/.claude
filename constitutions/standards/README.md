# Standards Directory

_Technical requirements and rules for code quality and consistency_

This directory contains detailed technical standards organized by technology and domain. Standards define WHAT the requirements are - the rules, patterns, and quality criteria that code must meet.

## Quick Access by Role

### 👨‍💻 **Frontend Engineers**

- **[React Components](@./frontend/react-components.md)** - Component structure, patterns, performance
- **[React Hooks](@./frontend/react-hooks.md)** - Custom hooks design and patterns
- **[Accessibility](@./frontend/accessibility.md)** - WCAG compliance and inclusive design
- **[TypeScript](@./code/typescript.md)** - Type safety, imports, language usage
- **[Testing](@./quality/testing.md)** - TDD principles and testing patterns

### 🔧 **Backend Engineers**

- **[Data Operations](@./backend/data-operations.md)** - Repository patterns and query standards
- **[TypeScript](@./code/typescript.md)** - Type safety, imports, language usage
- **[Testing](@./quality/testing.md)** - TDD principles and testing patterns

### 📋 **All Engineers**

- **[TypeScript](@./code/typescript.md)** - Core language standards
- **[Naming Conventions](@./code/naming.md)** - Variables, functions, files
- **[Functions](@./code/functions.md)** - Design, parameters, interfaces
- **[Documentation](@./code/documentation.md)** - JSDoc, comments, inline docs
- **[Testing](@./quality/testing.md)** - Comprehensive testing standards
- **[Git Workflow](@./project/git-workflow.md)** - Commit messages, branching

## Standards Categories

### 💻 Code Standards

| Standard                                 | Purpose                                    | Scope                              |
| ---------------------------------------- | ------------------------------------------ | ---------------------------------- |
| [TypeScript](@./code/typescript.md)       | Type safety, imports, strict configuration | All TypeScript code                |
| [Naming Conventions](@./code/naming.md)   | Consistent naming across codebase          | Variables, functions, files, types |
| [Functions](@./code/functions.md)         | Function design and parameter patterns     | All function implementations       |
| [Documentation](@./code/documentation.md) | JSDoc, comments, and inline documentation  | Code documentation                 |

### 🎨 Frontend Standards

| Standard                                           | Purpose                              | Scope              |
| -------------------------------------------------- | ------------------------------------ | ------------------ |
| [React Components](@./frontend/react-components.md) | Component structure and performance  | React components   |
| [React Hooks](@./frontend/react-hooks.md)           | Custom hooks design patterns         | React custom hooks |
| [Accessibility](@./frontend/accessibility.md)       | WCAG compliance and inclusive design | All UI components  |

### ⚙️ Backend Standards

| Standard                                        | Purpose                                     | Scope                  |
| ----------------------------------------------- | ------------------------------------------- | ---------------------- |
| [Data Operations](@./backend/data-operations.md) | Repository patterns and database operations | Data access layers     |

### 🔍 Quality Standards

| Standard                        | Purpose                             | Scope         |
| ------------------------------- | ----------------------------------- | ------------- |
| [Testing](@./quality/testing.md) | TDD principles and testing patterns | All test code |

### 📦 Project Standards

| Standard                                  | Purpose                               | Scope           |
| ----------------------------------------- | ------------------------------------- | --------------- |
| [Git Workflow](@./project/git-workflow.md) | Commit messages and branch management | Version control |

## How to Use Standards

### 1. **Reference During Development**

Standards provide the technical requirements you must follow while coding.

### 2. **Consult During Review**

Use standards as checklists when reviewing code or approving PRs.

### 3. **Learn Patterns**

Standards include examples of correct and incorrect patterns.

### 4. **Understand Why**

Standards explain the reasoning behind requirements, not just the rules.

## Standard Structure

Each standard document includes:

### 📋 **Requirements**

- Clear, enforceable rules
- Must-follow vs. should-follow guidance
- Configuration requirements

### ✅ **Examples**

- Good and bad code examples
- Before/after comparisons
- Real-world usage patterns

### 🚫 **Anti-Patterns**

- Common mistakes to avoid
- Problematic patterns with explanations
- Alternative approaches

### 🔗 **Integration**

- How the standard connects to others
- Dependencies and relationships
- Cross-references

## Standards Hierarchy

### **Core Standards** (Apply to All Code)

1. [TypeScript](@./code/typescript.md) - Language usage and type safety
2. [Naming Conventions](@./code/naming.md) - Consistent naming
3. [Functions](@./code/functions.md) - Function design patterns
4. [Documentation](@./code/documentation.md) - Code documentation
5. [Testing](@./quality/testing.md) - Testing principles

### **Domain Standards** (Apply to Specific Areas)

- **Frontend**: React components, hooks, accessibility
- **Backend**: API design, data operations
- **Project**: Git workflow, deployment

### **Integration Standards** (Cross-Domain)

Standards that apply across multiple domains and must be consistent throughout the codebase.

## Compliance Levels

### 🔴 **MUST** - Critical Requirements

- Violation blocks code approval
- Automated enforcement where possible
- Security and functionality requirements

### 🟡 **SHOULD** - Important Guidelines

- Strong recommendation, exceptions need justification
- Code quality and maintainability
- Performance and best practices

### 🟢 **MAY** - Optional Suggestions

- Helpful patterns and optimizations
- Style preferences
- Enhancement opportunities

## Quality Gates

Standards define quality gates that must pass:

### **Automated Checks**

- TypeScript compilation without errors
- Linting rules enforcement
- Test coverage thresholds
- Import order validation

### **Manual Review**

- Code review checklist items
- Architecture pattern compliance
- Documentation completeness
- Testing adequacy

## Need Help?

- **Looking for step-by-step guidance?** Check the [Workflows](@../workflows/) directory
- **Need examples or templates?** See the [Patterns](@../patterns/) directory
- **Want quick reference info?** Check the [References](@../references/) directory
- **Standard unclear?** Look for related workflow that shows how to apply it

## Contributing to Standards

When updating standards:

1. **Be specific** - Provide concrete, testable requirements
2. **Include examples** - Show both good and bad patterns
3. **Explain rationale** - Help people understand why the rule exists
4. **Consider automation** - Can this be enforced by tooling?
5. **Cross-reference** - Link to related standards and workflows

Remember: Standards are the "WHAT" - they define the technical requirements and quality criteria. Workflows are the "HOW" - they show you the process to follow these standards.
