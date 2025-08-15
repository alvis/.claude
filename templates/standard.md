# [Standard Title]

_[Brief description of what this standard covers and its purpose]_

<!-- INSTRUCTION: Replace placeholders in brackets with actual content -->
<!-- INSTRUCTION: Use clear, imperative language (e.g., "Use X", "Avoid Y", "Follow Z") -->
<!-- INSTRUCTION: Include practical examples for every rule or guideline -->
<!-- INSTRUCTION: Keep sections focused and avoid redundancy -->

## Core Principles

<!-- INSTRUCTION: List 3-5 fundamental principles that guide this standard -->
<!-- INSTRUCTION: Each principle should be actionable and clear -->

### [Principle 1 Name]

[Brief explanation of the principle and why it matters]

```typescript
// ✅ GOOD: [Explanation of good practice]
[Code example demonstrating the principle]

// ❌ BAD: [Explanation of why this is wrong]
[Counter-example showing what to avoid]
```

### [Principle 2 Name]

[Continue pattern for remaining principles...]

## [Main Topic Area 1]

<!-- INSTRUCTION: Break down the standard into logical topic areas -->
<!-- INSTRUCTION: Each area should cover a specific aspect comprehensively -->

### [Subtopic 1.1]

[Introduction to the subtopic and when it applies]

```typescript
// Standard pattern/template
[Code template or interface definition]

// Example implementation
[Concrete example using the pattern]
```

### [Subtopic 1.2]

#### Basic Pattern

```typescript
// ✅ GOOD: [Specific practice]
[Good example code]

// ❌ BAD: [Common mistake]
[Bad example code]
```

#### Advanced Pattern

```typescript
// When you need [specific requirement]:
[Advanced example with annotations]
```

## [Main Topic Area 2]

### Quick Reference

<!-- INSTRUCTION: Include tables for quick lookup when appropriate -->

| Pattern | Use Case | Example | Notes |
|---------|----------|---------|-------|
| [Pattern 1] | [When to use] | `[code]` | [Additional context] |
| [Pattern 2] | [When to use] | `[code]` | [Additional context] |

### Decision Matrix

<!-- INSTRUCTION: Help developers make quick decisions -->

**Use [Option A] when:**

- [Condition 1]
- [Condition 2]
- [Condition 3]

**Use [Option B] when:**

- [Condition 1]
- [Condition 2]

## Patterns & Best Practices

<!-- INSTRUCTION: Provide reusable patterns with clear use cases -->

### [Pattern Name]

**Purpose:** [What problem this pattern solves]

**When to use:**

- [Scenario 1]
- [Scenario 2]

**Implementation:**

```typescript
// Pattern template
[Reusable code pattern with placeholders]

// Real-world example
[Concrete implementation of the pattern]
```

### Common Patterns

<!-- INSTRUCTION: List frequently used patterns in this domain -->

1. **[Pattern 1]** - [Brief description]

   ```typescript
   [Code example]
   ```

2. **[Pattern 2]** - [Brief description]

   ```typescript
   [Code example]
   ```

## Anti-Patterns

<!-- INSTRUCTION: Explicitly call out what NOT to do -->
<!-- INSTRUCTION: Explain WHY each anti-pattern is problematic -->

### [Anti-Pattern 1 Name]

```typescript
// ❌ Never do this:
[Bad code example]

// Problem: [Explain what issues this causes]

// ✅ Instead, do this:
[Corrected code example]

// Why: [Explain the benefits of the correct approach]
```

### Common Mistakes to Avoid

<!-- INSTRUCTION: List frequent errors developers make -->

1. **[Mistake 1]**
   - Problem: [What goes wrong]
   - Solution: [How to fix it]
   - Example: `[code snippet]`

2. **[Mistake 2]**
   - Problem: [What goes wrong]
   - Solution: [How to fix it]

## Quick Decision Tree

<!-- INSTRUCTION: Help developers make quick decisions -->

1. **[First decision point]**
   - If [condition A] → [Action/Choice A]
   - If [condition B] → [Action/Choice B]
   - Otherwise → [Default action]

2. **[Second decision point]**
   - [Continue pattern...]

## Related Workflows & Standards

<!-- INSTRUCTION: Link to related documentation -->

- [Related Standard 1](@../path/to/standard.md) - [How it relates]
- [Related Standard 2](@../path/to/standard.md) - [How it relates]
- [External Resource](@https://example.com) - [Why it's relevant]

<!-- INSTRUCTION: Include supplementary information if needed -->

```json
// [Configuration file name]
{
  "[setting1]": "[value]",
  "[setting2]": "[value]"
}
```

---

<!-- AI META INSTRUCTIONS -->
<!-- 
When using this template to create a new standard:

1. STRUCTURE:
   - Keep sections logically ordered from general to specific
   - Use consistent heading levels (##, ###, ####)
   - Group related content together

2. CONTENT:
   - Be prescriptive - tell developers exactly what to do
   - Provide rationale - explain WHY, not just WHAT
   - Include examples for EVERY guideline
   - Show both good and bad practices

3. CODE EXAMPLES:
   - Use TypeScript for all examples (unless standard is language-specific)
   - Keep examples concise but complete
   - Add comments to explain non-obvious parts
   - Use ✅ and ❌ consistently for good/bad examples

4. FORMATTING:
   - Use tables for quick reference information
   - Use bullet points for lists of conditions or requirements
   - Use numbered lists for sequential steps
   - Use code blocks with proper syntax highlighting

5. TONE:
   - Be direct and clear
   - Avoid ambiguous language
   - Use "must", "should", "may" consistently (RFC 2119)
   - Keep explanations concise

6. COMPLETENESS:
   - Cover common scenarios
   - Address edge cases
   - Include migration paths if replacing existing standards
   - Provide testing guidelines where applicable

7. MAINTENANCE:
   - Include version information if needed
   - Date significant changes
   - Mark deprecated sections clearly
   - Keep examples up to date

Remember: Standards should be authoritative references that developers
can quickly consult to make decisions and write compliant code.
-->