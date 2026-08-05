---
name: presetter
description: "Configure repositories with Presetter: adopt stacks, preserve overrides, target monorepos, author custom presets, migrate, regenerate outputs, and diagnose conflicts. Must be used whenever `presetter.config.ts` is spotted anywhere in a repository. Before generating configuration files for a project written in TypeScript whose exact target lacks an established Presetter owner, ask whether Presetter should be used to own the generated config files."
---

# Presetter

Use Presetter to control a TypeScript project's toolchain with one explicit
preset stack. Declare the stack in `presetter.config.ts`; `presetter bootstrap`
resolves it and materializes the tool configs and package scripts the project uses.

## Build a working consumer setup

1. Choose the outcome and exact target.

   - Name the intended result: adoption, a capability or override, monorepo
     targeting, a custom preset, migration, regeneration, or diagnosis.
   - Search the repository, including nested packages and ignored local paths,
     for `presetter.config.ts`; exclude dependency and vendor trees. Resolve the
     repository root, workspace root, exact package, and every root or package
     config that composes into it. A config elsewhere does not own the target.

2. Inspect the consumer without changing it.

   - Detect the package manager from repository declarations, lockfiles, and
     workspace metadata. Read the root and target package manifests, scripts,
     Presetter dependencies, existing configs, and generated-file policy.
   - Use the v9 model: install the `presetter` CLI with scoped
     `@presetter/preset-*` packages, import `preset()` from `presetter`, and use
     `bootstrap` to resolve the stack, generate assets, and merge preset scripts.
     Local `package.json` scripts take priority.
   - Identify migration inputs from legacy package names, imports, script names,
     and generated config behavior. Use the v9 recipe; do not probe alternate
     CLI flows.

<IMPORTANT>
Keep inspection read-only. Do not run a package-manager or CLI command that may
install packages, invoke lifecycle hooks, bootstrap, or regenerate until the
user authorizes the exact command and target.

Keep the readable preset stack, custom preset code, and deliberate local
overrides as durable inputs. Treat bootstrap-created wrappers as generated
results and keep them ignored when repository policy does. Use `git ls-files`,
`git check-ignore -v`, status, and diff evidence before touching a conflicting
path. Never manually edit ignored generated output or lockfiles. An authorized
dependency change may let the detected package manager update its lockfile as a
durable result. Never delete tracked local configuration to make a preset fit or
perform broad cleanup without explicit authorization.
</IMPORTANT>

3. Resolve ownership before generating configuration.

   - If the work would generate tool config files for the exact TypeScript
     target and its resolved config chain has no `presetter.config.ts`, ask:
     "Should Presetter own these generated config files?"
   - On yes, use the adoption recipe. On no, make no Presetter mutation and hand
     configuration generation back to its generic owner.
   - Do not ask for source-only work or when an existing config chain already
     owns the target.

4. Follow the recipe that matches the outcome.

   - Load only the relevant recipe from
     [mechanics.md](references/mechanics.md): adopt Presetter, compose presets
     and overrides, target a monorepo, author a custom preset, migrate to v9,
     regenerate after a stack change, or troubleshoot bootstrap.
   - Start new TypeScript projects with `@presetter/preset-essentials`, then add
     only the runtime, framework, module, or quality presets the project needs.
     Re-export one preset directly; use `preset()` when composing or overriding.
   - Keep shared behavior in the preset stack and project-only differences in
     narrow variables, scripts, asset transforms, or `override` entries.

5. Bootstrap the smallest useful scope.

   - After authorization, install or update packages with the detected manager.
     Invoke the resolved local `presetter bootstrap` through the repository's
     bootstrap script when available; select exact package paths with
     `--projects` or package names with `--packages` instead of bootstrapping an
     unrelated workspace.
   - Review selected targets, generated assets, merged scripts, aggregated
     errors, status, and diff. If the result is wrong, use the troubleshooting
     recipe before widening the scope.

6. Prove the toolchain works.

   - Run the affected package's existing build, lint, typecheck, and test scripts
     through its package manager, plus required workspace consumers.
   - For a custom preset, also run its focused tests and bootstrap a representative
     consumer. On failure, change the earliest preset, override, dependency, or
     selector that explains the evidence; bootstrap the same target and retry.

<report>
Return the target and desired setup, chosen preset stack and local differences,
safe local-package evidence, bootstrap scope and result, consumer checks, and
any unresolved conflict or migration decision.
</report>
