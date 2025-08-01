# References Directory

_Quick lookup information and technical references_

This directory contains reference materials for quick lookup during development. References provide immediate access to commands, examples, and technical details without the full context of standards or workflows.

## Available References

### 📚 **Current References**

| Reference                               | Purpose                              | Content                                  |
| --------------------------------------- | ------------------------------------ | ---------------------------------------- |
| [Commit Examples](./commit-examples.md) | Git commit message patterns          | Good/bad examples, formatting rules      |
| [Tech Stack](./tech-stack.md)           | Technology commands and dependencies | Build commands, package info, tool usage |

### 🔄 **Planned References**

| Reference                                               | Purpose                        | Status        |
| ------------------------------------------------------- | ------------------------------ | ------------- |
| [TypeScript Quick Reference](./typescript-quick-ref.md) | Common TypeScript patterns     | _Coming Soon_ |
| [Testing Quick Reference](./testing-quick-ref.md)       | Test command and patterns      | _Coming Soon_ |
| [React Quick Reference](./react-quick-ref.md)           | Component and hook patterns    | _Coming Soon_ |
| [API Quick Reference](./api-quick-ref.md)               | HTTP status codes and patterns | _Coming Soon_ |

## Reference Categories

### 🛠️ **Tool Commands**

Quick access to commonly used commands:

- Build and development commands
- Testing and quality check commands
- Git workflow commands
- Package management commands

### 📋 **Code Snippets**

Ready-to-use code patterns:

- Common TypeScript patterns
- Frequently used React patterns
- Standard error handling snippets
- Testing boilerplate code

### 📊 **Technical Specs**

Quick lookup for technical details:

- HTTP status codes and meanings
- Git commit message formats
- Package.json configuration options
- Testing framework APIs

### 🎯 **Decision Trees**

Quick decision guides:

- When to use which testing approach
- Component vs. hook decision matrix
- Error handling strategy selection
- Performance optimization choices

## How to Use References

### 1. **During Development**

Quick lookup when you need specific syntax or commands.

### 2. **During Code Review**

Verify patterns and formats match established standards.

### 3. **During Onboarding**

New team members can quickly find common patterns and commands.

### 4. **During Troubleshooting**

Find correct syntax and configurations when debugging.

## Reference Principles

### ⚡ **Fast Access**

Information is organized for immediate lookup without extensive reading.

### 🎯 **Specific**

Each reference focuses on concrete, actionable information.

### 📋 **Complete**

References include all variations and common use cases.

### 🔄 **Up-to-Date**

References are maintained to reflect current tool versions and practices.

## Reference Format

### **Command References**

```bash
# Purpose: Brief description of what this accomplishes
command-name [options] [arguments]

# Examples:
npm run coverage
git commit -m "feat: add user authentication"
```

### **Code Pattern References**

```typescript
// Pattern Name: Brief description
interface PatternExample {
  property: type;
}

// Usage:
const example: PatternExample = { property: value };
```

### **Configuration References**

```json
{
  "setting": "value",
  "description": "What this setting controls"
}
```

## Cross-References

References connect to detailed information in other directories:

### **To Standards**

When you need the full technical requirements behind a reference pattern.

### **To Workflows**

When you need step-by-step guidance on using the referenced information.

### **To Patterns**

When you need complete implementation examples beyond the reference snippet.

## Quick Navigation

### **By Technology**

- **Git**: [Commit Examples](./commit-examples.md)
- **Node.js/npm**: [Tech Stack](./tech-stack.md)
- **TypeScript**: _Coming Soon_
- **React**: _Coming Soon_
- **Testing**: _Coming Soon_

### **By Use Case**

- **Starting Development**: [Tech Stack](./tech-stack.md) for setup commands
- **Making Commits**: [Commit Examples](./commit-examples.md) for message formats
- **Writing Code**: _TypeScript/React references coming soon_
- **Writing Tests**: _Testing reference coming soon_

### **By Role**

- **All Engineers**: [Commit Examples](./commit-examples.md), [Tech Stack](./tech-stack.md)
- **Frontend Engineers**: React and TypeScript references _(coming soon)_
- **Backend Engineers**: API and data operation references _(coming soon)_

## Need More Detail?

References provide quick answers, but for comprehensive information:

- **Complete technical requirements**: See [Standards](../standards/)
- **Step-by-step processes**: See [Workflows](../workflows/)
- **Implementation examples**: See [Patterns](../patterns/)
- **Project context**: See main [CLAUDE.md](../../CLAUDE.md)

## Contributing to References

When adding references:

1. **Keep it concise** - Focus on immediate, actionable information
2. **Include examples** - Show concrete usage patterns
3. **Stay current** - Verify information matches current tool versions
4. **Cross-reference** - Link to detailed information in other directories
5. **Test accuracy** - Ensure all commands and code snippets work

### Reference Quality Checklist

- [ ] Information is accurate and current
- [ ] Examples are tested and working
- [ ] Format is consistent with other references
- [ ] Cross-references are helpful and accurate
- [ ] Content is immediately actionable

Remember: References are for quick lookup - they provide immediate answers to common questions without requiring extensive reading or context.
