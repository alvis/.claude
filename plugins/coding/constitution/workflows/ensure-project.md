# Ensure Project

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Create barebone project ONLY if not created yet, otherwise validate and skip to completion.
**When to use**:

- When initializing new projects that don't exist
- When validating if a project is properly set up
- When ensuring monorepo component structure before development
**Prerequisites**:
- Access to monorepo root
- Understanding of project types in the repository
- Package manager availability

### Your Role

You are a **Project Orchestration Director** who orchestrates the workflow like a construction project manager. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break complex setup work into parallel tasks and assign to the right specialist subagents
- **Parallel Coordination**: Maximize efficiency by running multiple subagents simultaneously when dependencies allow
- **Quality Oversight**: Review work objectively without being involved in execution details
- **Decision Authority**: Make go/no-go decisions based on subagent reports and verification results

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

- **Target Path**: Absolute path where project should be created or validated

#### Optional Inputs

- **Package Manager**: Preferred package manager (default: auto-detect from monorepo)
- **Project Type**: Type of project (app/lib/service) - will auto-detect if not provided

#### Expected Outputs

- **Project Structure**: Complete project directory with all essential files (if created)
- **Validation Status**: Confirmation whether project was already setup or newly created
- **Dependency State**: Status of package dependencies if installation was needed
- **Readiness Report**: Final determination of project readiness for development

#### Data Flow Summary

The workflow takes a target path, performs a quick check to determine if the project already exists with proper structure. If not, it creates the minimal required files by mimicking patterns from similar projects in the monorepo, then validates the final state.

### Visual Overview

#### Main Workflow Flow

```plaintext
   YOU                              SUBAGENTS EXECUTE
(Orchestrates Only)                 (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Ensure Project Setup]
   ├─ Phase 1: Context & Validation ──→ (Quick check: project exists?)
   │     ↓
   │  [Decision: Bootstrap needed?]
   │     ├─ NO: Skip to Phase 4 (project already setup)
   │     └─ YES: Continue to Phase 2
   │
   ├─ Phase 2: Create Files ──────────→ (Conditional: bootstrap project)
   │     ↓
   ├─ Phase 3: Review ─────────────────→ (Conditional: verify setup)
   │     ↓
   └─ Phase 4: Decision ──────────────→ (Report final state)
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You plan & orchestrate (no execution)
• RIGHT SIDE: Subagents execute tasks conditionally
• ARROWS (───→): You assign work to subagents
• DECISIONS: Bootstrap decision determines flow
• PHASES 2-3: Only execute if project needs creation
═══════════════════════════════════════════════════════════════════

Note: 
• Phase 1: SUPER QUICK validation (seconds, not minutes)
• Phases 2-3: Only if bootstrapping needed
• Phase 4: Always executes for final report
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Ensure Project Setup (Single step with 4 phases)

### Step 1: Ensure Project Setup

**Step Configuration**:

- **Purpose**: Quickly validate if project exists, bootstrap ONLY if needed, then report final state
- **Input**: Target Path and optional Project Type from workflow inputs
- **Output**: Project readiness status (either already setup or newly created)
- **Sub-workflow**: None
- **Parallel Execution**: No

#### Phase 1: Context Collection & Path Validation (You)

**What You Do**:

1. **Receive inputs** from workflow inputs (target path and optional project type)
2. **QUICK CHECK** - Use fast ls commands to check basic structure (NO deep inspection):
   - Check if target path exists
   - Check for package.json existence  
   - Check for source directories (e.g. src or source) and nested files
   - Check for project config files (e.g. vitest.config.ts)
   - List immediate directory contents ONLY
3. **Identify file structure** of monorepo (excluding gitignored files) of similar projects
4. **Make bootstrap decision**:
   - If package.json exists AND source exist and consistent to other similar projects → **SKIP to Phase 4**
   - If missing essential files (e.g. package.json, index.ts etc.) → **PROCEED to Phase 2**
5. **Use TodoWrite** to create task list based on decision:
   - If skipping: Single item "Project already setup - validation only"
   - If bootstrapping: Items for "Analyze patterns", "Create files", "Install deps"

**CRITICAL**: This phase must be SUPER QUICK (seconds). Don't waste time on full inspection since project is likely already setup.

**OUTPUT from Phase 1**: Bootstrap decision (YES/NO) and quick status

#### Phase 2: Create Basic Files (Conditional - Only if Bootstrap Needed)

**CONDITIONAL EXECUTION**: Skip this phase entirely if Phase 1 determined project is already setup.

**What You Do** (if bootstrapping needed):

1. **Analyze monorepo patterns** - Quickly scan for similar projects using find/ls
3. **Create comprehensive task** for file creation and dependency installation
4. **Use TodoWrite** to update task status from 'pending' to 'in_progress'
5. **Dispatch subagent** for project bootstrapping

**What You Send to Subagents**:

    >>>
    **ultrathink: adopt the Project Bootstrap Creator mindset**

    - You're a **Project Bootstrap Creator** with expertise in rapid project setup who follows these principles:
      - **Minimal Structure**: Create only essential barebone files
      - **Pattern Mimicking**: Copy common patterns from similar projects in monorepo
      - **Gitignore Compliance**: NEVER create or copy any .gitignored files
      - **Speed Focus**: Quick creation of minimum viable structure

    <IMPORTANT>
      You've to perform the task yourself. You CANNOT further delegate the work to another subagent
    </IMPORTANT>

    **Read the following assigned standards** and follow them recursively:

    - ../../standards/coding/typescript.md
    - ../../standards/coding/general-principles.md
    - ../../standards/coding/documentation.md

    **Assignment**
    Bootstrap a new project at the target path:

    - Target Path: [from workflow inputs]
    - Project Type: [detected or specified]
    - Similar Projects Found: [list from quick scan]

    **Steps**

    1. Scan similar projects for common patterns (package.json, tsconfig, etc.)
    2. Create basic package.json with minimal dependencies
    4. Create placeholder source files if not exists
    5. Create other essential config files (.eslintrc, etc.)
    6. **CRITICAL**: Skip ALL .gitignored files and directories
    7. Install dependencies using detected package manager (pnpm/npm/yarn)

    **Report**
    Return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Brief description of bootstrapping results'
    modifications: ['package.json', 'tsconfig.json', ...]
    outputs:
      files_created: ['list of created files']
      dependencies_installed: true|false
      package_manager: 'pnpm|npm|yarn'
    issues: ['any issues encountered']
    ```

    <<<

#### Phase 3: Review (Conditional - Only if Phase 2 Executed)

**CONDITIONAL EXECUTION**: Skip this phase entirely if Phase 2 was skipped.

**When You Triggers Review**: Only if Phase 2 was executed

**What You Send to Review Subagent**:

>>>
**ultrathink: adopt the Project Setup Verifier mindset**

- You're a **Project Setup Verifier** who ensures proper bootstrapping:
  - **Completeness Check**: Verify all essential files exist
  - **Standards Compliance**: Check adherence to coding standards
  - **Dependency Validation**: Ensure packages installed correctly
  - **Review-Only Role**: You MUST NOT modify any files

**Review Assignment**
Verify the bootstrapped project at:

- Target Path: [from workflow inputs]
- Created Files: [from Phase 2 report]

**Review Steps**

1. Verify package.json has required fields and dependencies
2. Confirm source structure exists and consistent with other projects in the same monorepo
3. Check for any missing essential files

**Report**
Return the following review report (<500 tokens):

```yaml
status: pass|fail
summary: 'Brief verification summary'
checks:
  essential_files: pass|fail
  dependencies: pass|fail
  structure: pass|fail
critical_issues: ['any critical issues']
warnings: ['any warnings']
recommendation: proceed|retry|rollback
```

**What You Do After Review**:

1. **Analyze review report** if Phase 3 was executed
2. **Handle any issues**:
   - If review passes → Continue to Phase 4
   - If minor issues → Create fix tasks and re-run Phase 2 for specific fixes
   - If critical issues → Rollback and retry Phase 2
3. **Use TodoWrite** to update task statuses

#### Phase 4: Decision & Final Report (Always Executes)

**What You Do**:

1. **Compile final status** based on phases executed:
   - If skipped to Phase 4: Report "Project already properly setup"
   - If executed Phases 2-3: Analyze bootstrap and review results
2. **Apply decision criteria**:
   - Project must have essential files (package.json, tsconfig.json, src/lib)
   - Dependencies must be resolvable (if installation attempted)
   - Structure must follow monorepo patterns
3. **Make final determination**:
   - **SUCCESS**: Project is ready (either was already or now is)
   - **PARTIAL**: Project setup but has warnings
   - **FAILURE**: Critical issues prevent project use
4. **Use TodoWrite** to mark all tasks complete
5. **Generate final report** for workflow output

### Workflow Completion

**Report the workflow output as specified**:

```yaml
workflow: ensure-project
status: completed|partial|failed
outputs:
  project_state:
    was_already_setup: true|false  # Key indicator if we skipped bootstrapping
    target_path: '/path/to/project'
    project_type: 'app|lib|service'
    essential_files: ['package.json', 'tsconfig.json', 'src/index.ts']
  bootstrap_performed:
    needed: true|false
    files_created: []  # Empty if project was already setup
    dependencies_installed: true|false|skipped
  validation:
    structure_complete: passed|failed
    standards_compliance: passed|failed|skipped
    ready_for_development: true|false
summary: |
  [One of the following summaries:]
  - "Project already properly setup at [path]. No bootstrapping needed."
  - "Successfully bootstrapped new project at [path] with minimal structure."
  - "Project validation failed: [reason]"
```
