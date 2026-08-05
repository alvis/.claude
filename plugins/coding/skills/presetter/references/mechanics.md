# Presetter consumer recipes

Load only the recipe matching the requested outcome.

## Adopt Presetter

1. Record the project's working build, lint, typecheck, test, scripts, and
   deliberate tool customizations as the comparison baseline.
2. Install `presetter` and at least one `@presetter/preset-*` package as
   development dependencies with the repository's package manager. Start a
   general TypeScript project with `@presetter/preset-essentials`; add only the
   runtime, framework, module, or quality presets it needs.
3. Write `presetter.config.ts`. Re-export the single preset when it is the whole
   stack; otherwise import `preset` from `presetter` and list the selected
   presets in `extends` from foundation to specialization.
4. Add `"bootstrap": "presetter bootstrap"` and the standalone task delegates
   the project needs, such as `"build": "run build"` and
   `"lint": "run lint --"`, to `package.json`. Preserve intentional local
   scripts; they override preset scripts with the same name.
5. Run the bootstrap script with the detected package manager. Inspect the
   materialized tool configs and merged scripts, then run the baseline checks.
   Express intentional differences in the stack instead of copying generated
   wrappers.

## Compose presets and overrides

1. Import `preset` from `presetter`; place the foundation first in `extends`,
   followed by runtime, framework, and quality capabilities in intentional
   order.
2. Put ordinary project settings in `variables` and additional commands in
   `scripts`. Keep package-local scripts when they intentionally override a
   preset script; local `package.json` scripts take priority.
3. Put inherited changes in `override`. Deep-merge object assets, use a
   current-value function when preserving upstream arrays or executable config,
   and set an asset to `null` when the stack must stop generating it.
4. Bootstrap the exact target and verify that each capability contributes the
   expected scripts, dependencies, and tool configuration.

## Target a monorepo

1. Use `@presetter/preset-monorepo` for the workspace baseline. Resolve the root
   config and each package config that extends or specializes it.
2. Select project-directory globs with `presetter bootstrap --projects` or
   package-name globs with `presetter bootstrap --packages`. Use `!` exclusions
   only to subtract from an explicit positive selection.
3. Confirm every selected package before accepting the run. Bootstrap the
   narrowest useful set and inspect all aggregated package failures.
4. Run package checks plus workspace consumers affected by shared scripts,
   project references, or generated test configuration.

## Author a custom preset

1. Create a package that exposes typed preset code and checked-in templates.
   Use `@presetter/types` for `PresetGenerator`, `ProjectContext`, and asset
   types; declare `presetter` compatibility and the tools the preset requires.
2. Return reusable `variables`, `scripts`, and `assets`. Use project context
   only for real package differences, merge current content when augmenting a
   file, and keep options small enough to preserve a recognizable convention.
3. Test default, option, conditional, and merge paths. Build the package and
   bootstrap it in a representative consumer; verify the resulting scripts and
   tool configs, not only the generator's return value.

## Migrate to v9

1. Preserve a working baseline and inventory existing Presetter dependencies,
   imports, script delegates, local overrides, and generated config behavior.
2. Rename legacy `presetter-preset-*` packages to `@presetter/preset-*`, rename
   `presetter-types` to `@presetter/types`, and import consumer `preset()` from
   `presetter`. Update dependencies with the detected package manager.
3. Adopt v9 script names such as `test:coverage` and `test:watch`; account for
   the TypeScript 6 baseline, strict defaults, and `noUncheckedIndexedAccess`
   before weakening a rule in an override.
4. Bootstrap only the migrated targets, compare generated assets and scripts
   with the baseline, then run typecheck, lint, test, and build.

## Regenerate after a stack change

1. Confirm the edited stack, affected packages, and authorized scope. Invoke
   the resolved local binary through the repository's bootstrap script.
2. Use `--projects` or `--packages` to constrain monorepo regeneration. Review
   selected targets, each generated asset, merged scripts, and aggregated errors.
3. Keep generated wrappers ignored when repository policy expects that. If a
   tracked local file occupies a generated path, preserve it until the stack or
   override explicitly resolves the ownership conflict.

## Troubleshoot a failed or surprising bootstrap

1. Reproduce one explicit target and retain its selected package, asset log,
   error, status, and diff.
2. Trace the selected target, owning config chain, `extends` order, variables,
   scripts, asset conditions, override pass, local file, dependency resolution,
   and ignore policy in that order.
3. For missing output, check whether the target matched, an asset was set to
   `null` or made conditional, a local file won, or the wrapper is ignored. For
   conflicts, check duplicate asset owners and merge-versus-replacement logic.
4. Check old unscoped imports and old script names during migration. Preset
   binaries enter composed script paths, but dynamically imported libraries may
   still require a direct consumer dependency.
5. Change the earliest stack, override, dependency, or selector that explains
   the evidence; bootstrap the same target and repeat its failed consumer check.
