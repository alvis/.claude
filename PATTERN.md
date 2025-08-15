# Constitution Restructuring Pattern

_Documentation of the role-based organization approach for constitution files_

## Overview

This document describes the pattern used to restructure the CLAUDE.md constitution files from broad action-based files into focused, role-based documentation that scales for a 100-person AI tech company.

## Problems with Previous Structure

1. **Monolithic Files**: Action files were 300-600+ lines, mixing workflows, standards, and examples
2. **Mixed Concerns**: Standards (rules) mixed with workflows (procedures) in single files
3. **Poor Discoverability**: Hard to find relevant information for specific roles
4. **Maintenance Burden**: Large files difficult to update and keep consistent
5. **Cognitive Load**: Too much information to process for specific tasks

## New Organization Principles

### 1. Role-Based Entry Points

Each role gets a dedicated entry point showing:

- Which workflows apply to their daily work
- Relevant standards to follow
- Common patterns to use
- Quick reference for frequent tasks

**Target Roles:**

- Frontend Engineer
- Backend Engineer
- Fullstack Engineer (most common)
- Platform Engineer
- Data Engineer
- ML Engineer

### 2. Content Type Separation

```
workflows/     # HOW to do something (step-by-step procedures)
standards/     # WHAT rules to follow (conventions and requirements)
patterns/      # Templates to copy and adapt
references/    # Lookup information and examples
```

### 3. Domain-Based Grouping

Within each content type, group by domain:

- `coding/` - Language-agnostic development
- `frontend/` - React, UI, client-side concerns
- `backend/` - Services, APIs, server-side concerns
- `quality/` - Testing, reviews, code quality
- `project/` - Git, deployment, operations

## File Size Targets

- **Workflows**: 50-150 lines (single focused procedure)
- **Standards**: 80-200 lines (cohesive rule group)
- **Patterns**: 30-100 lines (focused templates)
- **Role Guides**: 50-100 lines (navigation help)
- **Main CLAUDE.md**: ~150 lines (essential only)

## File Naming Conventions

### Workflows (Action-Oriented)

- Use verbs: `create-component.md`, `verify-auth-scope.md`
- Focus on single action or outcome
- Include workflow metadata at top

### Standards (Rule-Oriented)

- Use nouns: `typescript.md`, `error-handling.md`
- Group related rules together
- Include rationale where helpful

### Patterns (Template-Oriented)

- Use descriptive nouns: `component-template.md`
- Include copy-paste examples
- Show common variations

### Role Guides (Navigation-Oriented)

- Use role names: `frontend-engineer/README.md`
- Focus on what's relevant to that role
- Provide quick access to common tasks

## Cross-Reference System

### Linking Strategy

- Use relative paths: `../standards/code/typescript.md`
- Include "Related" sections in each file
- Create breadcrumb navigation where helpful

### Anchor Naming

- Use consistent kebab-case: `#error-handling-patterns`
- Include section type: `#workflow-build-component`
- Make anchors descriptive and stable

## Content Guidelines

### Workflow Files

```markdown
# [Action Name]

**Purpose**: One-line description of what this accomplishes
**When to use**: Clear trigger conditions for using this workflow
**Prerequisites**: Required knowledge, tools, or setup

## Steps

1. Specific action with verification
2. Next action with expected outcome
3. Final step with next actions

## Standards to Follow

- Link to relevant standards files

## Common Issues

- Known problems and solutions
```

### Standards Files

```markdown
# [Topic] Standards

_Brief description of what rules this covers_

## Core Principles

- High-level guidelines

## Requirements

- Must-follow rules
- Critical constraints

## Conventions

- Preferred approaches
- Style guidelines

## Examples

- Good/bad comparisons
- Common patterns
```

### Pattern Files

```markdown
# [Template Name]

_Brief description of when to use this pattern_

## Template

[Copy-paste ready code/structure]

## Variations

- Common modifications
- Optional enhancements

## Usage Notes

- When to use vs alternatives
- Common mistakes to avoid
```

## Migration Strategy

### Phase 1: Foundation

1. Create directory structure
2. Document this pattern
3. Create role entry points

### Phase 2: Content Split

1. Split largest files first (by line count)
2. Maintain all existing workflows
3. Update cross-references continuously

### Phase 3: Optimization

1. Slim down CLAUDE.md
2. Validate file sizes
3. Test role-based navigation

## Success Metrics

- **File Size**: All files under target sizes
- **Discoverability**: Engineers can find relevant info in <30 seconds
- **Maintainability**: Updates affect minimal files
- **Completeness**: All existing workflows preserved
- **Usability**: Role guides provide clear next actions

## Future Enhancements

This pattern enables:

- Auto-generated index files
- IDE integration with snippets
- Workflow validation tooling
- Role-specific quick references
- Decision trees for complex choices

## Implementation Notes

- Only split content that exists today
- Preserve all current functionality
- Maintain backward compatibility during transition
- Update tooling to reference new locations
- Create validation scripts for consistency
