# Shared Workflows

_Common workflow components used across multiple development workflows_

This directory contains reusable workflow modules that are referenced by other workflows to reduce duplication and ensure consistency.

## Available Shared Workflows

| Workflow                            | Purpose                                             | Used By                   |
| ----------------------------------- | --------------------------------------------------- | ------------------------- |
| [Quality Gates](./quality-gates.md) | Standard TypeScript, linting, and test verification | All development workflows |

## Purpose

Shared workflows extract common patterns that appear across multiple workflows:

- Reduce duplication of instructions
- Ensure consistent quality standards
- Single source of truth for common processes
- Easier maintenance and updates

## How to Use

### From Other Workflows

Reference shared workflows using relative links:

```markdown
### Step 4: Run Quality Gates

Follow the [Quality Gates workflow](../shared/quality-gates.md) to verify your changes.
```

### Directly

Use shared workflows standalone when you need to:

- Quickly verify code quality
- Run standard checks before committing
- Understand quality requirements

## Contributing

When adding new shared workflows:

1. Identify patterns used in 3+ workflows
2. Extract to focused, reusable module
3. Update referencing workflows
4. Document usage and integration points
