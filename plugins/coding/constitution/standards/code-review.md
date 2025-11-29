# Code Review Standards

_Standards for conducting effective, constructive code reviews that improve code quality and team knowledge_

## Dependent Standards

🚨 **[IMPORTANT]** You MUST also read the following standards together with this file

- General Coding Principles (standard:general-principles) - Foundation of what makes good code and provides the principles to check against during review

## Core Principles

### Truth Over Ego

Value accuracy over being right. Every correction upgrades the system.

```typescript
// ✅ GOOD: Embrace corrections as learning
// Reviewer: "This approach has a race condition under load"
// Author: "You're right. I missed that. Let me add synchronization.
//          Can we document this pattern for others?"

// ❌ BAD: Defensive response
// "Well it works for now, we can fix it later if it's a problem"
```

**Application**:

- Corrections are data, not criticism
- Update beliefs when evidence shows they're wrong
- Document what you learned for the team
- Ask "What else am I missing?" to invite deeper review

### Constructive Collaboration

Reviews improve code and build team knowledge.

```typescript
// ✅ GOOD: Constructive feedback
// "suggestion: Consider extracting this validation logic into
// a reusable function for consistency across endpoints"

// ❌ BAD: Unconstructive criticism
// "This code is terrible"
```

### Focus on Impact

Prioritize critical issues over style. Critique is about ideas, not people.

```typescript
// ✅ GOOD: Focus on important issues
// "issue: This SQL query is vulnerable to injection attacks"

// ❌ BAD: Over-focusing on minor style
// "nit: Add space after comma (50 comments on spacing)"
```

### Psychological Safety with High Standards

Make the team feel trusted while maintaining rigorous quality.

**Application**:

- Separate code quality from personal worth
- Good process is praised even when outcomes disappoint
- Explain why standards matter, don't just enforce
- Invite challenge: "What am I missing in this review?"

## Review Focus Areas

### Correctness (Critical)

Does the code work correctly?

```typescript
// check for:
// - Logic errors, edge cases, null handling
// - Off-by-one errors, race conditions
// - Suppression comments (eslint-disable, @ts-ignore, etc.)

// example feedback:
// "issue: Function doesn't handle empty array case"
if (items.length === 0) return defaultValue;
```

## Suppression Comments

Suppression comments (`eslint-disable`, `@ts-ignore`, `@ts-expect-error`, `@ts-nocheck`, etc.) are **acceptable when properly documented** with reasoning.

### Review Action

When you find suppression comments:

1. **Check for documentation** - Is there a comment explaining WHY?
2. **If undocumented** - Request documentation before approving
3. **If documented** - Accept if the reasoning is valid

### Example of Acceptable Suppression

```typescript
// TypeScript cannot infer the narrowed type after the instanceof check in this closure
// @ts-expect-error - see https://github.com/microsoft/TypeScript/issues/9998
const handler = (err: unknown) => err instanceof Error && err.cause;
```

### Handling Untyped Libraries (NOT Suppression)

For third-party libraries without types, create type declarations instead of suppressing:

```typescript
// in types/legacy-lib.d.ts
declare module 'legacy-lib' {
  export function process(data: unknown): ProcessResult;
}
```

### Example of Unacceptable Suppression

```typescript
// ❌ BAD: Using suppression instead of creating type declarations
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const result = legacyLib.process(data) as any;
```

### Security (Critical)

```typescript
// check for:
// - Input validation, SQL injection
// - Authentication, authorization
// - Data exposure, XSS prevention

// example:
// "CRITICAL: Use parameterized queries"
db.query('SELECT * FROM users WHERE id = ?', [userId])
```

### Performance (Important)

```typescript
// check for:
// - Algorithm efficiency O(n) vs O(n²)
// - N+1 queries, memory leaks
// - Unnecessary imports, caching

// example:
// "consider Map for O(1) lookups"
const userMap = new Map(users.map(u => [u.id, u]));
```

### Maintainability (Important)

```typescript
// check for:
// - Readability, simplicity, DRY principle
// - Single responsibility, clear naming

// example:
// "extract validation logic for reusability"
function validateUserInput(input) { ... }
```

### Testing (Important)

```typescript
// check for:
// - Test coverage, edge cases
// - Test quality, isolation, naming

// example:
// "add tests for error scenarios:"
// - API returns 404
// - Network failure
// - Malformed response
```

## Quick Reference

| Priority | Focus Area | Comment Prefix | Example |
|----------|------------|----------------|----------|
| 🔴 Critical | Security/Correctness | `issue:` | `issue: SQL injection vulnerability` |
| 🟡 Important | Performance/Architecture | `suggestion:` | `suggestion: Extract to utility function` |
| 🟢 Optional | Style/Minor | `nit:` | `nit: Consider destructuring` |
| 🔵 Info | Clarification | `question:` | `question: Why sort twice?` |
| 🟢 Positive | Good practices | `praise:` | `praise: Great use of types!` |

## Patterns & Best Practices

### Effective Feedback Pattern

**Purpose**: Provide actionable, constructive code review comments

**When to use**:

- Critical issues that must be fixed
- Important improvements for maintainability  
- Educational opportunities

**Implementation**:

```typescript
// pattern: [prefix]: [problem] + [solution] + [context]
"issue: Function throws on null input. Add guard clause: 
if (!user) return null; // API can return null users"

"suggestion: Extract validation logic for reusability:
function validateEmail(email) { ... }"
```

### Comment Prefix System

**Purpose**: Categorize feedback by urgency and type

**Implementation**:

```typescript
// critical - must be fixed
"issue: This will cause runtime errors"

// important - should be improved  
"suggestion: Consider extracting to utility"

// optional - minor improvement
"nit: Spacing consistency"

// information - seeking clarity
"question: Is this intentional behavior?"

// recognition - positive feedback
"praise: Excellent error handling!"
```

### Common Review Patterns

1. **Security Review** - Check for vulnerabilities

   ```typescript
   // always validate user input
   if (!isValidEmail(email)) throw new Error('Invalid email');
   ```

2. **Performance Review** - Identify bottlenecks

   ```typescript
   // use efficient data structures
   const lookup = new Map(); // O(1) vs array.find O(n)
   ```

## Quick Decision Tree

1. **Prioritizing Comments**
   - If security/correctness issue → `issue:` (must fix)
   - If performance/architecture → `suggestion:` (should improve)
   - If style/minor → `nit:` (optional)
   - If unclear → `question:` (seek clarification)

2. **Review Depth**
   - If < 100 lines → Detailed line-by-line review
   - If 100-500 lines → Focus on key areas → Detailed line-by-line review (if no key issues found)
   - If > 500 lines → Architectural review first → Focus on key areas (if no architectural issues found) → Detailed line-by-line review (if no key issue found)
   - If hotfix → Security and correctness only
