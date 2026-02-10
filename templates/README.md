# Constitution Templates

This directory contains templates for creating new constitution documents. Use these templates to maintain consistency across all documentation.

## Available Templates

### 📋 workflow.md

**Purpose**: Template for creating new workflow documents in `constitutions/workflows/`

Use this template when you need to document:

- Step-by-step processes for completing tasks
- Development workflows (coding, testing, deployment)
- Review and verification procedures
- Quality assurance processes

**Key Sections**:

- Purpose, When to use, Prerequisites
- Expert Role definition
- Numbered steps with examples
- Tool recommendations
- Standards to follow (mandatory)
- Quality gates/verification
- Common issues and solutions

### 📐 standard.md

**Purpose**: Template for creating new standards documents in `constitutions/standards/`

Use this template when you need to document:

- Coding conventions and patterns
- Technical requirements and specifications
- Best practices and anti-patterns
- Security and performance guidelines

**Key Sections**:

- Core principles
- Topic areas with examples
- Patterns and anti-patterns
- Quick reference tables
- Testing standards
- Migration guides

### 🤖 agent.md

**Purpose**: Template for defining AI agent personas in `.claude/agents/`

Use this template when you need to create:

- Specialized agent roles
- Agent capabilities and expertise
- Collaboration protocols
- Tool access definitions

### 🔧 command.md

**Purpose**: Template for creating slash commands in `commands/`

Use this template when you need to create:

- Custom slash commands for common tasks
- Automated workflows triggered by commands
- Tool orchestration commands
- Batch operations

## Usage Guidelines

### For Workflows

1. **Start with workflow.md** when documenting any process
2. Replace all `[placeholders]` with specific content
3. Include concrete examples for every step
4. Reference relevant standards as MANDATORY
5. Define clear verification criteria

### For Standards

1. **Start with standard.md** when documenting requirements
2. Focus on WHAT should be done (workflows cover HOW)
3. Include both good (✅) and bad (❌) examples
4. Provide quick reference tables for easy lookup
5. Include migration guides when replacing old patterns

### Workflow vs Standard

| Aspect | Workflow | Standard |
|--------|----------|----------|
| **Focus** | HOW to do something | WHAT the rules are |
| **Structure** | Sequential steps | Topic-based sections |
| **Examples** | Step-by-step commands | Patterns and anti-patterns |
| **Verification** | Quality gates and checks | Compliance checklists |
| **When to use** | Specific task triggers | General requirements |

## Template Selection Guide

```
Need to document a process? → workflow.md
Need to define rules/patterns? → standard.md
Need to create an AI agent? → agent.md
Need to create a command? → command.md
```

## Best Practices

### When Creating Workflows

- ✅ Make steps actionable and specific
- ✅ Include tool recommendations for each phase
- ✅ Reference standards as mandatory requirements
- ✅ Define measurable success criteria
- ✅ Document common failure scenarios

### When Creating Standards

- ✅ Be prescriptive about requirements
- ✅ Explain the WHY behind each rule
- ✅ Provide code examples for every guideline
- ✅ Include quick decision matrices
- ✅ Define enforcement mechanisms

### General Guidelines

1. **Keep AI instructions** - Don't remove the `<!-- INSTRUCTION -->` comments
2. **Maintain consistency** - Follow the same structure as existing documents
3. **Be complete** - Replace ALL placeholders with real content
4. **Test examples** - Ensure all code examples are correct
5. **Cross-reference** - Link to related workflows and standards

## File Naming Conventions

### Workflows

```
constitutions/workflows/[category]/[verb]-[noun].md
Examples:
- build-service.md
- review-code.md
- verify-auth-scope.md
```

### Standards

```
constitutions/standards/[category]/[topic].md
Examples:
- typescript.md
- testing.md
```

## Maintenance

- Review templates quarterly for updates
- Keep AI instruction comments current
- Update examples to match current practices
- Add new optional sections as patterns emerge
- Ensure templates reflect actual document structures
