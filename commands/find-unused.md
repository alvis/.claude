---
allowed-tools: Read, Glob, Grep, Task, mcp__lsmcp__search_symbol_from_index, mcp__lsmcp__get_document_symbols, mcp__lsmcp__find_references, mcp__lsmcp__get_definitions, mcp__lsmcp__index_symbols, mcp__lsmcp__get_project_overview
argument-hint: [path/to/scan] [--exclude=pattern]
description: Identify commented-out code and unused symbols using LSP analysis
---

# Find Unused Code

Analyzes $ARGUMENTS to identify commented-out code and unused private/exported symbols not used internally or reachable in the export path declared in package.json.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Modify or delete any code
- Analyze external dependencies
- Check for dead code in test files
- Analyze non-TypeScript/JavaScript files

**When to REJECT:**

- Path does not exist
- Path is outside the project directory
- No package.json found for export analysis
- LSP indexing fails

## 📊 Dynamic Context

- **[IMPORTANT]** You must carefully remember all the context defined below

### System State

- Current branch: !`git branch --show-current`
- Working directory: !`pwd`

### Project Context

- Workflows: !`find "$(git rev-parse --show-toplevel)/constitutions/workflows" "$HOME/.claude/constitutions/workflows" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No workflows found"`
- Standards: !`find "$(git rev-parse --show-toplevel)/constitutions/standards" "$HOME/.claude/constitutions/standards" -type f -name '*.md' 2>/dev/null | sed "s|^$(pwd)/||" || echo "No standards found"`

## 🔄 Workflow

### Phase 1: Planning

1. **Analyze Requirements**
   - Parse $ARGUMENTS to get target path
   - Verify path exists and is within project
   - Identify file types to analyze (.ts, .tsx, .js, .jsx)
   - Locate package.json for export analysis

2. **Identify Applicable Workflows & Standards**
   - Review code quality standards
   - Check coding conventions for dead code handling
   - Note any project-specific exclusion patterns

3. **Delegation Decision**
   - Split into 2 parallel subtasks:
     - Subtask 1: Search for commented-out code patterns
     - Subtask 2: Use LSP to identify unused/unreachable symbols
   - Both agents work independently and report findings

4. **Risk Assessment**
   - No code modifications (read-only analysis)
   - May have false positives for dynamic imports
   - LSP indexing may take time for large codebases

### Phase 2: Execution

1. **Workflow Compliance**
   - Follow code analysis patterns
   - Respect gitignore and project exclusions
   - Use appropriate tools for each subtask

2. **Primary Implementation**
   - Launch 2 parallel agents using Task tool:

     **Agent 1: Commented Code Finder**
     - Search for common comment patterns:
       - Single-line: `//` followed by code patterns
       - Multi-line: `/* ... */` containing code
       - JSX comments: `{/* ... */}`
     - Identify patterns like:
       - Commented function declarations
       - Commented imports
       - Commented class definitions
       - Commented variable declarations

     **Agent 2: Unused Symbol Detector**
     - Index symbols using LSP if not already indexed
     - Identify all private symbols (not exported)
     - Check if private symbols are referenced
     - For exported symbols:
       - Check internal usage
       - Verify reachability from package.json exports
     - Flag symbols with zero references

3. **Standards Enforcement**
   - Report findings in structured format
   - Group by file and category
   - Provide actionable insights

4. **Edge Case Handling**
   - Handle mixed comment styles
   - Account for JSDoc comments (not dead code)
   - Recognize intentional code examples in comments
   - Handle dynamic imports and lazy loading

### Phase 3: Verification

1. **Workflow-Based Verification**
   - Merge reports from both agents
   - Remove duplicates and false positives
   - Validate findings against known patterns

2. **Automated Testing**
   - Verify all reported files exist
   - Confirm line numbers are accurate
   - Cross-reference with git history if needed

3. **Quality Assurance**
   - Filter out test files if excluded
   - Remove vendor/node_modules findings
   - Validate export path analysis

4. **Side Effect Validation**
   - Confirm no files were modified
   - Verify LSP index is up-to-date
   - Check memory usage for large analyses

### Phase 4: Reporting

**Output Format:**

```
[✅/❌] Command: $ARGUMENTS

## Summary
- Files analyzed: [count]
- Commented code blocks: [count]
- Unused private symbols: [count]
- Unreachable exports: [count]

## Commented-Out Code
### [file-path]
- Line [X-Y]: [Type of code] - [Brief description]

## Unused Private Symbols
### [file-path]
- Line [X]: [Symbol type] '[name]' - Never referenced

## Unreachable Exports
### [file-path]
- Line [X]: Export '[name]' - Not in package.json exports
- Line [Y]: Export '[name]' - Not used internally

## Recommendations
- Consider removing [X] blocks of commented code
- Review [Y] unused private symbols for deletion
- Update package.json exports or remove [Z] unreachable exports

## Next Steps
- Review findings with team
- Create cleanup tickets if needed
- Update export configuration
```

## 📝 Examples

### Basic Directory Analysis

```bash
/find-unused "src/"
# Analyzes all files in src/ directory
# Returns commented code and unused symbols
```

### Specific File Analysis

```bash
/find-unused "src/components/Button.tsx"
# Analyzes single file for unused code
# Useful for focused cleanup
```

### Library Package Analysis

```bash
/find-unused "packages/ui-library"
# Analyzes library package
# Checks exports against package.json
# Identifies unreachable public APIs
```

### With Exclusion Patterns

```bash
/find-unused "src/" --exclude="*.test.ts"
# Analyzes src/ excluding test files
# Focuses on production code only
```

### Large Codebase Analysis

```bash
/find-unused "."
# Analyzes entire project
# May take longer for indexing
# Comprehensive dead code report
```
