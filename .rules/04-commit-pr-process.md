# Commits, Branches & PRs

## Conventional Commits

```plain
<type>(<scope>): <summary>   # ≤ 72 chars, imperative

<body>

<footer>
```

### Message Title

Types: `feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert`

- **feat**: Introduces a new feature
- **fix**: Fixes a bug (including dependency upgrades for bug fixes)
- **docs**: Documentation updates
- **style**: Code formatting, white-space, etc. (no functionality change)
- **refactor**: Code changes that neither fix a bug nor add a feature
- **perf**: Performance improvements
- **test**: Adding or fixing tests
- **build**: Changes affecting the build system (e.g., `webpack`, `docker`)
- **ci**: Changes to CI configuration and scripts
- **chore**: Routine tasks like upgrading dependencies that don't affect production code
- **revert**: Reverts a previous commit

Guidelines:

- Scope = directory/module (optional)
  - ✅ `fix(client/web-talent): correct broken link`
  - ✅ `feat(service/profile): add new job type filter`
  - ✅ `chore: update TypeScript to v5.5` (omit scope if not relevant)
- Try to limit the commit title to 50 characters (72 max)
- Use present-tense, imperative mood (✅ add, fix, refactor ❌ added, fixed, refactored)
- Reference issue or PR numbers in title if helpful — `(#123, #456)`

### Message Body

- Wrap at 72 characters
- Keep it short but descriptive
- If the change requires more detail, add a body or BREAKING CHANGE section

### Message Footer

- Mention closed issues with `Closes #<issue-number>, #<issue-number>...` (use commas, not "Fixes")

## Branch naming

`<type>/<scope>/<topic>` — lowercase‑kebab

Examples:

- `feat/web-talent/add-new-job-type`
- `chore/web-talent/update-dependencies`
- `test/profile/add-new-test`
- `docs/web-talent/update-readme`
- `style/web-talent/fix-typo`
- `chore/speedup-eslint`

Use lowercase letters and hyphens to separate words. Avoid using underscores or camelCase.

## Pull Requests

A well-structured Pull Request (PR) helps reviewers and future developers understand, verify, and maintain code changes. Use the following structure for all PRs:

### PR Title

- Use the same format as commit messages, e.g.
  - `feat(api): add support for user analytics export`

### PR Description

- Stay clear and professional
- Keep each section focused and concise
- Link to code, tickets, specs, or discussions
- Explain non-obvious decisions or technical details
- Make it easy for reviewers and future maintainers to follow and understand
- Use paragraphs for longer explanations in general, but use point form if points are short, related and best expressed as a list (e.g., checklist, breaking changes, etc.)
- Require Summary, and Checklist sections
- Ignore any sections that have no content (including none or n/a)
- A sentence should start with a capital letter
- Ignore a fullstop at the end of a bullet point
- Use the following structure:

```markdown
### 📌

**> In plain language, explain the purpose of the PR and its main changes in less than 3 sentences.**

- Use the format `**> <description>**` to make it stand out

### 📝 Context

Include any relevant context or background information that helps reviewers understand the change, e.g.

- Why is this change needed? Any problems or symptoms?
- Links to the related bug tickets?
- What problem does it solve? and Why?
- Any relevant background or design considerations

### 🛠️ Implementation

Describe what has been implemented

- Any features implemented
- Outline how the solution was achieved
- Any trade-offs, architectural choices, or design patterns

### ✅ Checklist

List all necessary and relevant (e.g. omit tests for only documentation changes) checks to be completed before the PR can be merged, e.g.

- [ ] Code adheres to style guide
- [ ] Unit tests added/updated
- [ ] Documentation updated
- [ ] Manually tested

### 💥 Breaking Changes

List any breaking changes introduced by this PR

- Note if there are any changes that might break existing functionality
- Include upgrade or migration instructions if relevant
- Omit this section if there are no breaking changes

### 🔗 Related Issues

Reference related tickets, issues, RFCs, discussions, e.g.

- `Closes #123, See #456, Spec: [Notion doc](https://...)`
- Omit this section if there are no related issues

### 🧪 Manual Testing

If applicable, describe how to manually test the changes, including

- Steps or instructions for a reviewer to manually verify the change
- Screenshots or screencasts if relevant
- Include this section only if a developer needs to manually test the changes

### 📋 Additional Notes

List any other information useful for reviewers or future maintainers, e.g.

- Known issues, temporary limitations, future follow-ups
- Omit this section if there are no additional notes
```

Keep unused sections _omitted_

--- END ---
