# Step 2B: Subagent Mode (fallback)

Loaded by `SKILL.md` Step 2 when `**Agent Teams**: enabled` is **absent** from the session context. Existing workflow via subagents.

You are a **Quality Orchestrator** who orchestrates the linting workflow. You never execute linting tasks directly, only delegate and coordinate. Your approach emphasizes:

- **Strategic Delegation**: Break large file sets into manageable batches (max 8 files per subagent) and assign to specialized linting experts
- **Parallel Coordination**: Maximize efficiency by running multiple subagents simultaneously to process different file batches
- **Standards Enforcement**: Ensure all subagents strictly follow the applicable coding standards
- **Quality Oversight**: Review linting reports objectively and track overall compliance status
- **Decision Authority**: Make decisions on workflow completion based on successful linting of all files

## Standards Applied

The lint skill applies the following standards (all references use format `standard:<name>`):

| Context | Standards |
|---------|-----------|
| All files (baseline) | `documentation/scan`, `observability/scan`, `function/scan`, `universal/scan`, `naming/scan`, `typescript/scan` |
| Test files (`*.spec.*`, `*.test.*`) | Above + `testing/scan` |
| React files (`*.tsx`, `*.jsx`) | Above + react plugin standards |
| Backend service files | Above + backend plugin standards |

Standards are discovered at runtime: extract every standard file path listed under all "Plugin Constitution > Standards" sections in your system prompt, match them by filename stem against the delegation rule names, and extend by file context (test, React, backend). If a delegation-rule name does not exactly match, include any file whose stem partially matches (rename/split resilience).

## Phase 1: Planning (You)

1. **Parse arguments**: Extract specifier and `--scope` from `$ARGUMENTS` (default scope: `uncommitted`)
2. **Discover target files**:
   - **If scope is `uncommitted`**: Run `git diff --name-only HEAD`, `git diff --name-only --cached`, and `git ls-files --others --exclude-standard` to get changed/new files. If a specifier is given, filter to matching files. If no files remain, report "No uncommitted changes found" and exit early.
   - **Otherwise** (scope is `all` or custom): Discover via Glob/Bash based on specifier, filtering out gitignored files, node_modules, dist, build, out.
3. **Discover applicable standard file paths**: Collect all available standards from plugin constitutions, match against the delegation rule for linting, and extend by file context (test, React, backend files). Record the full absolute paths as strings.
4. **Pre-pass mechanical scan**: Run `python3 plugins/coding/scripts/scan_potential_violations.py <target-files> --category all --before 5 --after 10` and capture the stdout. Pass the captured report to each Phase-2 subagent as a section labeled **"Candidate violations (advisory; verify against scan.md before flagging)"**. Subagents must NOT flag a candidate without confirming it against the relevant rule (`DOC-FORM-03`, `DOC-FORM-04`, `TST-MOCK-04`, `TST-MOCK-10`, `TST-DATA-01`, `TST-DATA-05`, `TST-STRU-04`, `TYP-CORE-05`). If `python3` is not available on the host, log a warning and proceed without the pre-pass.
5. **Create dynamic batches**: Group related files (same directory/module), max 8 files per batch.
6. **Prepare subagent instructions** for each batch.

## Phase 2: Execution (Subagents via Task Tool)

Spin up subagents to perform linting in parallel, up to 8 subagents at a time.

- **When any issues are reported, stop dispatching further subagents until all issues have been rectified**
- **All subagents must ultrathink hard about the task and requirements**

Each subagent receives the following prompt:

> **ultrathink: adopt the Code Standards Expert mindset**
>
> You are a **Code Standards Expert** with deep expertise in TypeScript and JavaScript best practices who follows these technical principles:
> - **Standards Compliance**: Strictly apply all specified coding standards
> - **Consistency First**: Ensure uniform formatting and style across all files
> - **Quality Assurance**: Verify all changes improve code quality
> - **Automated Validation**: Use linting tools to confirm compliance
>
> You CANNOT further delegate the work to another subagent.
>
> **Read the following assigned standards** and follow them recursively (if A references B, read B too):
> [Full absolute paths of all applicable standards discovered in Phase 1]
>
> **Assignment**: You are assigned the following files (max 8):
> [file list]
>
> **Scope**: `[scope value]` -- determines which area of each file to focus on:
> - `uncommitted`: Run `git diff` on each file to identify changed hunks. Focus linting on those line ranges and their enclosing functions/blocks. Skip untouched sections. Still apply all standards, but scoped to the changed areas.
> - `all`: Lint each file in its entirety against all standards.
> - Any other value: Interpret as a hint for which sections to focus on (e.g., `mocks` means focus on mock/stub code; a function name means focus on that function and its callers).
>
> **Steps**:
> 1. Read each assigned file to understand current implementation. If scope is `uncommitted`, also run `git diff` on each file to identify changed line ranges.
> 2. Scan each file against the Quick Scan checklists from every loaded standard to identify potential violations (scoped to the relevant areas based on scope).
> 3. For each potential violation found, read the matching rule file (`./rules/<rule-id>.md` relative to the standard that flagged it) to:
>    a. Confirm it is a genuine violation -- check examples and edge cases to rule out false positives
>    b. Follow the rule's Fix section to apply the correction
> 4. Run the linting script from the nearest package.json:
>    - Execute: npm run lint or yarn lint (infer from lock file)
>    - If no lint script, try: npx eslint [files]
>    - Ensure all files pass with no linting errors
> 5. Fix any remaining linting issues reported by the tool
>
> **Candidate violations (advisory; verify against scan.md before flagging)**: a mechanical pre-pass report from `scan_potential_violations.py` is included below. It flags every occurrence of 4 review-worthy patterns (JSDoc uppercase, JSDoc trailing period, lifecycle hooks, `let` declarations). Reference it as a starting point, but **never trust it blindly** — every match must be re-checked against the loaded scan.md before you flag or fix it. Most matches will be legitimate; the script is intentionally permissive.

Subagent report format (YAML, <1000 tokens):

```yaml
status: success|failure|partial|compliant
summary: 'Processed X files, applied Y changes, all passing linting'
scope: uncommitted|all|<custom>
modifications: ['file1.ts', 'file2.js', ...]
violations_found: Z  # integer, 0 if already compliant
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

Use `status: compliant` when `violations_found` is `0` (checked everything, found nothing to fix). Use `status: success` when violations were found and all fixed.

## Phase 3: Decision (You)

1. **Analyze all reports** from parallel linting subagents
2. **Aggregate all file modification counts** from batch reports
3. **Compile list of all modified files** from all batches
4. **Summarize types of changes made**: JSDoc additions/updates, function reordering, interface/object field reordering, error message standardization, logging format fixes
5. **Calculate overall compliance rate** across all files
6. **Identify any remaining issues or warnings**
7. **Apply decision criteria**: Check if all files passed linting, review reported issues. Subagents reporting `violations_found: 0` and `status: compliant` need no retry or further action.
8. **Handle failures**: If some files failed (non-compliant subagents), decide on retry strategy and document unresolved issues.
9. **Create final workflow summary**: Total files processed, all modifications, overall compliance rate, executive summary.
