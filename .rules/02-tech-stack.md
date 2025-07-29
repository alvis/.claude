# Tech Stack & Tooling

| Layer           | Choice                                                     |
| --------------- | ---------------------------------------------------------- |
| **Language**    | TypeScript ≥ 5.8 (ESM only)                                |
| **Backend**     | Node 22 LTS, PostgreSQL via Prisma                         |
| **Frontend**    | Next.js ≥ 15, React ≥ 19, Tailwind 4, DaisyUI 5, Storybook |
| **Pkg mgr**     | pnpm workspaces                                            |
| **Tests**       | Vitest (unit `*.spec.ts`, integration `*.integration.ts`)  |
| **Lint/Format** | ESLint (custom + SonarJS) & Prettier                       |
| **CI/CD**       | GitHub Actions; deploy via Pulumi                          |

## Package Management

```bash
# Jump to a workspace folder by name:
cd "$(pnpm list -r --depth -1 --json \
  | jq -r '.[] | select(.name=="<project-name>").path')"
```

## Commands Reference

```bash
# Build
pnpm run build                  # root = all projects; inside project = scoped

# Testing
pnpm run test -- --coverage     # run all tests in monorepo (from root)
pnpm --filter <project> test -- --coverage --reporter=github-actions # run all tests in a project
pnpm --filter <project> test -- --coverage --reporter=github-actions path/to/file.spec.ts  # specific file
pnpm --filter <project> test -- --coverage --reporter=github-actions file1.spec.ts file2.spec.ts  # multiple files

# Linting & Formatting
pnpm run lint                   # run lint for entire monorepo (from root)
pnpm --filter <project> lint    # lint + format specific project

# Type Checking
npm run typecheck               # if available in project

# Development
npm run storybook               # component docs (in web clients)
```

## Import Paths

- Use `#*` aliases (defined in package.json subpath imports)
- No tsconfig.json path aliases

## Workspace Management

### Workspace Catalogs

Dependencies are organized in catalogs by category in `pnpm-workspace.yaml`:

```yaml
catalog:
  ai: # AI/ML libraries
  aws: # AWS services
  cli: # Command line tools
  courier: # Communication services
  data: # Database and data processing
  fs: # File system utilities
  payment: # Payment processing
  # ... other categories
```

This ensures consistent versioning across the monorepo and simplifies dependency management.

### Package.json Patterns

All packages follow standardized conventions:

```json
{
  "version": "1.0.0", // All packages use same version
  "scripts": {
    "build": "...",
    "coverage": "...",
    "lint": "...",
    "prepare": "...",
    "prepublishOnly": "..."
  },
  "imports": {
    "#*": "./source/*" // Subpath imports with # prefix
  },
  "publishConfig": {
    "imports": false // Remove imports field for published packages
  }
}
```

### Prisma Database Commands

Prisma-based packages include additional database scripts:

```json
{
  "scripts": {
    "db:env": "Load database environment",
    "db:migrate": "Apply database migrations", 
    "db:push": "Push schema changes to database",
    "db:reset": "Reset database to clean state",
    "db:seed": "Populate database with seed data"
  }
}
```

## Important Notes

- **Database**: PostgreSQL via Prisma (each schema in its own file)
- **Auto-fixing**: ESLint and Prettier automatically fix issues - include their changes in commits
- **Test reporters**: Use `--reporter=github-actions` in CI environments
- **Coverage**: Maintain 100% coverage (excluding barrel files with `/* v8 ignore start */`)

--- END ---
