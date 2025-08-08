---
allowed-tools: Bash, Edit, MultiEdit, Read, Write, Grep, Glob, Task
argument-hint: <error message or context>
description: Diagnose and fix CI/husky hook failures with systematic debugging
---

# Fix Husky Hook Failures

Diagnose and systematically fix CI/husky hook failures. When $ARGUMENTS contains an error message or failure context, analyze and resolve the issue following a structured debugging protocol.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Make commits (only stages fixes)
- Skip type checking or tests
- Ignore root causes
- Apply quick fixes without understanding

**When to REJECT:**

- No actual CI/husky failure exists
- Manual intervention explicitly required
- Security-sensitive hooks failing
- Production deployment hooks

## 📊 Dynamic Context

### System State

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Staged files: !`git diff --cached --name-only`
- Recent commits: !`git log --oneline -5`

### Project Context

- Available test commands: !`grep -E '"(test|lint|typecheck|format)"' package.json | head -5`
- Husky hooks: !`ls .husky 2>/dev/null || echo "No husky directory found"`

## 🔄 Workflow

### Phase 1: Planning

1. **Analyze Requirements**
   - Parse error messages from $ARGUMENTS
   - Identify which hook failed (pre-commit, pre-push, etc.)
   - Determine scope of failure

2. **Root Cause Analysis**
   - Examine relevant source code
   - Review test logs and error traces
   - Add console.logs if needed for diagnosis
   - Document evidence supporting hypothesis

3. **Delegation Decision**
   - Use test-runner agent for test execution
   - Consider marcus-williams-code-quality for code review
   - Plan ava-thompson-testing-evangelist for test fixes

4. **Risk Assessment**
   - Identify potential side effects
   - Note if fix might affect other components
   - Plan verification strategy

### Phase 2: Execution

1. **Workflow Compliance**
   - Follow `constitutions/workflows/quality/review-code.md` if applicable
   - Apply debugging best practices
   - Reference error handling standards

2. **Primary Implementation**
   - Explain the root cause with evidence
   - Propose fix with clear rationale
   - Implement fix with confidence
   - Add diagnostic code if necessary

3. **Standards Enforcement**
   - Maintain TypeScript type safety
   - Follow project coding standards
   - Ensure test coverage maintained

4. **Edge Case Handling**
   - Check for similar bugs elsewhere
   - Apply fix pattern consistently
   - Consider preventive measures

### Phase 3: Verification

1. **Quality Assurance**
   - Re-run failed hook/test
   - Verify fix resolves issue
   - Check no new failures introduced

2. **Cleanup**
   - Remove all diagnostic console.logs
   - Clean temporary debugging code
   - Ensure code is production-ready

3. **Side Effect Validation**
   - Run full test suite
   - Verify type checking passes
   - Check linting compliance

### Phase 4: Reporting

**Output Format:**

```text
[✅/❌] Command: husky

## Summary
- Files modified: [count]
- Tests passed: [count/total]
- Hook status: [PASS/FAIL]

## Root Cause Analysis
- **Issue**: [Description with evidence]
- **Evidence**: [Code/logs supporting diagnosis]

## Actions Taken
1. [Fix applied with rationale]
2. [Verification performed]

## Similar Issues Found
- [Location]: [Status]

## Next Steps (if applicable)
- Stage changes with: git add [files]
- Review changes before commit
```

## 📝 Examples

### Simple Hook Failure

```bash
/husky "pre-commit hook failed: ESLint errors"
# Analyzes ESLint output, fixes issues, stages changes
```

### Test Failure Debug

```bash
/husky "TypeError: Cannot read property 'id' of undefined at UserService.test.ts:45"
# Diagnoses test failure, adds logging if needed, fixes issue
```

### Type Error Resolution

```bash
/husky "TypeScript error TS2345: Argument of type 'string' is not assignable"
# Identifies type mismatch, corrects typing, verifies build
```

### Complex CI Failure

```bash
/husky "CI pipeline failed at integration tests"
# Runs full diagnostic, identifies root cause, fixes and verifies
# May delegate to specialized agents for complex fixes
```

### Error Case Handling

```bash
/husky "random error message"
# Error: Cannot identify hook or CI failure
# Suggestion: Provide specific error output or run 'npm test' manually
# Alternative: Check .husky/ directory for hook configurations
```
