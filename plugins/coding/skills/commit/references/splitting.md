# Standard Splitting Mode (no `--retrospective`)

Active when `--retrospective` is NOT set. Use this reference for Step 1.3 classification, dependency-tree ordering, and the self-containment / incremental-evolution rules that govern multi-commit splits.

## Splitting heuristic — group by

| Priority | Split by | Example commits |
|----------|----------|-----------------|
| 1st | Infrastructure vs features | `init: lay the foundation` separate from feature code |
| 2nd | Module / feature boundary | `feat(auth): add login` vs `feat(search): add query` |
| 3rd | Change type within a module | `feat(auth): add login` vs `docs(auth): add API docs` |

## What goes TOGETHER in one commit

- Feature implementation + its unit/integration tests
- A type/interface + the code that uses it + tests for that code

## What gets SEPARATE commits

- Configuration & tooling (package.json, tsconfig, eslint, CI/CD)
- Different features/modules (each feature = its own commit with its tests)
- Standalone documentation not tied to a specific feature commit
- Shared types/interfaces that serve multiple features (commit before the features that use them)

## Dependency tree ordering

After classifying files into groups, build a dependency tree between the groups:

1. Analyze imports/requires across groups to determine which groups depend on which
2. Topologically sort the groups -- leaf nodes (no dependencies) are committed first, root nodes (depended on by nothing) last
3. Each commit must only import/use code from commits that come BEFORE it in the chain
4. If a circular dependency exists between groups, merge them into one commit

## Self-containment through incremental file evolution

Shared files (package.json, tsconfig.json, config files) must NOT be committed as their final version in the first commit. Instead, each commit includes only the entries relevant to what it introduces.

- **Shared files evolve incrementally**: Each commit adds only the entries it introduces to shared files. The init commit contains the minimal viable version; later commits modify shared files to add their entries.
- **No forward references**: A commit must NEVER reference code, modules, paths, imports, or exports that don't exist yet in the chain. If a commit mentions it, it must exist at that point.
- **Modify files to achieve this**: You MUST modify file contents to make each commit self-contained. This includes removing entries from package.json that reference future code, removing imports for future modules, and trimming config to match what exists.
- **Config files go with their feature**: `vitest.config.e2e.ts` goes with the e2e test commit, not the init commit. The `bin` field in package.json goes with the CLI commit.

Concrete examples of incremental evolution:

- **package.json in init commit**: Only basic metadata, dependencies, and scripts -- NO `bin`, NO feature-specific `exports`, NO module-specific subpath imports
- **package.json in feat(cli) commit**: ADD `bin` field, ADD `exports["./cli"]`
- **package.json in feat(pull) commit**: ADD `exports["./pull"]` or `imports["#pull"]` if applicable
- **tsconfig.json**: Only include paths that exist at that commit point
- **vitest.config.ts**: Only the base test config in init; e2e-specific config added with e2e commit
- **package.json `dependencies` in init commit**: Only packages actually imported by init-commit code -- NO packages used exclusively by future feature commits
- **package.json in feat(api) commit**: ADD `dependencies` entries (e.g., `node-fetch`, `bottleneck`) that this feature's code imports
- **package.json in feat(cache) commit**: ADD `better-sqlite3` to `dependencies` -- each commit introduces only the packages its own code requires
- **Lock file** (`pnpm-lock.yaml` / `package-lock.json` / `yarn.lock`): Regenerated in EVERY commit that modifies `dependencies` or `devDependencies` -- run the package manager's lockfile-only install command (e.g., `pnpm install --ignore-scripts`) and include the lock file change in the same commit
- **pnpm `allowBuilds`**: When a newly added package requires native build scripts (e.g., `better-sqlite3`, `esbuild`, packages using `node-gyp` or `prebuild-install`), add it to `allowBuilds` in `pnpm-workspace.yaml` in the same commit. See https://pnpm.io/settings#allowbuilds
