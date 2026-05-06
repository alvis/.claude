# Invocation Examples

Reference examples for `/review-code`. Each example is gated on a specific invocation pattern (scope, specifier shape). Consult the example matching the user's invocation; do not load all of them.

### Context-Aware Review (Auto-Detect)

```bash
/review
# Detects current context:
#   - If in test files → Reviews test scope
#   - If in docs → Reviews documentation scope
#   - Otherwise → Asks user or defaults to all
```

### Single Scope Review

```bash
/review-code --area=test
# Reviews only test quality, coverage, and complexity
# Delegates to Testing Quality Analyst
```

### Multiple Scope Review

```bash
/review-code "src/api/" --area=security,code-quality
# Reviews API directory for security vulnerabilities and code quality
# Runs security and code-quality analysts in parallel
```

### Pattern-Based Review

```bash
/review-code "src/api/**/*.spec.ts" --area=test
# Reviews only API test files using glob pattern
# Limits file discovery to specified pattern
```

### Pull Request Review

```bash
/review-code "PR#123" --area=all
# Reviews all files changed in pull request 123
# Comprehensive review across all quality dimensions
```

### Directory Review with Custom Output

```bash
/review-code "src/auth/" --out=reviews/auth
# Reviews authentication directory
# Writes reviews/auth/SECURITY.md, QUALITY.md, etc.
# Index at reviews/auth/README.md
```

### Package-Based Review

```bash
/review-code "@myapp/auth" --area=security,code-quality
# Reviews all files that import/use the auth package
# Focuses on security and code quality in auth-related code
```

### CI Mode Example

```bash
/review-code --area=all
# In CI environment:
#   - Writes per-area files under reviews/
#   - Prints area-file listing + aggregate counts to console
#   - No interactive prompts
#   - Exits with non-zero code if any P0 issues found
```

### Interactive Mode Example

```bash
/review-code "src/"
# In interactive environment:
#   - May prompt for scope selection if unclear
#   - Writes per-area files under reviews/
#   - Prints area-file listing with verdicts to console
#   - User-friendly formatting
```

### Glob Pattern Review

```bash
/review-code "src/services/**/auth*.ts" --area=security
# Reviews only auth-related files within services directory
# Focuses on security vulnerabilities using glob pattern
```

### Documentation Review

```bash
/review-code "src/**/*.ts" --area=documentation
# Reviews JSDoc/TSDoc coverage in all TypeScript source files
# Identifies missing or incomplete documentation
```

### Git-Based Review

```bash
/review-code "HEAD~3..HEAD" --area=all
# Reviews changes in last 3 commits
# Comprehensive analysis of recent changes
```

### Pre-Commit Review

```bash
/review-code "$(git diff --cached --name-only)" --area=test,code-quality
# Reviews only staged files
# Perfect for pre-commit hook integration
# Focuses on test and code quality
```

### Multiple File Types Review

```bash
/review-code "**/*.{ts,tsx,js,jsx}" --area=code-quality,style
# Reviews all TypeScript and JavaScript files
# Focuses on code quality and style compliance
```

### Clean Pass Example (single area, zero issues)

```bash
/review-code "src/auth/" --area=style
# Subagent writes reviews/STYLE.md:
#
#   # STYLE Review
#   **Verdict**: ✅ PASS
#   ## General Status
#   _No issues found._
#
# Console output:
#   STYLE.md  ✅ PASS
#   Index: reviews/README.md
```

### Issues with Pending Decisions Example

```bash
/review-code "src/api/" --area=security,code-quality --out=reviews
# Subagents write reviews/SECURITY.md, reviews/QUALITY.md, reviews/CORRECTNESS.md.
# reviews/SECURITY.md contains issues like:
#
#   ## Issues
#   ### P0 — Blockers
#   - [ ] ### SEC-P0-1: missing input validation on /payments
#         **Source**: `src/api/payments.controller.ts:203-218`
#         **Issue**: ...
#         **Solution**: TBD
#   ### P1 — High
#   - [ ] ### SEC-P1-1: token compared with == instead of constant-time
#         **Solution**: replace with `timingSafeEqual` from existing `crypto-utils`
#
#   ## Pending Decisions
#   - [ ] ### SEC-P0-1: missing input validation on /payments
#         **Options**:
#         1. Inline zod schema — Pros: local. Cons: duplicates auth boundary contract.
#         2. Reuse existing `validateRequest` middleware — Pros: consistent. Cons: requires routing tweak.
#         **Recommended**: Option 2 — matches sibling controllers in `users.controller.ts`.
#
# Console output:
#   SECURITY.md     ❌ FAIL — 2 issues (P0:1, P1:1, P2:0, P3:0)
#   QUALITY.md      ✅ PASS
#   CORRECTNESS.md  ✅ PASS
#   Index: reviews/README.md
```

### Error Handling

```bash
/review-code "nonexistent/path"
# Error: Path not found
# Suggestion: Check path exists with 'ls nonexistent/'
# Alternative: Use glob patterns like '/review-code "**/*"' or '/review' for full codebase

/review-code --area=invalid
# Error: Invalid scope 'invalid'
# Valid scopes: test, documentation, code-quality, security, style, all
# Example: /review-code --area=test,code-quality

/review-code "unknown-package"
# Warning: Package 'unknown-package' not found in imports
# Suggestion: Check package name or use file path instead
# Alternative: Use '/review-code "src/**/*"' to review source directory
```
