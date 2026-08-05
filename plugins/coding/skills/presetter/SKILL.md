---
name: presetter
description: "Configures Presetter in consumer repositories: adopts or migrates Presetter, composes or authors presets, targets monorepo packages, manages generated assets, and diagnoses conflicts. Use whenever the target repo contains presetter.config.ts, or for Presetter bootstrap, overrides, custom presets, or missing generated configs; ask before generating TypeScript config without established Presetter ownership. Exclude engine internals, generic config, documentation-only, and pull-request work."
---

# Presetter

Manage Presetter as a consumer-facing configuration system while keeping
checked-in preset intent distinct from the outputs it generates. Derive every
command and API choice from the target repository and its installed Presetter
version.

Applicable standards: `universal/write`, `documentation/write`, and
`file-structure` for new or moved files.

## Boundaries

- Use this skill as the required first routing and inspection step whenever
  `presetter.config.ts` appears anywhere in the target repository, including a
  nested package, even when the requested change sounds like generic config
  work. After inspection, route work with no Presetter-owned effect to the
  appropriate coding skill; this gate does not make generic config in scope.
- Use for requests such as “adopt Presetter in this package,” “compose the
  React and strict presets,” “add a local Presetter override,” “author a shared
  custom preset,” “bootstrap only these workspace packages,” “migrate this
  Presetter setup,” or “find why Presetter stopped generating this config.”
- If the exact TypeScript target has no established Presetter owner and the
  requested work would generate configuration files, ask the user whether
  Presetter should own them before generating anything. A “no” answer routes
  to the appropriate generic configuration skill; a “yes” answer starts
  adoption.
- Do not use for “enable strict mode in tsconfig” or other generic TypeScript,
  ESLint, test, or package configuration with no Presetter ownership; route to
  the coding skill matching the requested implementation or fix.
- Do not use for changing Presetter's engine, resolver, CLI, or built-in preset
  implementation; use `coding:write-code` or `coding:fix`. A repository-owned
  custom preset consumed by projects remains in scope here.
- Do not use for documentation-only changes (`coding:document`) or creating,
  updating, reviewing, or merging a pull request (`coding:pr`).

## Inputs

- **Required**: target repository or package and the intended adoption,
  composition, override, preset, migration, targeting, or diagnosis outcome.
- **Optional**: desired preset packages, affected workspace packages, generated
  assets, and local behavior that must survive.

## Inspect before acting

1. Search the entire target repository for `presetter.config.ts`, including
   nested packages and ignored local files while excluding dependency/vendor
   trees. If any match exists, keep this skill as the routing gate and inspect
   every matching config that can affect the target.
2. Resolve the repository root, workspace root, and exact target package. Read
   the package-manager declaration, lockfiles, workspace configuration, root
   and target `package.json` files, scripts, dependencies, package name, and
   relevant sibling packages. Use only the detected manager for installs,
   dependency queries, local binaries, and scripts. Determine whether the
   exact target has a package-local config or is reached through a root/ancestor
   config; a config elsewhere that does not compose into this target is
   unrelated and does not establish Presetter ownership for it.
3. If the requested work would generate TypeScript configuration files for the
   exact target and no Presetter owner was established in step 2, stop and ask
   the user whether Presetter should be used; do not generate files before that
   answer. A “no” answer routes to the appropriate generic configuration skill.
4. Establish the effective Presetter version from the target's manifest range,
   lockfile resolution or manager-native dependency query, and the local CLI's
   version output. If these disagree or the package is not installed, resolve
   that ambiguity before relying on an API or running bootstrap.
5. Find every `presetter.config.ts` that can own the target, from workspace root
   through package-local config. Trace imports and `extends` in order, then map
   `variables`, `scripts`, `assets`, `override`, context-dependent functions,
   and custom preset sources. Read installed Presetter types, package exports,
   README or migration notes, and `--help` for the resolved version instead of
   copying syntax from a different release.
6. Classify each affected file as checked-in preset source, repository-owned
   local configuration, or generated output. Use repository policy,
   `git ls-files`, `git check-ignore -v`, status/diff evidence, generation
   headers, and Presetter logs; a familiar filename does not prove ownership.
   Inventory existing config files, package scripts, asset transformers, and
   comments that encode deliberate local overrides.

<IMPORTANT>
Preserve checked-in preset source and deliberate local overrides. Never edit a
lockfile by hand, treat an ignored generated output as the source of truth,
delete or replace a tracked local config merely because a preset emits the same
path, or run `unset` or broad cleanup without explicit authorization. Fix the
owning preset/config and regenerate the smallest selected scope.
</IMPORTANT>

## Implement

### Adopt or compose presets

1. Capture the current build, lint, type-check, test, scripts, config files,
   and generated-file policy as the migration baseline. Choose presets already
   compatible with the resolved Presetter version and the target's actual
   runtime, module, framework, and workspace shape.
2. Install Presetter and preset packages with the detected package manager.
   Create or update the nearest owning `presetter.config.ts`; keep shared
   behavior in ordered `extends` composition and express project-specific
   differences as narrow variables, scripts, assets, or `override` entries.
   Preserve a direct preset re-export when no composition or override is needed.
3. When modifying an existing asset or script, prefer the installed version's
   supported current-value transformer or merge utility so unrelated upstream
   content survives. Replace a complete asset only when replacement ownership
   is intentional and recorded in source.
4. Invoke `bootstrap` through the repository's local Presetter binary and
   detected package manager. Review its selected projects and asset log before
   accepting generated changes.

### Author a custom preset

1. Put reusable preset behavior in checked-in package source, not in generated
   consumer output. Match a compatible installed preset package's exports,
   module format, types, and tests; declare Presetter compatibility in package
   metadata according to neighboring preset packages.
2. Export a named preset using the installed API. Keep reusable defaults in
   variables, scripts, and assets; use context only for genuine repository or
   package differences; reserve the override pass for intentional changes to
   composed content. Keep large templates as checked-in preset assets.
3. Test resolved preset content and bootstrap it in a representative consumer.
   Verify both default behavior and each conditional or merge path.

### Target monorepos and migrate versions

1. Determine whether the root preset, a package preset, or an explicit chain
   owns each target. Read the installed CLI help for project-path and
   package-name selectors; pass the narrowest explicit selector and confirm its
   matches before changing multiple packages.
2. For migration, record the working pre-migration checks and generated asset
   set, then read migration notes, types, exports, and CLI help for the version
   actually being installed. Update dependencies with the detected manager,
   migrate checked-in preset source and local overrides, bootstrap only the
   intended targets, and compare the resulting asset set and scripts with the
   baseline. Do not infer migration steps from a time-sensitive version number.

### Diagnose conflicts or missing assets

1. Reproduce with the local installed CLI against one explicit target and
   retain the target list, asset log, error, and post-run status/diff. Enable
   diagnostics only through mechanisms supported by that installed version.
2. Trace evidence in resolution order: selected target and owning config,
   ordered presets, conditional context, initial variables/scripts/assets,
   override pass, existing local file, and generated-file policy.
3. For missing output, verify that the target matched, the preset and any
   dynamic dependency resolve from that package, the asset exists for the
   installed version, its condition passed, no local file owns the path, and
   ignore/cleanup policy did not hide or remove it. For conflicts, compare
   composition order, duplicate asset owners, merge-versus-replacement
   semantics, local scripts/config, and stale output from an earlier bootstrap.
4. Change the earliest authoritative source that explains the symptom,
   re-bootstrap the same bounded target, and confirm the evidence changed as
   predicted. If ownership or expected output remains ambiguous, stop with the
   competing owners and evidence instead of forcing a generated file.

## Verification

- Re-run bootstrap through the local installed version for every affected
  target; confirm the selected packages, expected asset set, script resolution,
  tracked/ignored state, and absence of unrelated workspace changes.
- Run the repository's own existing build, lint, type-check, and test scripts
  with its detected package manager for every affected package and required
  workspace-level consumer. Do not substitute invented generic commands for
  repository scripts.
- For a custom preset, run its focused tests and a representative consumer
  bootstrap in addition to the repository checks.
- When a check fails, fix the authoritative preset source, composition,
  dependency, selector, or local override; re-bootstrap the same scope and
  re-run the failed repository check until clean or concretely blocked.

## Completion

<report>

Report the resolved root and target packages, package manager, installed
Presetter version evidence, config ownership/composition chain, checked-in
source changed, generated outputs observed with tracked/ignored ownership,
bootstrap command and scope, repository checks run with results, and unresolved
conflicts or migration decisions.

</report>
