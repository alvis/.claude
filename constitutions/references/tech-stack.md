# Tech Stack & Commands

## Table of Contents

- [Stack](#stack) `stack`
- [Essential Commands](#commands) `commands`
- [Import Rules](#import_rules) `import_rules`
- [Workspace](#workspace) `workspace`
- [Critical Rules](#critical) `critical`

<stack>
| Layer | Technology |
|-------|------------|
| **Language** | TypeScript ≥5.8 (ESM only) |
| **Backend** | Node 22 LTS, PostgreSQL/Prisma |
| **Frontend** | Next.js ≥15, React ≥19, Tailwind 4 |
| **Package Manager** | pnpm workspaces |
| **Testing** | Vitest (*.spec.ts) |
| **Linting** | ESLint + Prettier |
| **CI/CD** | GitHub Actions, Pulumi |
</stack>

<commands>

## Essential Commands

```bash
# Build
pnpm run build

# Test
pnpm run test -- --coverage
pnpm --filter <project> test

# Lint & Format
pnpm run lint

# Type Check
npm run typecheck

# Development
npm run dev
npm run storybook
```

## Database (Prisma)

```bash
npm run db:migrate    # Apply migrations
npm run db:push       # Push schema changes
npm run db:reset      # Reset database
npm run db:seed       # Seed data
```

</commands>

<import_rules>

* ALWAYS use `#*` subpath imports from package.json
* NO tsconfig path aliases
* Example: `import { emit } from '#emit';`
</import_rules>

<workspace>
* Dependencies organized in pnpm-workspace.yaml catalogs
* All packages use version 1.0.0
* Standard scripts: build, lint, test, coverage
* Prisma packages include db:* scripts
</workspace>

<critical>
* MUST maintain 100% test coverage
* Use `--reporter=github-actions` in CI
* ESLint/Prettier auto-fix - include in commits
* Each Prisma schema in separate file
</critical>
