# Handover-Doc Discovery Strategy

Use this strategy during Step 1 ("Diagnose Issues") to surface relevant context from markdown documentation in the project before planning fixes. Recent documents (by modification time) have higher priority; review findings take precedence for identifying what to fix; multiple sources strengthen confidence in fix requirements.

## 1. Find All Markdown Files

- Search project root for all markdown files: `**/*.md`
- Exclude common non-context files: `node_modules/`, `README.md`, `CHANGELOG.md`, `LICENSE.md`

## 2. Analyze Content to Identify Relevant Documents

Read each markdown file and analyze its content against the following five categories. A file may match more than one category.

### Review/Findings Documents

- **Keywords**: "review", "issues", "findings", "critical", "major", "minor", "violations"
- **Patterns**: Issue lists, severity levels, file references with line numbers

### Handover/Continuation Documents

- **Keywords**: "handover", "takeover", "continuation", "work in progress", "WIP", "next steps"
- **Patterns**: Task lists, pending work, blockers, decisions made

### Context Documents

- **Keywords**: "context", "current state", "progress", "status", "overview"
- **Patterns**: Current implementation state, recent changes, decisions

### Planning Documents

- **Keywords**: "plan", "todo", "tasks", "implementation", "roadmap", "checklist"
- **Patterns**: Numbered steps, task lists, requirements, milestones

### Research/Investigation Documents

- **Keywords**: "research", "investigation", "analysis", "findings", "options", "alternatives"
- **Patterns**: Options compared, decisions rationale, technical investigations

## 3. Extract Fix Requirements

From identified documents, extract:

- Known issues and their locations (file paths, line numbers)
- Required fixes and their priority/severity
- Architectural constraints and requirements
- Pending tasks related to discovered target files
- Blockers or decisions that inform fix direction

## 4. Prioritize Information

- Recent documents (by modification time) have higher priority
- Review findings take precedence for identifying what to fix
- Handover notes provide critical context for work continuation
- Multiple sources strengthen confidence in fix requirements
