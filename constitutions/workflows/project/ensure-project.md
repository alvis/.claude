# Ensure Project

**Purpose**: Validate and bootstrap a project structure at a given path, ensuring minimum viable project setup with proper metadata and dependencies
**When to use**: When initializing new projects, validating existing project structure, or setting up development environments for monorepo components
**Prerequisites**: Access to monorepo root, understanding of project types in the repository, package manager availability (pnpm)

## Expert Role

You are a **DevOps Engineer** with deep expertise in project initialization and monorepo management. Your mindset prioritizes:

- **Structure Consistency**: Ensure all projects follow established patterns and conventions within the monorepo
- **Dependency Management**: Properly configure shared dependencies and maintain version consistency across projects
- **Bootstrap Efficiency**: Minimize setup time while ensuring all essential components are in place
- **Type Detection**: Accurately identify project types to apply appropriate scaffolding templates
- **Environment Safety**: Never expose or copy sensitive files, always respect .gitignore patterns

## Steps

### 0. Workflow Preparation and Prepare Task Management Mindset

**Initialize workflow tracking and identify reusable components**:

- [ ] Identify available task tracking tools and use the most appropriate one
- [ ] Create initial todo items for all known major workflow steps
- [ ] Include estimated complexity for each task
- [ ] Set initial status to 'pending' for all tasks
- [ ] **IMPORTANT**: Be prepared to add more todo items as new tasks are discovered
- [ ] Mark this initialization task as 'completed' once done

**Identify existing workflows to reuse**:

- [ ] Search for applicable existing workflows
- [ ] Reference [Prepare Coding](@../coding/prepare-coding.md) for environment setup
- [ ] Reference [Commit with Git](@commit-with-git.md) for version control setup
- [ ] Document workflow dependencies in a clear format
- [ ] Map which steps will use each referenced workflow
- [ ] Avoid recreating steps that existing workflows already handle

**Plan agent delegation strategy**:

- [ ] Identify available specialized agents in the system
- [ ] Determine which steps require specialized expertise
- [ ] Create a delegation plan mapping steps to appropriate agents
- [ ] Document parallel execution opportunities where dependencies allow
- [ ] Specify verification points for quality assurance

**Proactive task discovery**:

- [ ] As workflow progresses, actively identify additional tasks
- [ ] Add new todo items immediately when discovered
- [ ] Update complexity estimates if tasks prove more involved
- [ ] Break down complex tasks into subtasks when needed

### 1. Validate Project Path and Structure

**Analyze target path and determine project requirements**:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] Verify target path exists and is accessible
- [ ] Check for existing project metadata files (package.json, tsconfig.json, etc.)
- [ ] Identify source directory structure (src/, lib/, components/)
- [ ] Determine project type from path structure or existing configuration
- [ ] **IMPORTANT**: Always respect .gitignore - never read or copy ignored files

**Verification**:

- [ ] Subagent/workflow self-verification: Path validated and type identified
- [ ] Primary agent verification: Project requirements clearly documented
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

**Anti-pattern to avoid:**

```typescript
// ❌ Don't do this - ignoring .gitignore
import fs from 'fs'
fs.readdirSync('./node_modules') // This violates .gitignore rules
```

### 2. Analyze Similar Projects in Monorepo

**Discover patterns and shared dependencies from existing projects**:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] Scan monorepo for projects of the same type (apps/, libs/, services/)
- [ ] Extract common dependencies from package.json files
- [ ] Identify shared configuration patterns (tsconfig, eslint, etc.)
- [ ] Document minimum required project structure
- [ ] **CRITICAL**: Skip all .gitignored directories and files during analysis

**Verification**:

- [ ] Subagent/workflow self-verification: Pattern analysis complete with common dependencies identified
- [ ] Primary agent verification: Minimum structure requirements documented
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

### 3. Create Minimum Project Structure

**Bootstrap project with essential files and directories**:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] Create package.json with minimum dependencies shared by similar projects
- [ ] Create src/ directory structure appropriate for project type
- [ ] Add essential configuration files (tsconfig.json, .eslintrc, etc.)
- [ ] Create basic README.md with project information
- [ ] Set up appropriate .gitignore if not inherited from root

**Verification**:

- [ ] Subagent/workflow self-verification: All essential files created with proper structure
- [ ] Primary agent verification: Project structure follows monorepo conventions
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

**Anti-pattern to avoid:**

```json
// ❌ Don't do this - hardcoded versions without checking existing projects
{
  "dependencies": {
    "react": "18.0.0" // Should match other projects in monorepo
  }
}
```

### 4. Bootstrap with Package Manager

**Initialize project dependencies and validate setup**:

**Task tracking**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Review if this step reveals additional subtasks and add them immediately

**Core actions**:

- [ ] Identify package manager from monorepo root (pnpm, npm, yarn)
- [ ] Run package manager install command for the project
- [ ] Verify all dependencies resolve correctly
- [ ] Run any post-install scripts or validation commands
- [ ] Confirm project builds successfully if build scripts exist

**Verification**:

- [ ] Subagent/workflow self-verification: Dependencies installed and project functional
- [ ] Primary agent verification: No package resolution errors or build failures
- [ ] Mark this task as 'completed' in task tracking tool when verified
- [ ] Add any follow-up tasks discovered during execution

### 5. Final Review and Comprehensive Validation

**Primary agent performs final review of all delegated work**:

**Task tracking review**:

- [ ] Mark this task as 'in_progress' in task tracking tool
- [ ] Verify all tracked tasks show 'completed' status
- [ ] Confirm no tasks remain in 'pending' or 'in_progress' state

**Subagent work review**:

- [ ] Review outputs from all delegated agents
- [ ] Verify each subagent's self-verification was performed
- [ ] Double-check work quality meets standards
- [ ] Confirm all referenced workflows were properly executed

**Requirements validation**:

- [ ] Project metadata file exists and contains appropriate dependencies
- [ ] Source directory structure follows monorepo conventions
- [ ] Package manager successfully installed all dependencies
- [ ] No .gitignored files were read or copied during setup
- [ ] Project builds and runs without errors

**Final sign-off**:

- [ ] Primary agent approves all work
- [ ] Mark this final review task as 'completed' in task tracking tool
- [ ] Document any deviations or follow-up items

## Standards to Follow

**🔴 MANDATORY: All standards listed below MUST be followed without exception**

- [Folder Structure](@../../standards/code/folder-structure.md) - Project directory organization and naming conventions
- [TypeScript](@../../standards/code/typescript.md) - TypeScript configuration and coding standards
- [Environment Variables](@../../standards/code/environment-variables.md) - Secure handling of configuration values
- [Git Workflow](@../../standards/project/git-workflow.md) - Version control and .gitignore compliance

## Common Issues

- **Package Version Conflicts**: Dependencies don't match other projects in monorepo → Check existing package.json files and align versions with workspace standards
- **Missing Package Manager**: pnpm/npm/yarn not available in environment → Install appropriate package manager or use container with pre-installed tools
- **Permission Errors**: Cannot create files in target directory → Verify write permissions and user access to the target path
- **Gitignore Violations**: Accidentally reading node_modules or build artifacts → Always check .gitignore patterns before file operations
- **Project Type Misidentification**: Wrong template applied for project type → Analyze path structure and existing projects more carefully to determine correct type
- **Dependency Resolution Failures**: npm/pnpm install fails with peer dependency errors → Review and align peer dependencies with other projects in the monorepo
- **Configuration File Conflicts**: tsconfig.json or eslint config causes build errors → Ensure configuration extends from monorepo root and doesn't conflict with shared settings

## Project Setup Report Template

### Expected Output Format

```markdown
## Project Initialization Report

### Summary
Project successfully initialized at [path] with [project-type] configuration

### Project Structure Created
- package.json with [X] dependencies aligned with monorepo standards
- src/ directory with [structure description]
- Configuration files: [list of config files]
- Documentation: README.md with project overview

### Dependencies Installed
- Total packages: [count]
- Shared with other projects: [percentage]%
- Project-specific dependencies: [list]

### Validation Results
- ✅ Package manager install successful
- ✅ Project builds without errors
- ✅ No .gitignore violations detected
- ✅ Structure follows monorepo conventions

### Next Steps
- Begin development following TDD workflow
- Set up CI/CD pipeline if needed
- Add project-specific documentation
```