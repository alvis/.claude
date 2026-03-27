---
name: modernize
description: >-
  Analyze project configuration and upgrade code to use the latest supported
  syntax, APIs, and patterns. Use when adopting new language features, upgrading
  runtime versions, or ensuring code uses modern idioms the project supports.
model: opus
context: fork
agent: general-purpose
allowed-tools: Bash, Read, Write, MultiEdit, Edit, Glob, Grep, Task
argument-hint: <area> [--dry-run] [--target-version=X.Y]
---

# Modernize

Analyze project configuration and upgrade code to use the latest supported syntax, APIs, and patterns. Features are discovered at runtime from the reference catalog and filtered by the project's actual TypeScript/Node.js version.

## Arguments

- **area** (positional, required): File path, directory, or glob pattern selecting which files to modernize.
- **--dry-run** (optional): Report what would change without applying any edits.
- **--target-version** (optional): Override the detected TypeScript version (e.g., `--target-version=5.4`). Useful for previewing upgrades before bumping the project version.

## 🎯 Purpose & Scope

**What this command does**:

- Detects the project's TypeScript version, tsconfig targets, and Node.js engine version
- Identifies legacy patterns that can be replaced with modern equivalents the project already supports
- Applies safe, mechanical transforms (pattern-for-pattern replacements)

**What this command does NOT do**:

- Does not upgrade `package.json` dependencies or TypeScript version
- Does not modify configuration files (tsconfig.json, eslintrc, etc.)
- Does not introduce new dependencies
- Does not refactor architecture or business logic
- Does not process binary files or non-code assets
- Does not modify gitignored or vendor files

**When to REJECT**:

- Target is a configuration file
- No valid source files found in the specified area
- Target is outside the project directory
- No applicable modernization features for the detected version

## 🔄 Workflow

ultrathink: you'd perform the following steps

### Step 1: Detect Config

Read the project's `tsconfig.json` and `package.json` to determine the modernization ceiling:

1. **TypeScript version**: Extract from `devDependencies.typescript` or `dependencies.typescript` in `package.json`. Strip range prefixes (`^`, `~`) to get the base version.
2. **Compiler options**: Read `target`, `module`, and `lib` from `tsconfig.json` `compilerOptions`. Follow `extends` if present to resolve the full effective config.
3. **Node.js engine version**: Extract from `package.json` `engines.node` field. Strip range prefixes to get the minimum supported version.

If `--target-version` is provided, use that instead of the detected TypeScript version.

Record these values — they gate which features are applicable in Step 2.

### Step 2: Load Reference

Read the feature reference catalog at `references/typescript.md` (relative to this skill's directory).

Filter entries to only those whose required TypeScript version is ≤ the version detected (or overridden) in Step 1. Discard features that require a higher version than the project supports.

The reference file uses a compact one-line-per-feature format with `use xxx` entries. Each entry points to a corresponding example file for detection patterns and transforms.

### Step 3: Load Examples

For each applicable feature from Step 2, read the corresponding example file at `examples/typescript/<name>.md` (relative to this skill's directory). Example filenames are prefixed with the version they were introduced in (e.g., `ts50-tc39-decorators.md`).

Each example file contains:

- **Detection patterns**: Grep-compatible regex patterns that identify legacy code eligible for the transform
- **Before/after transforms**: Concrete code showing the old pattern and its modern replacement
- **Edge cases**: Situations where the transform should NOT be applied

Collect all detection patterns and their associated transforms.

### Step 4: Scan

Using the detection patterns from Step 3, grep the target files for legacy patterns:

1. For each applicable feature, run Grep with the detection pattern against the target area
2. Collect all matches with file paths, line numbers, and matched content
3. Cross-reference with edge cases — exclude matches that fall under documented exceptions
4. Group results by feature for organized reporting and application

If no matches are found, report that the target files are already using modern patterns and exit.

### Step 5: Apply

**If `--dry-run` is NOT set**:

1. For each match found in Step 4, apply the corresponding transform using the Edit tool
2. Process files one at a time to avoid conflicts between overlapping edits
3. After all edits are complete:
   - Run `npx tsc --noEmit` to verify no type errors were introduced
   - Run project tests via `npm test` (or the appropriate test script from `package.json`)
4. If verification fails:
   - Identify which transform caused the failure
   - Revert that specific transform
   - Add it to the "skipped" list with reason "verification failed"
   - Re-run verification to confirm the revert resolved the issue

**If `--dry-run` IS set**:

- Do NOT apply any edits
- For each match, report: file path, line number, current pattern, proposed replacement, and the feature that motivated the change
- Skip verification steps entirely

### Step 6: Report

Output a structured summary:

```
[✅/❌] Command: modernize $ARGUMENTS

## Configuration Detected
- TypeScript: [version]
- Target: [target]
- Module: [module]
- Node.js: [version]
- Features applicable: [count] of [total] in catalog

## Changes Applied
| File | Line | Feature | Description |
|------|------|---------|-------------|
| src/utils/foo.ts | 42 | using-declarations | Replaced manual cleanup with `using` |
| ... | ... | ... | ... |

## Changes Skipped
| File | Line | Feature | Reason |
|------|------|---------|--------|
| src/lib/bar.ts | 15 | satisfies-operator | Edge case: computed property |
| ... | ... | ... | ... |

## Manual Review Needed
- [file:line] — [description of what needs human judgment]

## Verification
- Type check: [PASS/FAIL]
- Tests: [PASS/FAIL]
```

If `--dry-run` was set, replace "Changes Applied" with "Changes Proposed" and omit the Verification section.

## 📝 Examples

### Modernize a Directory

```bash
/modernize src/services/
# Detects TS 5.4, scans services for legacy patterns,
# applies transforms, verifies with tsc and tests
```

### Dry Run to Preview Changes

```bash
/modernize src/ --dry-run
# Reports all modernization opportunities without applying any edits
```

### Target a Specific Version

```bash
/modernize src/utils/ --target-version=5.2
# Only applies features available in TS 5.2, even if project uses 5.4
```

### Single File

```bash
/modernize src/components/Button.tsx
# Modernizes a single file
```
