# Constitution Directory

_Complete development standards and workflows for the Theriety monorepo_

This directory contains the restructured development constitution, organized by role and responsibility for better discoverability and maintainability.

## 🎯 **Quick Start by Role**

### 👨‍💻 **Frontend Engineers**

**Essential workflows:**

- [Build Component](@./workflows/frontend/build-component.md) - React component development
- [Write Code (TDD)](@./workflows/coding/write-code.md) - Test-driven development
- [Review Code](@./workflows/quality/review-code.md) - Code review process

**Key standards:**

- [React Components](@./standards/frontend/react-components.md) - Component patterns and structure
- [Accessibility](@./standards/frontend/accessibility.md) - WCAG compliance
- [TypeScript](@./standards/code/typescript.md) - Language usage and imports

**Templates:**

- [Component Template](@./patterns/frontend/component-template.md) - Complete component boilerplate

### 🔧 **Backend Engineers**

**Essential workflows:**

- [Build Data Controller](@./workflows/backend/build-data-controller.md) - Repository pattern implementation
- [Verify Auth Scope](@./workflows/backend/verify-auth-scope.md) - Authentication and authorization
- [Write Code (TDD)](@./workflows/coding/write-code.md) - Test-driven development

**Key standards:**

- [Data Operations](@./standards/backend/data-operation.md) - Database and repository patterns
- [TypeScript](@./standards/code/typescript.md) - Language usage and imports

**Templates:**

- [Repository Template](@./patterns/backend/repository-template.md) - Data access layer boilerplate

### 📋 **All Engineers**

**Core workflows:**

- [Write Code (TDD)](@./workflows/coding/write-code.md) - **MANDATORY** test-driven development
- [Review Code](@./workflows/quality/review-code.md) - Code review standards
- [Approve PR](@./workflows/quality/approve-pr.md) - Final approval quality gates

**Essential standards:**

- [TypeScript](@./standards/code/typescript.md) - Core language requirements
- [Testing](@./standards/quality/testing.md) - TDD principles and patterns
- [Naming Conventions](@./standards/code/naming.md) - Consistent naming across codebase
- [Functions](@./standards/code/functions.md) - Function design and parameters

## 📁 **Directory Structure**

### **[workflows/](@./workflows/)** - HOW to do things

Step-by-step processes for common development tasks (50-150 lines each):

- `frontend/` - React component development
- `backend/` - Services, data controllers, authentication
- `coding/` - General programming workflows
- `quality/` - Code review and approval processes
- `project/` - Git, deployment, operations

### **[standards/](@./standards/)** - WHAT the rules are

Technical requirements and quality criteria (80-200 lines each):

- `code/` - TypeScript, naming, functions, documentation
- `frontend/` - React, hooks, accessibility
- `backend/` - APIs, data operations
- `quality/` - Testing standards
- `project/` - Git workflow standards

### **[patterns/](@./patterns/)** - Templates and examples

Ready-to-use implementation examples (30-100 lines each):

- `frontend/` - Component templates and examples
- `backend/` - Repository and service templates
- `code/` - Function and error handling patterns
- `quality/` - Test templates and examples

### **[references/](@./references/)** - Quick lookup information

Immediate reference materials:

- [Commit Examples](@./references/commit-examples.md) - Git commit message patterns
- [Tech Stack](@./references/tech-stack.md) - Commands and tool usage

## 🔄 **How Content Types Work Together**

```
TASK: "I need to create a React component"

1. WORKFLOW: Follow build-component.md for step-by-step process
2. STANDARDS: Apply react-components.md for technical requirements
3. PATTERNS: Use component-template.md as starting boilerplate
4. REFERENCES: Look up specific syntax in quick references
```

## 🚨 **Critical Requirements**

### **TDD Compliance**

- **ALL code development** must follow [Write Code (TDD)](@./workflows/coding/write-code.md)
- Tests written BEFORE implementation
- 100% coverage maintained with minimal tests

### **Quality Gates**

- **ALL commits** must follow [Commit with Git](@./workflows/project/commit-with-git.md)
- **ALL PRs** must pass [Review Code](@./workflows/quality/review-code.md) standards
- **NO `--no-verify`** commits allowed
- **ALL merges** require [Approve PR](@./workflows/quality/approve-pr.md) completion

### **Standards Compliance**

- **TypeScript strict mode** - No `any` types, explicit return types
- **Import order** - Node built-ins → third-party → project modules
- **Naming conventions** - camelCase, PascalCase, UPPER_SNAKE_CASE per rules
- **Error handling** - Explicit error types and handling patterns

## 📊 **File Size Targets Met**

The restructuring successfully achieved the target file sizes:

- **Workflows**: 50-150 lines (process-focused)
- **Standards**: 80-200 lines (requirement-focused)
- **Patterns**: 30-100 lines (template-focused)
- **References**: Varies (lookup-focused)

## 🔗 **Integration with Main CLAUDE.md**

This constitution directory provides the detailed implementation of the action workflows referenced in the main [CLAUDE.md](@../CLAUDE.md) file. The main file contains essential project context while this directory provides comprehensive technical guidance.

## 🆘 **Need Help?**

### **Can't find what you need?**

1. **Check your role section** above for most relevant content
2. **Browse directory READMEs** for comprehensive organization
3. **Use cross-references** - files link to related content
4. **Check main CLAUDE.md** for project context

### **Content unclear?**

- **Workflows** show you HOW to do something step-by-step
- **Standards** define WHAT the technical requirements are
- **Patterns** provide templates to copy and customize
- **References** offer quick lookup for syntax and commands

### **Still stuck?**

Reference the main [CLAUDE.md](@../CLAUDE.md) for project overview and integration guidance, or ask team members familiar with the specific domain area.

---

_This constitution ensures consistent, high-quality development practices across the entire Theriety monorepo while providing role-specific guidance for efficient workflow navigation._
