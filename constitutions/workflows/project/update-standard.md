# Update Standard

**Purpose**: Update an existing standard documentation file to add new patterns, clarify requirements, or expand coverage while maintaining consistency
**When to use**: When AI needs to modify a standard file in constitutions/standards/ to add content, fix issues, or enhance documentation
**Prerequisites**: Existing standard file to update, clear requirements for what needs changing, understanding of current standard content

## Expert Role

You are a **Standards Maintenance Specialist** with expertise in evolving technical documentation. Your mindset prioritizes:

- **Preservation**: Keep existing valid content intact unless explicitly changing it
- **Enhancement**: Add value through new examples, patterns, and clarifications
- **Consistency**: Maintain the original structure and style of the document
- **Completeness**: Fill gaps without creating redundancy
- **Clarity**: Improve readability while keeping technical accuracy

## Steps

### 1. Read and Analyze Current Standard

Load and analyze the existing standard thoroughly:

Initial reading tasks:

- [ ] Use file reading tools to load constitutions/standards/[category]/[standard-name].md
- [ ] Read entire file to understand current coverage
- [ ] Note all existing principles and their rationale
- [ ] Map current topic areas and their organization
- [ ] List patterns already documented
- [ ] Identify anti-patterns currently covered
- [ ] Check existing decision trees and matrices
- [ ] Review related standards and workflows linked

Structure analysis tasks:

- [ ] Document the current section organization
- [ ] Note the writing tone and style used
- [ ] Identify well-documented areas
- [ ] Find gaps in coverage
- [ ] Analyze code example patterns used
- [ ] Check formatting conventions followed

**Anti-pattern to avoid:**

```markdown
// ❌ Don't duplicate existing content
// If "Error Handling" section exists, don't add "Exception Management" section

// ✅ Do enhance existing sections
// Add new patterns to existing "Error Handling" section
```

Thorough analysis prevents duplication and ensures enhancements fit naturally.

### 2. Identify Update Requirements

Categorize and plan all required changes:

```markdown
## Update Classification

### Content Additions
- New patterns to add
- Additional examples needed
- Edge cases to document
- Missing anti-patterns

### Clarifications
- Ambiguous requirements to clarify
- Better explanations needed
- More concrete examples

### Corrections
- Technical errors to fix
- Broken code examples
- Outdated practices

### Structural Changes
- New sections needed
- Reorganization required
- Missing standard sections from template
```

Update planning tasks:

- [ ] Classify updates into categories above
- [ ] List specific sections that need modification
- [ ] Identify completely new sections to add
- [ ] Note code examples requiring updates
- [ ] Plan optimal placement for new content
- [ ] Check for missing template sections
- [ ] Prioritize changes by importance
- [ ] Document rationale for each change

Clear requirements prevent unnecessary changes and maintain focus.

### 3. Update Core Principles (If Needed)

Carefully enhance or add principles only when necessary:

```markdown
## Core Principles

### [Existing Principle - Enhanced]

[Original explanation with additions for clarity]

```typescript
// ✅ GOOD: [Original example - still valid]
originalExample();

// ✅ Also Good: [New pattern that emerged]
enhancedExample(); // Added in update
```

### [New Principle - Only if Critical Gap]

**Added because:** [Specific gap this fills that wasn't covered]

[Clear explanation with examples]
```

Principle update rules:

- [ ] Keep all existing valid principles
- [ ] Only add principles for major gaps
- [ ] Enhance explanations without changing meaning
- [ ] Add new examples alongside existing ones
- [ ] Document why new principles were added

Remember that principles are foundational - modify them carefully.

### 4. Enhance Topic Sections

Expand existing sections with complementary content:

```markdown
## [Existing Topic Area]

### [Existing Subtopic]

[Keep original content...]

#### Additional Patterns

[New patterns that complement existing ones]

```typescript
// New pattern for edge case
[Code example for newly documented scenario]
```

### [New Subtopic - If Needed]

[Content for aspect not previously covered]
```

Topic enhancement tasks:

- [ ] Identify sections needing expansion
- [ ] Add new patterns to relevant existing sections
- [ ] Document edge cases and advanced scenarios
- [ ] Create additional examples for complex concepts
- [ ] Build quick reference tables if missing
- [ ] Preserve all original valid examples
- [ ] Ensure new content flows naturally
- [ ] Maintain consistent formatting

Build upon existing content rather than replacing it.

### 5. Add New Patterns and Anti-Patterns

Extend pattern documentation with new discoveries:

```markdown
## Patterns & Best Practices

### [Existing Pattern]
[Keep existing content...]

### [New Pattern Name]

**Purpose:** [Problem this new pattern solves]

**When to use:**
- [New scenario discovered]
- [Edge case now covered]

**Implementation:**

```typescript
// New pattern template
[Generic version for reuse]

// Real-world example
[Concrete implementation]
```

## Anti-Patterns

### [Existing Anti-Pattern]
[Keep existing content...]

### [New Anti-Pattern]

```typescript
// ❌ Newly identified bad practice:
[Code showing the problem]

// Problem: [What issues this causes]

// ✅ Correct approach:
[Fixed version]
```
```

Pattern addition tasks:

- [ ] Review existing patterns to avoid duplication
- [ ] Create descriptive names for new patterns
- [ ] Write purpose statement for each new pattern
- [ ] List specific use cases for new patterns
- [ ] Generate template and implementation examples
- [ ] Preserve all working existing patterns
- [ ] Document newly discovered anti-patterns
- [ ] Explain problems and solutions clearly
- [ ] Verify all new code examples compile
- [ ] Maintain consistent formatting throughout

New patterns should extend coverage, not replace existing ones.

### 6. Update Decision Support Tools

Extend decision tools with new scenarios:

```markdown
## Quick Decision Tree

[Keep existing decision points...]

3. **[New Decision Point]**
   - If [new condition] → Use [Pattern/Approach]
   - If [other condition] → Use [Alternative]

## Decision Matrix

| Scenario | Recommended | Avoid | Reason |
|----------|-------------|-------|---------|
| [Existing] | [Keep] | [Keep] | [Keep] |
| [New Case] | [New Approach] | [Anti-pattern] | [Why] |
```

Decision tool update tasks:

- [ ] Review existing decision trees and matrices
- [ ] Identify gaps in decision coverage
- [ ] Add new decision points for new patterns
- [ ] Expand matrix with additional scenarios
- [ ] Preserve all existing valid decisions
- [ ] Ensure logical flow in decision trees
- [ ] Write concrete, testable conditions
- [ ] Link to relevant sections for details

Extend decision support tools rather than rebuilding them.

### 7. Update Cross-References

Refresh and expand links to related content:

```markdown
## Related Workflows & Standards

### Standards
[Keep existing links...]
- [Newly Related Standard](@../path/to/standard.md) - How it relates

### Workflows
[Keep existing links...]
- [New Workflow](@../../workflows/new/workflow.md) - Now uses this standard

### External Resources
[Keep existing links...]
- [New Resource](@https://...) - Recently published best practices
```

Cross-reference update tasks:

- [ ] Verify all existing links are still valid
- [ ] Keep all working existing links
- [ ] Search for newly created related standards
- [ ] Add links to new related standards
- [ ] Find workflows that now use this standard
- [ ] Add new workflow references with step numbers
- [ ] Check external links for outdated URLs
- [ ] Update broken or outdated external links
- [ ] Write clear relationship descriptions

Preserve existing references while adding new connections.

### 8. Fill Missing Template Sections

**🔴 CRITICAL: The updated standard MUST maintain compliance with the templates/standard.md template structure.**

Ensure all template sections are present:

Template compliance tasks:

- [ ] Use file reading tools to load templates/standard.md
- [ ] **MANDATORY: Verify all template sections are present**
- [ ] Compare current standard against template structure
- [ ] Identify any missing template sections
- [ ] Add missing sections in appropriate locations
- [ ] Generate domain-relevant content for new sections
- [ ] Maintain logical flow and organization
- [ ] Preserve existing section order where possible
- [ ] **Ensure template structure compliance is maintained**

Complete any gaps from the original template to ensure comprehensiveness.

### 9. Validate Updated Content

Perform comprehensive quality validation:

Content quality validation:

- [ ] Verify all original valid content is preserved
- [ ] Confirm new content adds value without redundancy
- [ ] Test all code examples compile correctly
- [ ] Check all internal links point to valid files
- [ ] Validate external URLs are still active

Structure integrity checks:

- [ ] Ensure document structure is maintained
- [ ] Verify sections flow logically
- [ ] Check formatting consistency throughout
- [ ] Confirm tables are properly aligned
- [ ] Validate markdown syntax is correct

Completeness verification:

- [ ] Confirm all planned updates are implemented
- [ ] Verify no sections were accidentally deleted
- [ ] Check all template sections are present
- [ ] Ensure cross-references are updated
- [ ] Review AI instruction comments are preserved

Validate that updates improve the standard without breaking existing functionality.

### 10. Write Updated Standard

**🔴 FINAL VALIDATION: Ensure the updated file still follows templates/standard.md structure EXACTLY.**

Save the enhanced standard file:

File update tasks:

- [ ] **MANDATORY: Template structure from templates/standard.md is preserved**
- [ ] Compile all changes into complete document
- [ ] Verify all additions are properly integrated
- [ ] Confirm original valid content is preserved
- [ ] Ensure new content flows naturally
- [ ] Maintain all AI instruction comments
- [ ] Mark significant additions with date comments
- [ ] **Verify all template sections remain present**
- [ ] Use file editing tools to save to constitutions/standards/[category]/[standard-name].md
- [ ] Confirm file saved successfully

Save the complete updated standard with all improvements while maintaining full template compliance.

### 11. Update Change Log (If Exists)

Document all changes made:

```markdown
## Change Log

### [Date] - Enhancement Update
- Added: [List new patterns/sections]
- Enhanced: [List expanded sections]
- Clarified: [List clarified requirements]
- Fixed: [List any corrections]
```

Change documentation tasks:

- [ ] Check if change log section exists in file
- [ ] If exists, add new entry with current date
- [ ] List all new patterns or sections added
- [ ] Document which sections were enhanced
- [ ] Note any clarifications made
- [ ] List any corrections or fixes applied
- [ ] Include rationale for significant changes
- [ ] Format consistently with existing entries

Document changes for transparency and future reference.

## Standards to Follow

**🔴 MANDATORY: All standards listed below MUST be followed without exception**

- [Documentation Guidelines](@../../standards/code/documentation.md) - Maintain documentation quality
- [Naming Conventions](@../../standards/code/naming.md) - Keep consistent naming
- [TypeScript Standards](@../../standards/code/typescript.md) - Ensure code examples remain valid
- [General Principles](@../../standards/code/general-principles.md) - Preserve quality principles

These standards apply to how updates are made. Maintain existing quality levels and ensure consistency throughout.

## Common Issues

Common problems to avoid during updates:

- **Deleting valid content**: Never remove working examples or valid rules
- **Duplicating sections**: Check if content already exists before adding
- **Breaking examples**: Ensure all code examples still compile after edits
- **Losing structure**: Maintain the original document organization
- **Inconsistent style**: Match the existing tone and format
- **Missing AI comments**: Preserve all AI instruction comments
- **Unmarked changes**: Mark significant additions with date comments
- **Invalid links**: Verify all cross-references still work

Focus on preservation and enhancement. Validate thoroughly before saving.

## Update Summary Template

### Expected Update Summary

```markdown
## Update Summary for [Standard Name]

### Sections Modified
- [Section Name]: [What was added/changed]
- [Section Name]: [What was added/changed]

### New Content Added
- [New Pattern 1]: [Purpose]
- [New Pattern 2]: [Purpose]
- [New Anti-Pattern]: [What it prevents]

### Clarifications Made
- [Requirement]: [How it was clarified]
- [Example]: [What was improved]

### Gaps Filled
- [Missing Topic]: [What was added]
- [Edge Case]: [How it's now covered]

### Files Updated
- constitutions/standards/[category]/[name].md
- [Any index files updated]
```

This summary format helps track all changes made and is useful for review and tracking.