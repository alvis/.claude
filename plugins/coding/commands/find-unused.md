---
allowed-tools: Bash, Read, Glob, Grep, Task, mcp__plugin_coding_lsmcp__search_symbols, mcp__plugin_coding_lsmcp__lsp_get_document_symbols, mcp__plugin_coding_lsmcp__lsp_find_references, mcp__plugin_coding_lsmcp__lsp_get_definitions, mcp__plugin_coding_lsmcp__lsp_get_diagnostics, mcp__plugin_coding_lsmcp__get_project_overview
argument-hint: [path/to/scan] [--exclude=pattern]
description: Identify commented-out code and unused symbols using graph-based LSP analysis
---

# Find Unused Code

Analyzes $ARGUMENTS to identify commented-out code and unused symbols using graph-based analysis. Symbols are considered used if they are referenced internally or reachable via exports in package.json (including subpath exports). Detects both 1st-degree unused symbols and 2nd-degree unused symbols (symbols only used by unused code).

## 🎯 Purpose & Scope

**What this command does NOT do**:

- Modify or delete any code
- Analyze external dependencies
- Analyze non-TypeScript/JavaScript files
- Remove or modify any symbols automatically

**When to REJECT**:

- Path does not exist
- Path is outside the project directory
- No package.json found for export analysis
- LSP indexing fails

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Planning

1. **Analyze Requirements**
   - Parse $ARGUMENTS to get target path (default: current working path)
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
     - Subtask 2: Build symbol graph and identify unused/unreachable symbols
   - Both agents work independently and report findings
   - Graph analysis enables detection of 2nd-degree unused symbols

4. **Risk Assessment**
   - No code modifications (read-only analysis)
   - May have false positives for dynamic imports
   - LSP indexing may take time for large codebases
   - Symbol graph construction requires memory for large codebases
   - Graph traversal complexity increases with codebase size

### Step 2: Execution

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
     - Build symbol dependency graph (JSON structure):
       - Extract all symbols from source files (functions, variables, types)
       - Extract all symbols from test files separately
       - Create nodes for each symbol with metadata (type, location, scope)
       - Create edges representing usage relationships (symbol A uses symbol B)
       - Store graph temporarily for analysis
     - Analyze source file symbols:
       - Check if used internally (has incoming edges from other source symbols)
       - For exported symbols: verify reachability via package.json exports (including subpath exports)
       - Mark as 1st-degree unused if: not used internally AND (not exported OR not reachable in exports)
     - Analyze test file symbols:
       - Check if used within test files (has incoming edges from other test symbols)
       - Mark as 1st-degree unused if not referenced in test files
     - Detect 2nd-degree unused symbols:
       - Traverse graph to find symbols only referenced by 1st-degree unused symbols
       - These would become unused if 1st-degree unused symbols are removed
       - Mark dependency chains for reporting
     - Optionally execute analysis code:
       - Run programmatic graph traversal to validate findings
       - Use automated algorithms to confirm unused symbol detection

3. **Standards Enforcement**
   - Report findings in structured format
   - Group by file and category
   - Provide actionable insights

4. **Edge Case Handling**
   - Handle mixed comment styles
   - Account for JSDoc comments (not dead code)
   - Recognize intentional code examples in comments
   - Handle dynamic imports and lazy loading

### Step 3: Verification

1. **Workflow-Based Verification**
   - Merge reports from both agents
   - Remove duplicates and false positives
   - Validate findings against known patterns

2. **Graph Validation**
   - Verify symbol graph structure integrity
   - Confirm all edges have valid source and target nodes
   - Validate 2nd-degree unused detection accuracy
   - Check for circular dependencies that might affect analysis
   - Ensure test file symbols are properly isolated from source symbols

3. **Automated Testing**
   - Verify all reported files exist
   - Confirm line numbers are accurate
   - Cross-reference with git history if needed
   - Validate export declarations match package.json

4. **Quality Assurance**
   - Filter out vendor/node_modules findings
   - Validate export path analysis (including subpath exports)
   - Confirm 1st and 2nd-degree classifications are correct

5. **Side Effect Validation**
   - Confirm no files were modified
   - Verify LSP index is up-to-date
   - Check memory usage for graph construction
   - Ensure temporary graph files are handled properly

### Step 4: Reporting

**Output Format**:

```text
[✅/❌] Command: $ARGUMENTS

## Summary
- Files analyzed: [count]
- Commented code blocks: [count]
- 1st-degree unused symbols: [count]
- 2nd-degree unused symbols: [count]
- Unreachable exports: [count]
- Test file unused symbols: [count]

## Commented-Out Code
### [file-path]
- Line [X-Y]: [Type of code] - [Brief description]

## 1st-Degree Unused Symbols
### [file-path]
- Line [X]: [Symbol type] '[name]' - Not used internally, not in exports
- Line [Y]: [Symbol type] '[name]' - Not referenced anywhere

## 2nd-Degree Unused Symbols (only used by unused code)
### [file-path]
- Line [X]: [Symbol type] '[name]' - Only used by: [unused-symbol-1], [unused-symbol-2]
- Line [Y]: [Symbol type] '[name]' - Only used by: [unused-symbol-3]

## Unreachable Exports
### [file-path]
- Line [X]: Export '[name]' - Not in package.json exports (including subpath exports)
- Line [Y]: Export '[name]' - Not used internally and not in exports

## Test File Unused Symbols
### [file-path]
- Line [X]: [Symbol type] '[name]' - Not used within test files

## Recommendations
- Consider removing [X] blocks of commented code
- Review [Y] 1st-degree unused symbols for deletion
- After removing 1st-degree symbols, [Z] 2nd-degree symbols will also become removable
- Update package.json exports or remove [W] unreachable exports
- Clean up [V] unused test symbols

## Next Steps
- Review findings with team
- Create cleanup tickets prioritizing 1st-degree unused symbols
- Update export configuration for unreachable exports
- Consider cascading cleanup for 2nd-degree unused symbols
```

## 📝 Examples

### Basic Directory Analysis

```bash
/find-unused "src/"
# Builds symbol dependency graph for src/ directory
# Returns commented code, 1st-degree and 2nd-degree unused symbols
# Includes test file analysis
```

### Specific File Analysis

```bash
/find-unused "src/components/Button.tsx"
# Analyzes single file with graph-based detection
# Shows which unused symbols would cascade to other symbols
# Useful for focused cleanup
```

### Library Package Analysis

```bash
/find-unused "packages/ui-library"
# Analyzes library package with export path validation
# Checks exports against package.json (including subpath exports)
# Identifies unreachable public APIs
# Shows 2nd-degree unused symbols that depend on unused exports
```

### With Exclusion Patterns

```bash
/find-unused "src/" --exclude="*.test.ts"
# Analyzes src/ excluding test files
# Graph-based analysis of production code only
# Still checks export reachability in package.json
```

### Large Codebase Analysis

```bash
/find-unused "."
# Analyzes entire project with full symbol graph
# May take longer for graph construction and indexing
# Comprehensive report with cascading unused symbol detection
# Shows complete dependency chains for cleanup planning
```
