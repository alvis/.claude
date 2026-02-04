---
allowed-tools: Bash, Read, Glob, Grep, Task, LSP
argument-hint: [path/to/scan] [--exclude=pattern]
description: Identify commented-out code, unused symbols, and unused test helpers using LSP-based analysis
---

# Find Unused Code

Analyzes $ARGUMENTS to identify commented-out code, unused symbols, unreachable production files, production code only used by tests, and unused test helpers. Uses LSP operations for efficient symbol analysis with a hierarchical approach (file-level → symbol-level). Detects 1st-degree unused symbols, 2nd-degree unused symbols (symbols only used by unused code), test-only production code, and orphaned test utilities.

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
- LSP server unavailable or fails to respond

## 🔧 LSP Operations Reference

| Detection Task | LSP Operation | Description |
| -------------- | ------------- | ----------- |
| Enumerate symbols in a file | `documentSymbol` | Get all functions, classes, variables in a document |
| Find if symbol is used | `findReferences` | Find all references to a symbol |
| Trace call chains (2nd-degree) | `incomingCalls` / `outgoingCalls` | Find callers/callees of a function |
| Search symbols across workspace | `workspaceSymbol` | Find symbols matching a query across all files |
| Find symbol definitions | `goToDefinition` | Navigate to where a symbol is defined |
| Find implementations | `goToImplementation` | Find implementations of interfaces/abstract methods |

### Reference Classification (Critical)

When using `findReferences`, classify each reference by its context:

| Reference Type | Counts as Usage? | Example |
| -------------- | ---------------- | ------- |
| Function call | ✅ Yes | `myFunction()` |
| Class instantiation | ✅ Yes | `new MyClass()` |
| Variable read | ✅ Yes | `const x = myVar` |
| Property access | ✅ Yes | `obj.myMethod()` |
| Type annotation | ✅ Yes | `const x: MyType` |
| Export statement | ❌ No | `export { myFunc }` |
| Re-export | ❌ No | `export * from './mod'` |
| Import statement | ❌ No | `import { x } from './y'` |
| Type-only import | ❌ No | `import type { X }` |
| Definition itself | ❌ No | `function myFunc() {}` |

**A symbol is UNUSED if `findReferences` returns ONLY non-usage references (definition, exports, imports).**

## 📋 Test File Detection Strategy

**Config-based detection with convention fallback:**

1. **Try to read test patterns from config files** (in order of preference):
   - `jest.config.js/ts` → `testMatch`, `testPathIgnorePatterns`
   - `vitest.config.js/ts` → `include`, `exclude` patterns
   - `package.json` → `jest.testMatch`

2. **If no config found, use conventions:**
   - Test files: `**/*.spec.ts`, `**/*.test.ts`, `**/*.spec.*.ts`, `**/*.test.*.ts`, `__tests__/**`, `test/**`
   - Production: Everything else in `src/**`

### Test Helper Identification

Test helpers are identified by deriving their location from test file patterns:

1. **Test folders**: Any folder containing files matching test patterns (e.g., `*.spec.ts`, `*.test.ts`)
2. **Test helpers**: Non-test files within test folders
3. **Exception**: For co-located tests (test files alongside source files like `src/foo.spec.ts`), other files in that folder are treated as production code (covered by Phase 2)

**Common helper patterns** (for symbol-level detection):

- Functions: `createMock*`, `build*`, `make*`, `*Factory`, `*Helper`
- Constants: `MOCK_*`, `TEST_*`, `mock*`, `fake*`

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Planning

1. **Analyze Requirements**
   - Parse $ARGUMENTS to get target path (default: current working path)
   - Verify path exists and is within project
   - Identify file types to analyze (.ts, .tsx, .js, .jsx)
   - Locate package.json for export analysis (including subpath exports)
   - Detect test file patterns using config-based strategy

2. **Identify Applicable Workflows & Standards**
   - Review code quality standards
   - Check coding conventions for dead code handling
   - Note any project-specific exclusion patterns

3. **Delegation Decision**
   - Split into 3 parallel subtasks:
     - Agent 1: Search for commented-out code patterns
     - Agent 2: Hierarchical unused symbol detection (file-level → symbol-level)
     - Agent 3: Test-only production code detection
   - All agents work independently and report findings
   - Hierarchical analysis enables efficient large codebase handling

4. **Risk Assessment**
   - No code modifications (read-only analysis)
   - May have false positives for dynamic imports
   - LSP operations may take time for large codebases
   - Test-only detection may have false positives for intentional test utilities

### Step 2: Execution

1. **Workflow Compliance**
   - Follow code analysis patterns
   - Respect gitignore and project exclusions
   - Use appropriate tools for each subtask

2. **Primary Implementation**
   - Launch 3 parallel agents using Task tool:

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

     **Agent 2: Unused Symbol Detector (Hierarchical LSP-Based)**

     _Phase 1: File-Level Analysis (Unreachable Production Files)_

     1. Parse package.json exports (including subpath exports like `"./utils"`):
        - Main entry: `"main"`, `"module"`, `"exports"`
        - Subpath exports: `"./foo"`, `"./bar/*"`
     2. Use `workspaceSymbol` to find all exported entry points
     3. Build file reachability graph from exports:
        - Start from exported files as roots
        - Trace imports to find all reachable production files
        - Use `findReferences` on each file's exports to trace importers
     4. Identify UNREACHABLE files:
        - Production files NOT imported by any reachable file
        - These entire files are potentially dead code
        → Report: "Unreachable Production Files"

     _Phase 2: Symbol-Level Analysis (on reachable files only)_

     1. For each REACHABLE production file:
        - Use `documentSymbol` to get all symbols (functions, classes, variables, types)
     2. For each symbol:
        - Use `findReferences` to get all references
        - **IMPORTANT**: Filter references to find ACTUAL USAGE only:
          - ✅ Counts as usage: function calls, class instantiations, variable reads, type annotations in code
          - ❌ Does NOT count as usage: export statements, re-exports, type-only imports
        - If no actual usage references found → 1st-degree unused
     3. For 2nd-degree detection:
        - Use `incomingCalls` on 1st-degree unused functions
        - Find symbols only called by unused code
        - Mark dependency chains for reporting

     _Phase 3: Test Code Analysis (Unused Test Helpers)_

     1. Identify test helper files using "Test Helper Identification" logic:
        - Find test folders (folders containing files matching test patterns)
        - Non-test files within test folders are test helpers
        - Skip co-located test scenarios (handled by Phase 2)
     2. For each test helper file:
        - Use `documentSymbol` to get all exported symbols
        - Use `findReferences` for each symbol
        - Apply same ACTUAL USAGE filtering as Phase 2
     3. Classify unused test symbols:
        - **Unused fixture**: No test imports or uses it
        - **Unused helper function**: Defined but never called by any test
        - **Unused mock**: Mock factory never invoked
        → Report: "Unused Test Helpers"

     **Agent 3: Test-Only Production Code Detector**

     _Detection Algorithm:_

     1. For each symbol in production files:
        - Use `findReferences` to get all usages
        - Classify each reference location:
          - **Production**: Files NOT matching test patterns
          - **Test**: Files matching test patterns (from config or conventions)

     2. If ALL references are in test files, classify the symbol:

        **A. Test Helper Pattern** → Recommend MOVE to test fixtures:
        - Name contains: `mock`, `stub`, `fake`, `fixture`, `helper`, `factory`, `builder`
        - Pattern matches: `createMock*`, `build*`, `make*Factory`, `*TestHelper`, `*TestUtils`
        - Is a small utility (< 20 lines)
        - Returns test data or mocks

        **B. Dead Tested Code** → Recommend REMOVE entirely:
        - Is a class, service, or substantial function
        - Is directly tested (imported in test files)
        - Has NO production callers
        - Examples: Features tested but never integrated, classes never instantiated in prod

3. **Standards Enforcement**
   - Report findings in structured format
   - Group by file and category
   - Provide actionable insights with specific recommendations

4. **Edge Case Handling**
   - Handle mixed comment styles
   - Account for JSDoc comments (not dead code)
   - Recognize intentional code examples in comments
   - Handle dynamic imports and lazy loading
   - Account for type-only exports (may be used at compile time)
   - Consider reflection and string-based access patterns
   - Handle re-exports and barrel files

### Step 3: Verification

1. **Workflow-Based Verification**
   - Merge reports from all agents
   - Remove duplicates and false positives
   - Validate findings against known patterns

2. **LSP Response Validation**
   - Verify LSP operations return valid responses
   - Confirm `documentSymbol` returns expected symbol types
   - Validate `findReferences` includes all reference locations
   - Check `incomingCalls`/`outgoingCalls` for completeness
   - Ensure `workspaceSymbol` covers all entry points

3. **Graph Validation**
   - Verify file reachability graph from package.json exports
   - Confirm all edges have valid source and target
   - Validate 2nd-degree unused detection accuracy
   - Check for circular dependencies that might affect analysis
   - Ensure test file symbols are properly isolated from source symbols

4. **Test-Only Detection Validation**
   - Verify test file pattern detection is accurate
   - Confirm classification heuristics are applied correctly
   - Check for false positives (intentional test utilities in src/)
   - Validate helper vs dead code classification

5. **Automated Testing**
   - Verify all reported files exist
   - Confirm line numbers are accurate
   - Cross-reference with git history if needed
   - Validate export declarations match package.json

6. **Quality Assurance**
   - Filter out vendor/node_modules findings
   - Validate export path analysis (including subpath exports)
   - Confirm 1st and 2nd-degree classifications are correct

7. **Side Effect Validation**
   - Confirm no files were modified
   - Verify LSP server state is clean
   - Check memory usage for large codebases

### Step 4: Reporting

**Output Format**:

```text
[✅/❌] Command: $ARGUMENTS

## Summary
- Files analyzed: [count]
- Unreachable production files: [count]
- Commented code blocks: [count]
- 1st-degree unused symbols: [count]
- 2nd-degree unused symbols: [count]
- Unreachable exports: [count]
- Test-only production symbols: [count]
  - Test helpers to move: [count]
  - Dead tested code to remove: [count]
- Unused test helpers: [count]

## Unreachable Production Files
Files not exported via package.json and not imported by any reachable file.
These entire files are dead code.

### [file-path]
- Not exported in package.json
- Not imported by any reachable production file
- Contains [X] symbols
→ Suggest: Remove entire file or add to package.json exports

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

## Production Code Only Used in Tests

### Test Helpers (Move to Fixtures)
### [file-path]
- Line [X]: function 'createMockUser' - Only used in: user.test.ts, auth.test.ts
  → Suggested location: __tests__/fixtures/user.fixture.ts
- Line [Y]: function 'buildTestData' - Only used in: data.test.ts
  → Suggested location: __tests__/helpers/data.helper.ts

### Dead Tested Code (Remove)
### [file-path]
- Line [X]: class 'LegacyProcessor' - Tested in processor.test.ts but never used in production
  → Suggest: Remove class AND its tests (testing unused code)
- Line [Y]: function 'unusedFeature' - Tested but no production callers
  → Suggest: Remove function AND tests

## Unused Test Helpers
Helpers, fixtures, and utilities in test code that are never used by any test.

### [file-path] (e.g., __tests__/helpers/user.helper.ts)
- Line [X]: function 'createMockUser' - Defined but never called in any test
  → Suggest: Remove unused helper
- Line [Y]: constant 'MOCK_USER_DATA' - Exported but never imported
  → Suggest: Remove unused fixture
- Line [Z]: function 'buildTestOrder' - Was used but all consuming tests were deleted
  → Suggest: Remove orphaned helper

## Recommendations
- Consider removing [X] blocks of commented code
- Remove [A] unreachable production files (entire files are dead code)
- Review [Y] 1st-degree unused symbols for deletion
- After removing 1st-degree symbols, [Z] 2nd-degree symbols will also become removable
- Update package.json exports or remove [W] unreachable exports
- Move [M] test helpers to test fixtures
- Remove [N] dead tested code along with their tests
- Clean up [T] unused test helpers (orphaned fixtures, mocks, and utilities)

## Next Steps
- Review findings with team
- Start cleanup with unreachable files (biggest impact)
- Create cleanup tickets prioritizing 1st-degree unused symbols
- Update export configuration for unreachable exports
- Consider cascading cleanup for 2nd-degree unused symbols
- Relocate test helpers to proper fixture directories
- Remove dead tested code and associated tests
- Clean up unused test helpers to reduce test maintenance burden
```

## 📝 Examples

### Basic Directory Analysis

```bash
/find-unused "src/"
# Phase 1: Identifies unreachable production files via package.json exports
# Phase 2: LSP-based symbol analysis on reachable files only
# Returns commented code, unused symbols, and test-only production code
```

### Specific File Analysis

```bash
/find-unused "src/components/Button.tsx"
# Analyzes single file with LSP-based detection
# Uses findReferences to check each symbol's usage
# Shows which unused symbols would cascade to other symbols
```

### Library Package Analysis

```bash
/find-unused "packages/ui-library"
# Phase 1: Maps package.json exports (including subpath exports)
# Identifies files not reachable from any export
# Phase 2: Symbol-level analysis on reachable files
# Detects test helpers that should be in fixtures
```

### With Exclusion Patterns

```bash
/find-unused "src/" --exclude="*.test.ts"
# Analyzes src/ excluding test files from scan
# Still uses test patterns to detect test-only production code
# Checks export reachability in package.json
```

### Large Codebase Analysis

```bash
/find-unused "."
# Hierarchical approach handles large codebases efficiently
# Phase 1: Quick file-level analysis filters out unreachable files
# Phase 2: Symbol analysis only on reachable subset
# Comprehensive report with cascading cleanup recommendations
```

### Test-Only Detection Focus

```bash
/find-unused "src/" --focus=test-only
# Specifically looks for production code only used by tests
# Identifies test helpers that should be moved to fixtures
# Finds dead code that is being tested but never used
```

### Test Directory Analysis

```bash
/find-unused "spec/"
# Phase 3: Analyzes test directory for unused helpers and fixtures
# Identifies orphaned test utilities that no test imports
# Finds unused mocks, factories, and helper functions
# Useful for cleaning up test code debt
```

## ⚠️ Edge Cases & Limitations

### Dynamic Imports

- Symbols imported via `import()` may not be detected as used
- String-based dynamic imports (`import(variable)`) cannot be analyzed
- **Mitigation**: Check for dynamic import patterns before marking as unused

### Type-Only Exports

- TypeScript type exports may show as "unused" at runtime
- Types used only for declaration merging may appear unused
- **Mitigation**: Distinguish between value and type exports

### Reflection & String Access

- `object[propertyName]` access patterns hide usage
- `Object.keys()` iteration may use symbols indirectly
- **Mitigation**: Flag symbols in files with heavy reflection

### Re-exports & Barrel Files

- `export * from './module'` re-exports all symbols
- Barrel files (`index.ts`) may mask actual usage
- **Mitigation**: Trace through re-exports to find actual usage

### Test Utilities in Production

- Some projects intentionally keep test helpers in `src/`
- Factory patterns may be used in both prod and test
- **Mitigation**: Check for explicit `@testOnly` annotations or config

### Conditional Exports

- Platform-specific exports (`"browser"`, `"node"`) may vary
- Conditional exports in package.json need full parsing
- **Mitigation**: Analyze all export conditions
