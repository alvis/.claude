---
name: setup-project
description: Ensure project structure exists before development, creating barebone scaffolding only if needed. Use when initializing new projects, validating project setup, or ensuring monorepo component structure.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
argument-hint: <target-path> [--type=app|lib|service]
---

# Setup Project

Ensures a project is properly set up for development. Performs a quick validation of the target path and, only if essential files are missing, bootstraps a minimal project structure by mimicking patterns from similar projects in the monorepo.

## Purpose & Scope

**What this command does NOT do**:

- Implement business logic or feature code
- Install unnecessary dependencies
- Create deep file hierarchies beyond the minimum viable structure
- Modify existing project files that are already properly configured
- Create or copy any `.gitignored` files or directories

**When to REJECT**:

- Target path is outside the repository
- No monorepo root can be detected
- Project already exists and is fully configured (report as already setup)

## Applicable Standards

When executing this skill, the following standards apply:

| Standard | Purpose |
|---|---|
| `file-structure` | Project directory layout and organization |
| `universal/write` | General code authoring conventions |
| `typescript/write` | TypeScript configuration and compilation |
| `documentation/write` | README and inline documentation |

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Context Collection and Path Validation

1. **Receive inputs**
   - Parse target path from $ARGUMENTS
   - Parse optional `--type` flag (app, lib, service) or auto-detect
   - Determine if running as standalone or as part of composite (`--from-composite`)

2. **Quick check** -- use fast ls commands to check basic structure (NO deep inspection):
   - Check if target path exists
   - Check for `package.json` existence
   - Check for source directories (e.g., `src` or `source`) and nested files
   - Check for project config files (e.g., `vitest.config.ts`)
   - List immediate directory contents ONLY

3. **Identify file structure** of monorepo (excluding gitignored files) of similar projects

4. **Make bootstrap decision**:
   - If `package.json` exists AND source exists and is consistent with other similar projects: **SKIP to Step 4** (already setup)
   - If missing essential files (e.g., `package.json`, `index.ts`): **PROCEED to Step 2**

**CRITICAL**: This step must be SUPER QUICK (seconds). Do not waste time on full inspection since the project is likely already setup.

### Step 2: Create Basic Files (Conditional -- Only if Bootstrap Needed)

**CONDITIONAL EXECUTION**: Skip this step entirely if Step 1 determined the project is already setup.

1. **Analyze monorepo patterns** -- quickly scan for similar projects using Glob/ls
2. **Bootstrap the project**:
   - Scan similar projects for common patterns (package.json, tsconfig, etc.)
   - Create basic `package.json` with minimal dependencies
   - Create placeholder source files if not exists
   - Create other essential config files
   - **CRITICAL**: Skip ALL `.gitignored` files and directories
   - Install dependencies using detected package manager (pnpm/npm/yarn)

### Step 3: Verify Setup (Conditional -- Only if Step 2 Executed)

**CONDITIONAL EXECUTION**: Skip this step entirely if Step 2 was skipped.

1. Verify `package.json` has required fields and dependencies
2. Confirm source structure exists and is consistent with other projects in the same monorepo
3. Check for any missing essential files
4. If verification fails with minor issues, fix and re-verify
5. If verification fails critically, rollback and retry Step 2

### Step 4: Final Report (Always Executes)

1. **Compile final status** based on steps executed:
   - If skipped to Step 4: Report "Project already properly setup"
   - If executed Steps 2-3: Analyze bootstrap and verification results
2. **Apply decision criteria**:
   - Project must have essential files (`package.json`, `tsconfig.json`, `src/` or `lib/`)
   - Dependencies must be resolvable (if installation attempted)
   - Structure must follow monorepo patterns
3. **Make final determination**:
   - **SUCCESS**: Project is ready (either was already or now is)
   - **PARTIAL**: Project setup but has warnings
   - **FAILURE**: Critical issues prevent project use

### Step 5: Reporting

**Output Format**:

```
[OK/FAIL] Command: setup-project $ARGUMENTS

## Summary
- Target path: [path]
- Project type: [app|lib|service]
- Was already setup: [yes/no]
- Bootstrap performed: [yes/no]
- Dependencies installed: [yes/no/skipped]

## Actions Taken
1. [Validation results]
2. [Files created, if any]
3. [Dependencies installed, if any]

## Project State
- Essential files: [PASS/FAIL]
- Structure: [PASS/FAIL]
- Ready for development: [yes/no]

## Next Steps
1. [Immediate next action]
```

## Examples

### Validate Existing Project

```bash
/setup-project "/path/to/existing/project"
# Quick check: package.json exists, src/ exists
# Result: "Project already properly setup. No bootstrapping needed."
```

### Bootstrap New Project

```bash
/setup-project "/path/to/new/project" --type=lib
# Detects missing structure, scans similar libs
# Creates package.json, tsconfig.json, src/index.ts
# Installs dependencies
```

### Error Case

```bash
/setup-project "/invalid/path"
# Error: Target path is outside the repository
# Suggestion: Provide a path within the monorepo
```
