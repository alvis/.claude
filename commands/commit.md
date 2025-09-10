---
allowed-tools: Bash(git:*), Bash(npm:*), Bash(pnpm:*), Read, Grep, Glob
argument-hint: [--no-verify] to skip pre-commit checks
description: Creates well-formatted commits with conventional messages and emoji

---

# Create Commit with Conventional Format

Analyzes changes and creates atomic commits with conventional commit messages and appropriate emoji. Automatically runs pre-commit checks and suggests splitting large changes into multiple commits when appropriate.

## 🎯 Purpose & Scope

**What this command does NOT do:**

- Push commits to remote repository
- Create merge commits
- Modify commit history
- Add any co-authorship footer

**When to REJECT:**

- No changes to commit
- Working directory has merge conflicts
- Pre-commit checks fail (unless --no-verify)
- Uncommitted changes would be lost

## 📊 Dynamic Context

### System State

- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- Modified files: !`git diff --name-only`
- Staged files: !`git diff --cached --name-only`

### Project Context

- Available workflows: !`ls -1 constitutions/workflows/ 2>/dev/null | head -5 || echo "No workflows found"`

## 🔄 Workflow

### Phase 1: Planning

1. **Analyze Requirements**
   - Check for --no-verify flag
   - Identify files to commit
   - Determine project scripts available from package metadata such as package.json
   - Determine pre-commit checks needed

2. **Pre-commit Verification**
   - Run linting script (if any) to ensure code quality
   - Run build script (if any) to verify build succeeds
   - Run document geneation script (if any) to update documentation
   - Skip if --no-verify flag present

3. **Change Analysis**
   - Review git diff for all changes
   - Identify logical groupings
   - Determine if split needed

4. **Risk Assessment**
   - Check for uncommitted changes
   - Verify no merge conflicts
   - Ensure build stability

### Phase 2: Execution

1. **File Staging**
   - Check git status for staged files
   - If no staged files, add all modified/new files
   - Confirm files ready for commit

2. **Commit Splitting (if needed)**
   - Group related changes
   - Stage files for each logical commit
   - Create separate commits for each group

3. **Commit Message Generation**
   - Analyze changes for commit type for each commit group
   - Generate message suggestions following the `Commit Guidelines` below

4. **Commit Creation**
   - Execute git commit with message and signature
   - Verify commit succeeded
   - Report completion status

### Phase 3: Verification

1. **Post-commit Validation**
   - Verify commit created successfully
   - Check git log for new commit
   - Confirm working directory clean

2. **Quality Assurance**
   - Message follows conventional format
   - Description is clear and concise

### Phase 4: Reporting

**Output Format:**

```text
[✅/❌] Command: commit

## Summary
- Files committed: [count]
- Commits created: [count]
- Pre-commit checks: [PASS/SKIP/FAIL]

## Actions Taken
1. [Pre-commit check results]
2. [Staging actions]
3. [Commit creation]

## Commit Messages
- [Emoji Type: Description]

## Next Steps (if applicable)
- [Push to remote]
- [Create pull request]
```

## 📝 Examples

### Simple Commit

```bash
/commit
# Runs pre-commit checks and creates single commit
```

### Skip Verification

```bash
/commit --no-verify
# Skips pre-commit checks for quick commits
```

### Suggested Split Example

```bash
/commit
# Detects multiple logical changes:
# Commit 1: feat: add user authentication
# Commit 2: docs: update API documentation
# Commit 3: fix: resolve memory leak
```

### Error Case Handling

```bash
/commit
# Error: No changes to commit
# Suggestion: Make changes first or check git status
```

### Pre-commit Check Failure

```bash
/commit
# Pre-commit checks failed:
# - Lint errors: 5
# - Build failed: TypeScript compilation errors
# Options: Fix issues or use --no-verify to skip
```

## Commit Guidelines

**Message Format:**

- First line must be under 70 characters, with a soft limit of 50 characters
- Present tense, imperative mood
- No period at end of subject line
- Follow conventional format:
  - `<type>: <description>` for global or non-project/feature specific changes
  - `<type>(scope): <description>` for project or feature specific changes (check git log for historic usages on scope)

**Atomic Commits:**

- Each commit serves single purpose
- Related changes grouped together
- Unrelated changes split into separate commits

**Split Criteria:**

- Different concerns or modules
- Mixed change types (feat/fix/docs)
- Large changes needing breakdown
- Different file patterns
