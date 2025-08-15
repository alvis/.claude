# Prepare for Coding

**Purpose**: Complete pre-coding verification to ensure proper setup and context before writing code
**When to use**: Before starting any coding task, especially when working with unfamiliar code or new features
**Prerequisites**: Development environment set up, repository cloned, task requirements understood

## Expert Role

You are a **Senior Software Engineer** with deep expertise in development environment setup and codebase analysis. Your mindset prioritizes:

- **Thoroughness**: Never skip pre-coding checks, as they prevent hours of debugging later
- **Pattern Recognition**: Quickly identify existing patterns and conventions in unfamiliar codebases
- **Quality First**: Ensure all quality tools are working before writing any code
- **Context Awareness**: Understand the full picture before making any changes

## Steps

### 1. Verify Development Environment

Check that your environment is properly configured:

```bash
# Check Node.js version
node --version  # Should match project requirements

# Check npm/package manager
npm --version

# Verify repository status
git status
```

### 2. Check Dependencies

Ensure all required libraries are available:

```bash
# Review package.json for dependencies
cat package.json

# Install/update dependencies if needed
npm ci

# Verify critical dependencies are installed
npm list --depth=0
```

### 3. Explore Existing Code Patterns

Before creating new code, understand existing patterns:

- Look at neighboring files for similar functionality
- Check existing components before creating new ones
- Review import styles and framework choices
- Identify reusable utilities and helpers

### 4. Review Project Structure

Understand the codebase organization:

```bash
# Review directory structure
ls -la

# Check for configuration files
ls -la .*rc* *.config.*

# Look for documentation
find . -name "*.md" -o -name "*.txt" | head -10
```

### 5. Verify Testing Setup

Ensure testing framework is ready:

```bash
# Check test configuration
cat package.json | grep -A5 -B5 "test"

# Run existing tests to verify setup
npm run coverage
```

### 6. Check Code Quality Tools

Verify linting and type checking:

```bash
# Run TypeScript compiler
npm run typecheck || npx tsc --noEmit

# Run linter
npm run lint

# Check for pre-commit hooks
ls -la .git/hooks/
```

### 7. Review Related Standards

Based on your task, review relevant standards:

- For functions: [Function Design Standards](@../../standards/code/functions.md)
- For TypeScript: [TypeScript Standards](@../../standards/code/typescript.md)
- For React: [React Component Standards](@../../standards/frontend/react-components.md)

### 8. Plan Your Approach

Before writing code:

- Identify what needs to be created vs modified
- Plan the test cases you'll write first
- Consider integration points and dependencies
- Sketch out the basic structure

### 9. Set Up Your Workspace

Organize your development environment:

```bash
# Create feature branch if needed
git checkout -b feat/your-feature-name

# Open relevant files in your editor
# Set up terminal windows for testing/building
```

## Recommended Tools

### Analysis Tools

- **Grep/Glob**: Fast pattern searching across codebase
- **Read**: Detailed file examination for understanding patterns
- **LS**: Directory structure exploration

### Verification Tools

- **Bash**: Run all verification commands (npm, git, tests)
- **Task**: Complex multi-step verifications with specialized agents

### Documentation Tools

- **WebSearch**: Find framework documentation and best practices
- **Read**: Review existing documentation and standards

### When to Use Each Tool

- **Initial exploration**: Start with LS and Glob to understand structure
- **Pattern discovery**: Use Grep to find similar implementations
- **Deep understanding**: Use Read for detailed file analysis
- **Verification**: Use Bash for all command execution
- **Complex analysis**: Use Task agent for multi-file pattern analysis

## Standards to Follow

**🔴 MANDATORY: All standards listed below MUST be followed without exception**

- [General Principles](@../../standards/code/general-principles.md) - Core coding principles and best practices
- [TypeScript Standards](@../../standards/code/typescript.md) - TypeScript conventions and patterns
- [Naming Conventions](@../../standards/code/naming.md) - Variable, function, and file naming rules
- [Documentation Guidelines](@../../standards/code/documentation.md) - Comments, JSDoc, and documentation standards
- [Folder Structure](@../../standards/code/folder-structure.md) - Project organization patterns
- [Testing Standards](@../../standards/quality/testing.md) - Test structure and coverage requirements

## Pre-Coding Checklist

Before writing any code, verify:

✅ **Environment Ready**

- [ ] Correct Node.js version installed
- [ ] Dependencies installed and up to date
- [ ] Git repository clean and on correct branch

✅ **Context Understood**

- [ ] Reviewed similar existing code
- [ ] Identified reusable patterns and utilities
- [ ] Checked for existing components/functions
- [ ] Understood project structure and conventions

✅ **Quality Tools Working**

- [ ] TypeScript compiler runs without errors
- [ ] Linter passes on existing code
- [ ] Test runner works and existing tests pass
- [ ] Pre-commit hooks configured (if applicable)

✅ **Standards Reviewed**

- [ ] Read relevant coding standards for your task
- [ ] Understood testing requirements (TDD workflow)
- [ ] Reviewed naming and structure conventions
- [ ] Planned approach including test cases

## Quality Gates Before Proceeding

**Required checks before starting to code:**

```bash
# These must all pass before you begin coding
npm run typecheck     # TypeScript compilation
npm run lint         # Code style validation
npm run coverage         # Existing test suite
```

Skip quality gates only when modifying comments or documentation.

## Common Issues

- **Missing dependencies**: Always run `npm ci` in new repositories
- **Wrong Node version**: Check `.nvmrc` or `package.json` engines field
- **Broken existing tests**: Fix broken tests before adding new code
- **Unknown patterns**: Don't guess - look at existing similar code
- **Missing context**: Review related files and documentation
- **Skipping standards**: Always review relevant standards first
