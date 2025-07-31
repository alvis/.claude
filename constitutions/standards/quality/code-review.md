# Code Review Standards

*Standards for conducting effective, constructive code reviews that improve code quality and team knowledge*

## Core Review Principles

### Review Objectives

- **Improve code quality** - Catch bugs, improve design
- **Share knowledge** - Spread understanding across team
- **Maintain standards** - Ensure consistency
- **Foster collaboration** - Build team cohesion
- **Prevent issues** - Catch problems early

### Review Mindset

- **Be constructive** - Focus on improvement, not criticism
- **Be specific** - Provide actionable feedback
- **Be respectful** - Remember there's a person behind the code
- **Be thorough** - But also be reasonable
- **Be timely** - Review promptly to avoid blocking

## Review Focus Areas

### 1. Correctness

First priority - does the code work correctly?

```typescript
// Review for:
// - Logic errors
// - Edge cases handling
// - Off-by-one errors
// - Null/undefined handling
// - Race conditions

// Example feedback:
// "This function doesn't handle the case where `items` is empty. 
// Consider adding a guard clause: `if (items.length === 0) return defaultValue;`"
```

### 2. Security

Critical security considerations:

- **Input validation** - All user inputs sanitized?
- **Authentication** - Proper auth checks?
- **Authorization** - Correct permission checks?
- **Data exposure** - No sensitive data leaks?
- **SQL injection** - Parameterized queries used?
- **XSS prevention** - Output properly escaped?

```typescript
// ❌ Security issue example:
// "ISSUE: This SQL query uses string concatenation which is vulnerable to SQL injection.
// Use parameterized queries instead:
// `db.query('SELECT * FROM users WHERE id = ?', [userId])`"
```

### 3. Performance

Performance impact assessment:

- **Algorithm efficiency** - O(n) vs O(n²)?
- **Database queries** - N+1 problems?
- **Memory usage** - Memory leaks?
- **Caching opportunities** - Repeated calculations?
- **Bundle size** - Unnecessary imports?

```typescript
// Example feedback:
// "PERFORMANCE: This nested loop creates O(n²) complexity. 
// Consider using a Map for O(1) lookups:
// const userMap = new Map(users.map(u => [u.id, u]));"
```

### 4. Maintainability

Long-term code health:

- **Readability** - Is the code self-explanatory?
- **Simplicity** - Is there a simpler approach?
- **DRY principle** - Any duplication?
- **Single responsibility** - Does each function do one thing?
- **Naming** - Are names clear and consistent?

```typescript
// Example feedback:
// "suggestion: This function is doing too many things. Consider extracting 
// the validation logic into a separate `validateUserInput()` function 
// for better separation of concerns."
```

### 5. Testing

Test coverage and quality:

- **Test coverage** - Are new features tested?
- **Edge cases** - Are edge cases covered?
- **Test quality** - Are tests meaningful?
- **Test isolation** - Do tests run independently?
- **Test naming** - Do test names describe behavior?

```typescript
// Example feedback:
// "question: I don't see tests for the error cases. Could you add tests for:
// - When the API returns 404
// - When the network request fails
// - When the response is malformed"
```

### 6. Architecture

Design and structure:

- **Pattern consistency** - Follows established patterns?
- **Dependency direction** - Clean architecture maintained?
- **Abstraction level** - Appropriate abstractions?
- **Module boundaries** - Clear separation?
- **Future extensibility** - Easy to extend?

## Feedback Patterns

### Comment Prefixes

Use standard prefixes for clarity:

```typescript
// nit: Minor style issue (optional)
"nit: Consider using object destructuring here for cleaner code"

// question: Seeking clarification
"question: Why do we need to sort the array twice? Is this intentional?"

// suggestion: Recommended improvement
"suggestion: Consider extracting this into a reusable utility function"

// issue: Must be addressed
"issue: This will throw an error if `user.profile` is undefined"

// praise: Positive feedback
"praise: Great use of TypeScript discriminated unions here! Very clean."

// thought: Discussion starter
"thought: Have we considered using a state machine for this complex flow?"
```

### Effective Feedback Examples

#### Good Feedback

```typescript
// ✅ Specific and actionable
"The `calculateDiscount` function doesn't validate that the discount 
percentage is between 0 and 100. This could lead to negative prices. 
Consider adding: `if (discount < 0 || discount > 100) throw new Error('Invalid discount')`"

// ✅ Explains the why
"Using `any` type here bypasses TypeScript's type checking. 
This could hide runtime errors. Can we define a proper interface 
for the API response instead?"

// ✅ Provides alternative
"Instead of nested ternary operators which are hard to read:
`return a ? b ? c : d : e`
Consider using if/else statements or extracting to a function 
with early returns for better readability."

// ✅ Acknowledges context
"I see you're optimizing for performance here. While the mutation 
improves speed, it makes the function harder to test. Have you 
considered the trade-off? If performance is critical, please add 
a comment explaining why mutation is necessary."
```

#### Poor Feedback

```typescript
// ❌ Too vague
"This code is confusing"

// ❌ Personal preference without justification
"I don't like this approach"

// ❌ Overly critical
"This is wrong. Did you even test this?"

// ❌ Nitpicking without value
"Add a period at the end of this comment"

// ❌ Solution without explanation
"Change this to `map` instead of `forEach`"
```

## Review Process Standards

### For Reviewers

#### Review Checklist

1. **Understand the context**
   - Read the PR description
   - Check related issues
   - Understand the why

2. **Review systematically**
   - Start with tests
   - Check the implementation
   - Verify documentation

3. **Prioritize feedback**
   - Critical issues first
   - Important suggestions next
   - Style nits last

4. **Be thorough but reasonable**
   - Don't nitpick everything
   - Focus on important issues
   - Respect author's time

#### What to Look For

```typescript
// Architecture & Design
- Does it follow SOLID principles?
- Is it over-engineered or under-engineered?
- Are the abstractions appropriate?

// Code Quality
- Is the code DRY?
- Are functions focused and small?
- Is error handling comprehensive?

// Readability
- Can I understand the code without extensive comments?
- Are variable/function names descriptive?
- Is the flow logical?

// Testing
- Are happy paths tested?
- Are edge cases covered?
- Are tests maintainable?

// Performance
- Are there obvious bottlenecks?
- Is pagination used for large datasets?
- Are expensive operations cached?

// Security
- Is user input validated?
- Are permissions checked?
- Is sensitive data protected?
```

### For Authors

#### Preparing for Review

1. **Self-review first**
   - Review your own diff
   - Check for obvious issues
   - Ensure tests pass

2. **Provide context**
   - Clear PR description
   - Link related issues
   - Explain non-obvious decisions

3. **Keep PRs focused**
   - One feature/fix per PR
   - Separate refactoring
   - Small, reviewable chunks

#### Responding to Feedback

```typescript
// ✅ Good responses
"Good catch! I've added validation for the edge case."
"I chose this approach because [explanation]. Does that make sense?"
"You're right, I'll refactor this to be more maintainable."
"I've added tests for those scenarios."

// ❌ Poor responses
"It works on my machine"
"I've always done it this way"
"That's not important"
"I'll fix it later"
```

## Code Review Anti-Patterns

### Review Anti-Patterns

1. **Rubber stamping** - Approving without real review
2. **Nitpick paralysis** - Focusing only on style
3. **Design changes** - Major redesigns in review
4. **Personal style** - Enforcing personal preferences
5. **Delayed reviews** - Letting PRs sit for days

### Comment Anti-Patterns

```typescript
// ❌ Being a gatekeeper
"This isn't how we do things here"

// ❌ Making it personal
"You always make this mistake"

// ❌ Being dismissive
"This is obviously wrong"

// ❌ Overwhelming with comments
// Adding 50+ minor style comments on a PR

// ❌ Bike-shedding
// Extensive debate on trivial matters while ignoring important issues
```

## Best Practices

### Review Timing

- **Review promptly** - Within 24 hours
- **Set expectations** - Communicate delays
- **Time-box reviews** - Don't spend hours
- **Multiple passes** - Quick pass, then detailed

### Building Knowledge

```typescript
// Share knowledge in reviews
"TIL: JavaScript's Array.sort() mutates the original array. 
Using [...array].sort() creates a copy first. Thanks for teaching me this!"

// Explain domain knowledge
"Context: We validate emails this way because our email provider 
has specific requirements for the '+' character in addresses."

// Reference documentation
"FYI: This pattern is documented in our architecture guide:
[link to docs]"
```

### Creating a Positive Culture

1. **Assume positive intent**
2. **Praise good code publicly**
3. **Discuss concerns privately**
4. **Learn from each other**
5. **Celebrate improvements**

### Review Metrics

Track but don't weaponize:

- **Review turnaround time** - How quickly reviews happen
- **Comments per PR** - Quality over quantity
- **Defect detection** - Issues caught in review
- **Knowledge sharing** - Learning moments

## Special Situations

### Reviewing Junior Developer Code

- More teaching, less criticism
- Explain the why
- Provide examples
- Focus on patterns
- Be extra encouraging

### Reviewing Senior Developer Code

- Still be thorough
- Question decisions respectfully
- Learn from their approach
- Focus on architecture
- Discuss trade-offs

### Emergency Reviews

For hotfixes and urgent changes:

- Focus on the critical fix
- Verify the fix works
- Check for regressions
- Review comprehensively later
- Document the urgency

### Large PR Reviews

When PR is unavoidably large:

1. **Review in chunks** - Logical sections
2. **Multiple reviewers** - Divide work
3. **Focus areas** - Each reviewer takes aspect
4. **Author guidance** - Where to start
5. **Consider splitting** - Even post-hoc

## Tools and Automation

### Automated Checks

Let tools handle:

- Code formatting
- Linting rules
- Test coverage
- Build success
- Security scanning

Focus human review on:

- Logic and design
- Architecture decisions
- Business requirements
- Edge cases
- Knowledge sharing