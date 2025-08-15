# Create Standard

**Purpose**: Generate a new standard documentation file that defines mandatory practices, patterns, and principles for a specific technical domain
**When to use**: When AI needs to create a new standard file in the constitutions/standards/ directory based on requirements
**Prerequisites**: Access to templates/standard.md, understanding of the technical domain, existing standards reviewed programmatically

## Expert Role

You are a **Technical Documentation Architect** with deep expertise in creating clear, enforceable standards. Your mindset prioritizes:

- **Precision**: Every requirement must be specific and measurable
- **Completeness**: Cover all common scenarios and edge cases  
- **Clarity**: Use simple language with concrete examples
- **Structure**: Follow the template exactly for consistency
- **Practicality**: Focus on real-world applicable patterns

## Steps

### 1. Analyze Requirements and Context

First understand what standard needs to be created by gathering information about the technical domain:

- [ ] Identify the technical domain (frontend, backend, code, quality, security, project)
- [ ] Understand the specific problem or pattern to standardize
- [ ] Determine the scope and boundaries of the standard
- [ ] Use available search tools to check for existing related standards
- [ ] Identify target audience (developers, architects, reviewers)

**Anti-pattern to avoid:**

```typescript
// ❌ Don't create overlapping standards
// If error-handling.md exists, don't create error-management.md

// ✅ Do create complementary standards  
// If error-handling.md exists, create error-logging.md for different aspect
```

### 2. Load and Prepare Template

**🔴 CRITICAL: The generated standard MUST follow the templates/standard.md template structure exactly.**

Load and prepare the standard template for instantiation:

- [ ] Use file reading tools to load templates/standard.md file
- [ ] Identify all template sections that must be included
- [ ] Note all placeholders that need replacement
- [ ] List all AI instruction comments to follow
- [ ] Determine target category (code, frontend, backend, quality, security, or project)
- [ ] Choose descriptive filename for the standard
- [ ] Construct target path: constitutions/standards/[category]/[filename].md

Additional validation tasks:

- [ ] Verify all template sections are accounted for
- [ ] Plan content structure based on domain requirements
- [ ] Ensure every template section will be included in output
- [ ] Confirm no sections will be omitted or skipped

Always start from the template, never create from scratch. The template structure is mandatory and must be preserved in the final output.

### 3. Generate Standard Title and Overview

Create the standard's title and overview section:

```markdown
# [Replace with Specific Standard Name]

_[One-line description of what this standard covers and why it matters]_
```

Title generation tasks:

- [ ] Create noun phrase title (e.g., "Function Design" not "Design Functions")
- [ ] Make scope specific (e.g., "React Hooks" not just "Hooks")
- [ ] Keep title under 4 words when possible
- [ ] Include technology name if specific (TypeScript, React, Node.js)
- [ ] Write one-line description explaining scope and importance
- [ ] Replace all template placeholders with actual content

### 4. Define Core Principles (Generate 3-5)

Create fundamental principles that guide all rules in the standard:

```markdown
## Core Principles

### Principle 1: [Clear, Active Title]

[One sentence explaining why this principle is essential]

```typescript
// ✅ GOOD: [Specific reason this follows the principle]
[Generate working code example]

// ❌ BAD: [Specific reason this violates the principle]  
[Generate problematic code example]
```

```

Principle generation tasks:

- [ ] Determine 3-5 fundamental principles for the domain
- [ ] Write clear, active title for each principle
- [ ] Explain why each principle is essential (one sentence)
- [ ] Generate working TypeScript code example for good practice
- [ ] Generate contrasting bad practice example
- [ ] Add specific reasons for good/bad classifications
- [ ] Ensure principles are actionable and measurable
- [ ] Verify all code examples compile correctly

Remember that principles are foundational - all other rules derive from them.

### 5. Generate Main Topic Sections

Create comprehensive sections covering all aspects of the standard:

```markdown
## [Primary Topic Area]

### [Specific Pattern or Rule]

[When and why to use this pattern]

```typescript
// Template pattern
[Generic pattern with placeholders for reuse]

// Concrete example
[Actual implementation showing the pattern]
```

### Quick Reference

| Pattern | When to Use | Example | Performance |
|---------|------------|---------|-------------|
| [Gen 1] | [Use case] | `code` | [Impact] |
| [Gen 2] | [Use case] | `code` | [Impact] |

```

Topic section generation tasks:

- [ ] Identify 2-4 main topic areas for the domain
- [ ] Create section for each topic area
- [ ] Write specific patterns or rules for each section
- [ ] Explain when and why to use each pattern
- [ ] Generate generic template pattern for reuse
- [ ] Create concrete implementation example
- [ ] Build quick reference table with patterns
- [ ] Include use cases and performance impacts
- [ ] Progress from basic to advanced concepts
- [ ] Add decision matrices where applicable

### 6. Generate Patterns and Best Practices

Create reusable patterns developers can copy directly into their code:

```markdown
## Patterns & Best Practices

### [Pattern Name Based on Domain]

**Purpose:** [What problem this pattern solves]

**When to use:**
- [Specific scenario 1]
- [Specific scenario 2]
- [Specific scenario 3]

**Implementation:**

```typescript
// Generic template
[Generate parameterized pattern]

// Real-world usage
[Generate concrete implementation]
```

```

Pattern generation tasks:

- [ ] Identify 3-6 common patterns for the domain
- [ ] Name each pattern clearly based on its purpose
- [ ] Write purpose statement for what problem it solves
- [ ] List 3 specific scenarios when to use the pattern
- [ ] Generate parameterized template version
- [ ] Create real-world implementation example
- [ ] Ensure all code is copy-pasteable
- [ ] Verify TypeScript types are complete
- [ ] Test that examples compile correctly

### 7. Generate Anti-Patterns Section

Document common mistakes and how to avoid them:

```markdown
## Anti-Patterns

### [Anti-Pattern Name]

```typescript
// ❌ Never do this:
[Generate problematic code example]

// Problem: [Explain specific issues this causes]
// - Issue 1: [Specific problem]
// - Issue 2: [Specific problem]

// ✅ Instead, do this:
[Generate corrected version]

// Why: [Explain benefits of correct approach]
// - Benefit 1: [Specific improvement]
// - Benefit 2: [Specific improvement]
```

```

Anti-pattern generation tasks:

- [ ] Identify 3-5 common mistakes in the domain
- [ ] Name each anti-pattern descriptively
- [ ] Generate problematic code example
- [ ] List specific issues the anti-pattern causes
- [ ] Create corrected version of the code
- [ ] Explain benefits of the correct approach
- [ ] Include performance impacts if relevant
- [ ] Include security impacts if relevant
- [ ] Ensure examples are realistic scenarios
- [ ] Verify corrected versions compile properly

### 8. Generate Decision Trees

Create decision support tools for quick choices:

```markdown
## Quick Decision Tree

1. **[First Decision Point]**
   - If [condition A] → Use [Pattern/Approach A]
   - If [condition B] → Use [Pattern/Approach B]  
   - Otherwise → Use [Default Pattern]

2. **[Second Decision Point]**
   - If [condition X] → Apply [Technique X]
   - If [condition Y] → Apply [Technique Y]

## Decision Matrix

| Scenario | Recommended Approach | Avoid | Reason |
|----------|---------------------|-------|---------|
| [Scenario 1] | [Approach] | [Anti-pattern] | [Why] |
| [Scenario 2] | [Approach] | [Anti-pattern] | [Why] |
```

Decision tool generation tasks:

- [ ] Identify 2-3 common decision points in the domain
- [ ] Create decision tree for each point
- [ ] Write concrete, testable conditions
- [ ] Specify recommended approach for each condition
- [ ] Include default/fallback pattern
- [ ] Build decision matrix for complex scenarios
- [ ] List scenarios with recommended approaches
- [ ] Identify anti-patterns to avoid for each scenario
- [ ] Provide clear reasons for recommendations
- [ ] Link to relevant detailed sections

### 9. Add Related Standards Links

Generate cross-references and external resources:

```markdown
## Related Workflows & Standards

### Standards
- [TypeScript Standards](@../code/typescript.md) - Type safety requirements
- [Testing Standards](@../quality/testing.md) - How to test implementations
- [Documentation Standards](@../code/documentation.md) - Documenting compliant code

### Workflows  
- [Workflow Name](@../../workflows/category/workflow.md) - Uses this standard in Step X
- [Workflow Name](@../../workflows/category/workflow.md) - Applies these patterns

### External Resources
- [Official Documentation](@https://...) - Authoritative reference
- [Best Practices](@https://...) - Community guidelines
```

Link generation tasks:

- [ ] Use search tools to find related standards in constitutions/standards/
- [ ] Select 3-5 most relevant standards
- [ ] Write brief description of each relationship
- [ ] Search for workflows that would use this standard
- [ ] Link relevant workflows with specific step references
- [ ] Find official documentation for the technology
- [ ] Include community best practices resources
- [ ] Verify all internal links are valid paths
- [ ] Ensure external URLs are authoritative sources

### 10. Write Standard File

**🔴 FINAL VALIDATION: Ensure the generated file follows templates/standard.md structure EXACTLY.**

Create and save the complete standard file:

File creation tasks:

- [ ] Compile all generated sections into complete document
- [ ] **MANDATORY: Verify all templates/standard.md sections are present**
- [ ] Ensure all placeholders are replaced with actual content
- [ ] Preserve AI instruction comments for future updates
- [ ] Validate all TypeScript code examples compile
- [ ] Check all tables are properly formatted
- [ ] Verify internal links point to valid paths
- [ ] **Confirm structure matches templates/standard.md exactly**
- [ ] Use file writing tools to create file at constitutions/standards/[category]/[filename].md
- [ ] Verify file was created successfully

The generated file MUST be a complete instantiation of the templates/standard.md template with all sections present and filled with domain-specific content.

### 11. Update Index Files

Make the new standard discoverable in index files:

Index update tasks:

- [ ] Use file editing tools to update constitutions/standards/README.md
- [ ] Add link to new standard with brief description
- [ ] Check if constitutions/standards/[category]/README.md exists
- [ ] If category README exists, add entry for new standard
- [ ] Search for workflows that should reference this standard
- [ ] Update relevant workflow files to reference new standard
- [ ] Consider if CLAUDE.md needs update for fundamental standards
- [ ] Save all modified index files

## Standards to Follow

**🔴 MANDATORY: All standards listed below MUST be followed without exception**

- [Documentation Guidelines](@../../standards/code/documentation.md) - Structure and formatting for documentation
- [Naming Conventions](@../../standards/code/naming.md) - File and section naming patterns
- [TypeScript Standards](@../../standards/code/typescript.md) - TypeScript code in examples
- [General Principles](@../../standards/code/general-principles.md) - Overall quality principles

These meta-standards apply to the standard being created. Ensure generated content follows these standards and all examples follow TypeScript standards.

## Common Issues

Common problems to check for after generation:

- **Placeholder not replaced**: Ensure all `[bracketed]` placeholders are replaced with actual content
- **Invalid code examples**: All TypeScript examples must compile without errors
- **Missing sections**: Every section from template must be present or explicitly noted as N/A
- **Broken links**: Verify paths to other standards/workflows exist
- **Vague requirements**: Replace abstract concepts with specific, measurable rules
- **No examples**: Every rule/pattern must have at least one code example
- **Formatting issues**: Tables must be properly aligned, code blocks properly closed
- **Category mismatch**: Ensure standard is placed in correct category folder

Run validation to ensure quality and fix any issues before finalizing.

## Output Template

### Expected Generated Structure

```markdown
# [Specific Standard Title]

_[One-line description of scope and purpose]_

## Core Principles

### [Generated Principle 1]
[Explanation with code examples]

### [Generated Principle 2]
[Explanation with code examples]

## [Main Topic Area 1]

### [Pattern/Rule Name]
[Description and examples]

### Quick Reference
[Generated reference table]

## [Main Topic Area 2]

### [Advanced Patterns]
[More complex examples]

## Patterns & Best Practices
[3-6 reusable patterns]

## Anti-Patterns
[3-5 common mistakes to avoid]

## Quick Decision Tree
[Decision support tools]

## Related Workflows & Standards
[Cross-references and links]
```

This shows the expected output structure. All sections should have substantial generated content. Keep AI instruction comments in the generated file for future maintenance.
