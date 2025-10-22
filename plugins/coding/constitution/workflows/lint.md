# Linting

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Apply documentation, TypeScript, and error-handling standards to ensure consistent code quality across all files, including proper JSDoc comments, logging messages, error handling, and correct ordering of functions and interface fields.

**When to use**:

- Before committing major changes to ensure code standards compliance
- During code review preparation to automate style and formatting fixes
- When onboarding legacy code to bring it up to current standards

**Prerequisites**:

- Node.js environment with package.json configured
- Linting tools installed (ESLint, Prettier, or similar)
- Access to project coding standards documentation

### Your Role

You are a **Quality Orchestrator** who orchestrates the workflow like a meticulous quality control director. You never execute tasks directly, only delegate and coordinate. Your management style emphasizes:

- **Strategic Delegation**: Break large file sets into manageable batches (max 20 files per subagent) and assign to specialized linting experts
- **Parallel Coordination**: Maximize efficiency by running multiple subagents simultaneously to process different file batches
- **Standards Enforcement**: Ensure all subagents strictly follow documentation, TypeScript, and error-handling standards
- **Quality Oversight**: Review linting reports objectively and track overall compliance status
- **Decision Authority**: Make decisions on workflow completion based on successful linting of all files

## 2. WORKFLOW OVERVIEW

### Workflow Input/Output Specification

#### Required Inputs

(No mandatory inputs - workflow can operate on defaults)

#### Optional Inputs

- **File Area Specifier**: Path or pattern to specify which files to lint (default: all source code and test files in current directory, ignoring .gitignored files)
- **Standards Override**: Custom standards paths to apply instead of defaults

#### Expected Outputs

- **Linting Report**: Comprehensive report showing files processed, standards applied, and compliance status
- **Modified Files List**: Array of file paths that were updated to meet standards
- **Change Summary**: Detailed breakdown of changes made (JSDoc additions, comment formatting, function reordering, etc.)
- **Compliance Status**: Pass/fail status for each file against the applied standards

#### Data Flow Summary

The workflow discovers all target files based on the input specifier, batches them for parallel processing (max 20 files per batch), applies documentation and coding standards to each batch through subagents, and produces a comprehensive compliance report with all modifications made.

### Visual Overview

#### Main Workflow Flow

```plaintext
  YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Apply Linting Standards]
   |
   ├─[Phase 1: Planning] ─────────────→ (You plan all tasks)
   |     • Discover files directly
   |     • Create batches
   |     • Prepare instructions
   |
   ├─[Phase 2: Execution] ─────────────→ (Subagents execute in parallel)
   |     • Apply standards
   |     • Run linting
   |     • Fix issues
   |
   └─[Phase 3: Decision] ─────────────→ (You analyze & summarize)
   |     • Review all reports
   |     • Create final summary
   |     • Complete workflow
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• Phase 1: ALL planning done by YOU
• Phase 2: ALL execution done by SUBAGENTS in parallel
• Phase 3: ALL decisions and summary done by YOU
• Workflow is LINEAR: Phase 1 → 2 → 3 within single step
═══════════════════════════════════════════════════════════════════

Note:
• Each phase has ONE clear purpose - no sub-phases
• Maximum parallelization in execution phase
• Clear separation of planning, execution, and decision
```

## 3. WORKFLOW IMPLEMENTATION

### Workflow Steps

1. Apply Linting Standards - Complete linting process from file discovery through summary report

### Step 1: Apply Linting Standards

**Step Configuration**:

- **Purpose**: Complete end-to-end linting process from file discovery through summary report
- **Input**: Optional file area specifier from workflow input
- **Output**: Final linting report with all modifications and compliance status
- **Sub-workflow**: (none)
- **Parallel Execution**: Yes (in Phase 2)

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** - Parse the optional file area specifier
2. **Discover all files** using find command:
   - Execute: `find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) | grep -v node_modules | grep -v dist`
   - Filter out gitignored files
   - Count total files found
3. **Determine the standards** to apply:
   - documentation.md
   - typescript.md
   - error-handling-logging.md
4. **Create dynamic batches** following these rules:
   - Generate batches at runtime based on files found
   - Limit each batch to max 20 files
   - Group related files together when possible (same directory/module)
5. **Plan parallel linting** - Prepare detailed instructions for each linting batch
6. **Use TodoWrite** to create comprehensive task list including:
   - One task per file batch for linting
7. **Prepare all subagent instructions** in advance for the entire workflow

**OUTPUT from Planning**: Complete workflow plan with all tasks queued

#### Phase 2: Execution (Subagents)

**What You Send to Subagents**:

You spin up subagents to perform linting in parallel, up to **10** subagents at a time:

- **[IMPORTANT]** When there are any issues reported, you must stop dispatching further subagents until all issues have been rectified
- **[IMPORTANT]** You MUST ask all subagents to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update each batch's status from 'pending' to 'in_progress' when dispatched

Request each subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Code Standards Expert mindset**

    - You're a **Code Standards Expert** with deep expertise in TypeScript and JavaScript best practices who follows these technical principles:
      - **Standards Compliance**: Strictly apply all specified coding standards
      - **Consistency First**: Ensure uniform formatting and style across all files
      - **Quality Assurance**: Verify all changes improve code quality
      - **Automated Validation**: Use linting tools to confirm compliance

    **Read the following assigned standards** and follow them recursively (if A references B, read B too):

    - documentation.md
    - typescript.md
    - error-handling-logging.md

    **Assignment**
    You're assigned with the following files (max 20):

    - [file1.ts]
    - [file2.js]
    - ...

    **Steps**

    1. Read each assigned file to understand current implementation
    2. Apply documentation standards:
       - Add/update JSDoc comments for all functions, classes, and interfaces
       - Ensure comments are clear, concise, and follow consistent format
       - Document parameters, return types, and examples where appropriate
    3. Apply TypeScript standards:
       - Ensure proper type annotations on all functions and variables
       - Order interface fields alphabetically or by logical grouping
       - Order class methods: constructor, public, protected, private
    4. Apply error-handling and logging standards:
       - Standardize all error messages with consistent format
       - Ensure logging messages follow established patterns
       - Add appropriate error handling where missing
    5. Reorder functions in files following logical flow:
       - Exports first, then main functions, then helpers
       - Group related functions together
    6. Run the linting script from the nearest package.json:
       - Execute: npm run lint or yarn lint (infer from lock file)
       - If no lint script, try: npx eslint [files]
       - Ensure all files pass with no linting errors
    7. Fix any remaining linting issues reported by the tool

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Processed X files, applied Y changes, all passing linting'
    modifications: ['file1.ts', 'file2.js', ...]
    outputs:
      files_processed: X
      jsdoc_added: Y
      functions_reordered: Z
      linting_status: 'all_pass|some_fail'
      changes_summary:
        - 'Added JSDoc to X functions'
        - 'Reordered Y interfaces'
        - 'Fixed Z error messages'
    issues: ['issue1', 'issue2', ...]  # only if problems encountered
    ```
    <<<

#### Phase 3: Decision (You)

**What You Do**:

1. **Analyze all reports** from parallel linting subagents
2. **Aggregate all file modification counts** from batch reports
3. **Compile list of all modified files** from all batches
4. **Summarize types of changes made**:
   - JSDoc additions/updates
   - Function reordering
   - Interface/object field reordering
   - Error message standardization
   - Logging format fixes
5. **Calculate overall compliance rate** across all files
6. **Identify any remaining issues or warnings**
7. **Apply decision criteria**:
   - Check if all files passed linting
   - Review any reported issues
8. **Handle any issues**:
   - If some files failed, decide on retry strategy
   - Document any unresolved issues
9. **Create final workflow summary**:
   - Calculate total files processed
   - Sum up all modifications made
   - Determine overall compliance rate
   - Generate executive summary
10. **Use TodoWrite** to mark all tasks as completed
11. **Prepare final output** in required format

### Workflow Completion

**Report the workflow output as specified**:

```yaml
workflow: linting
status: completed
summary: 'Applied documentation, TypeScript, and error-handling standards to [X] files'
outputs:
  files_processed: X
  files_modified: Y
  compliance_achieved: Z%
  changes_made:
    - 'Added/updated JSDoc comments in A files'
    - 'Reordered functions in B files'
    - 'Standardized error messages in C files'
    - 'Fixed logging formats in D files'
  modified_files_list: 
    - 'path/to/modified/file1.ts'
    - 'path/to/modified/file2.js'
  linting_status: 'all_pass'
timestamp: 'YYYY-MM-DD HH:MM:SS'
```
