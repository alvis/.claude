# Code Review Workflow

## Purpose & Context

This workflow ensures comprehensive review of code following established coding standards.

**Use Cases:**

- Reviewing any code (existing codebase, PRs, specific files)
- Ensuring code quality standards are met
- Validating test coverage and documentation
- Security review for sensitive changes

## Visual Flow

```
┌─────────────────────────────┐
│  Phase 1: File              │
│  Identification (You)        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Phase 2: Review Execution  │
│  (All 5 Agents in Parallel) │
├─────────────────────────────┤
│  ╔══════════════════════╗   │
│  ║ Code Quality Agent   ║───┤
│  ╚══════════════════════╝   │
│  ╔══════════════════════╗   │
│  ║ Testing Agent        ║───┤
│  ╚══════════════════════╝   │
│  ╔══════════════════════╗   │
│  ║ Documentation Agent  ║───┼──→ Phase 3
│  ╚══════════════════════╝   │
│  ╔══════════════════════╗   │
│  ║ Security Agent       ║───┤
│  ╚══════════════════════╝   │
│  ╔══════════════════════╗   │
│  ║ Linting Agent        ║───┤
│  ╚══════════════════════╝   │
└─────────────────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Phase 3: Consolidation     │
│  (You)                      │
└─────────────────────────────┘
```

## Workflow Steps

#### Phase 1: File Identification (You)

**Goal**: Identify all files that need review

**Steps:**

1. **Get File Information**
   - Identify source of review request (PR, existing code, specific files)
   - Get list of files to review
   - Identify file types and categories

2. **Categorize Files**
   - Source code files
   - Test files
   - Documentation files
   - Configuration files

3. **Create Review Plan**
   - Map files to appropriate review criteria
   - Set review priorities
   - Identify critical paths

#### Phase 2: Execution (Subagents)

**Goal**: Perform comprehensive code review across all quality dimensions

**Parallel Execution**: Deploy all 5 review agents simultaneously

Request each subagent to perform the following steps with full detail:

    >>>
    **ultrathink: adopt the Code Review Specialist mindset**
    
    You're a **Code Review Specialist** with deep expertise in your specific domain who follows these technical principles:
    - **Standards Compliance**: Ensure code follows all established standards
    - **Quality Assurance**: Identify issues and provide actionable feedback
    - **Best Practices**: Recommend improvements based on industry standards
    
    **Read the following assigned standards** and follow them recursively:
    
    **For Code Quality Agent (@marcus-williams-code-quality)**:
    - ../../standards/coding/general-principles.md
    - ../../standards/coding/typescript.md
    - ../../standards/coding/functions.md
    - ../../standards/coding/naming/variables.md
    - ../../standards/coding/naming/functions.md
    - ../../standards/coding/naming/types.md
    - ../../standards/coding/naming/files.md
    
    **For Testing Agent (@ava-thompson-testing-evangelist)**:
    - ../../standards/coding/testing.md
    - ../../standards/coding/general-principles.md
    
    **For Documentation Agent (@sam-taylor-documentation)**:
    - ../../standards/coding/documentation.md
    - ../../standards/coding/general-principles.md
    
    **For Security Agent (@nina-petrov-security-champion)**:
    - ../../standards/coding/general-principles.md
    - ../../standards/coding/environment-variables.md
    
    **For Linting Agent (@alex-chen-linting-specialist)**:
    - ../../standards/coding/general-principles.md
    
    **Assignment**
    You're assigned to review the provided code files for issues in your domain of expertise.
    
    **Steps**
    
    **For Code Quality Agent**:
    1. Check code structure and organization against standards
    2. Validate naming conventions per naming standards
    3. Review complexity metrics and suggest refactoring
    4. Check for code duplication and DRY violations
    5. Verify error handling patterns
    6. Review performance considerations
    
    **For Testing Agent**:
    1. Analyze test coverage metrics against minimum requirements
    2. Review test structure and organization per standards
    3. Check for missing test scenarios and edge cases
    4. Validate test assertions and expectations
    5. Review mock usage and test isolation
    6. Check integration test coverage
    
    **For Documentation Agent**:
    1. Check inline code comments per documentation standards
    2. Review function/method documentation completeness
    3. Validate README updates if applicable
    4. Check API documentation accuracy
    5. Review type definitions and interfaces
    6. Verify example usage and clarity
    
    **For Security Agent**:
    1. Check for injection vulnerabilities (SQL, XSS, etc.)
    2. Review authentication/authorization implementation
    3. Validate input sanitization and validation
    4. Check for sensitive data exposure in logs/responses
    5. Review dependency security and known vulnerabilities
    6. Check CORS configuration and security headers
    
    **For Linting Agent**:
    1. Identify project meta files (package.json) at project and monorepo levels
    2. Extract linting scripts from meta files (e.g., lint, lint:fix, eslint, tslint)
    3. Map appropriate linting scripts to each file group based on file types
    4. Prefer project-level scripts over monorepo-level scripts when available
    5. Execute relevant linting scripts and capture output
    6. Report all linting issues found by the tools (DO NOT read config files)
    7. Provide summary of linting results per file group
    
    **Report**
    Provide findings in YAML format:
    
    ```yaml
    agent: [agent_name]
    status: [pass|warning|fail]
    findings:
      critical:
        - issue: "Description"
          file: "path/to/file"
          line: 123
          recommendation: "How to fix"
      warnings:
        - issue: "Description"
          file: "path/to/file"
          recommendation: "Improvement suggestion"
      passed:
        - "What was done well"
    metrics:
      [relevant metrics for your domain]
    ```
    <<<

#### Phase 3: Consolidation (You)

**Goal**: Consolidate all review feedback and generate final report

**Steps:**

1. **Collect All Reports**
   - Gather reports from all 5 agents
   - Validate report completeness
   - Check for conflicting findings

2. **Prioritize Issues**
   - Critical: Must fix immediately
   - Major: Should fix before proceeding
   - Minor: Can fix in follow-up
   - Suggestions: Optional improvements

3. **Generate Consolidated Report**

   ```yaml
   code_review:
     review_type: "[pr|codebase|files]"
     identifier: "[pr_number|path|description]"
     status: "[pass|requires_changes|fail]"
     
     critical_issues:
       - category: "security"
         description: "SQL injection vulnerability"
         file: "src/api/users.ts"
         line: 45
         recommendation: "Use parameterized queries"
         
     major_issues:
       - category: "testing"
         description: "Missing test coverage"
         file: "src/services/auth.ts"
         coverage: "65%"
         recommendation: "Add unit tests for error cases"
       - category: "linting"
         description: "ESLint violations found"
         file: "src/components/Button.tsx"
         issues: ["prefer-const", "no-unused-vars"]
         recommendation: "Fix linting violations using automated tools"
         
     minor_issues:
       - category: "documentation"
         description: "Missing JSDoc comments"
         files: ["src/utils/helpers.ts"]
         recommendation: "Add function documentation"
         
     suggestions:
       - category: "performance"
         description: "Consider caching for repeated queries"
         file: "src/api/data.ts"
         
     metrics:
       test_coverage: "78%"
       documentation_coverage: "85%"
       complexity_score: "B"
       security_score: "A-"
       files_reviewed: 15
       issues_found: 8
   ```

4. **Create Action Items**
   - List required fixes by priority
   - Provide clear remediation steps
   - Suggest implementation order

## Output

**Success Criteria:**

- All files reviewed by appropriate agents (5 specialized agents)
- Critical issues identified and documented
- Comprehensive report generated including linting analysis
- Clear action items provided

**Deliverables:**

1. Consolidated review report in YAML format
2. Prioritized list of issues
3. Remediation recommendations
4. Review metrics summary
