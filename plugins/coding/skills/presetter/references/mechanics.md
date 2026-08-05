# Presetter mechanics

Load this reference only when the task needs composition, custom preset
authoring, monorepo targeting, migration, or conflict diagnosis.

## Composition and overrides

A consumer config may re-export one preset or compose a stack with the
installed API. Common fields are `extends`, `variables`, `scripts`, `assets`,
and `override`, but package names and APIs vary by release. Follow the
installed types and neighboring configs.

Preserve `extends` order. Put shared defaults in the composed presets and keep
project-specific differences in the owning config. Asset and script functions
that receive current content should merge or patch it when upstream behavior
must survive; replace an asset only when the repository explicitly owns the
whole file. Root configs and child configs commonly form a chain: a child may
extend the root and specialize context-aware scripts or assets.

## Adoption and custom presets

Read the installed package's documentation and metadata to confirm the adoption
command and behavior. Invoke local help only after establishing that the binary
is already present and the help path is read-only. In releases that support it,
`presetter use <preset...>` records the preset choice and may bootstrap
immediately; treat it as mutating. `presetter bootstrap` applies the selected
source later. Do not repeat an existing lifecycle hook or remove local config
until its owner is established.

For a custom preset, keep the preset implementation, templates, package
metadata, compatibility declaration, and tests in checked-in package source.
Export the release-supported preset shape, use context only for genuine
package or repository differences, and test resolved assets in a representative
consumer. Do not test only the preset function in isolation when bootstrap
behavior is the requested outcome.

## Monorepos and migrations

Resolve the root config and every child config that composes into the exact
target. Derive selector syntax from the installed package first; invoke
`bootstrap --help` only when the existing local binary and that help path are
established as read-only. Some releases expose path and package-name selectors
such as `--projects` and `--packages`. Confirm the matched targets, then
bootstrap the narrowest explicit scope rather than the whole workspace.

For a version migration, compare the manifest constraint, lockfile resolution,
installed package metadata, types/exports, migration notes, and generated asset
set. Treat a proven-read-only local CLI version as corroboration, not a required
probe. Update source and dependencies with the detected package manager,
bootstrap the selected targets, and review the generated diff before widening
the scope. Never infer a migration from a version number alone.

## Conflicts and missing outputs

Trace a missing or conflicting result in this order:

1. target selection and package context;
2. owning config and `extends` order;
3. variables, scripts, asset conditions, and override pass;
4. existing local file and tracked/ignored policy;
5. preset dependency resolution and generated output.

Preset binaries may be made available to composed scripts while libraries
loaded through dynamic imports still resolve from the consumer project. When a
script fails to load a dynamic dependency, verify the consumer's direct
dependency and workspace resolution policy before changing the preset.

Treat an absent file as an ownership question first: the target may not have
matched, the asset may be conditional, a local file may intentionally win, or
the output may be ignored. Use the installed release's diagnostics and logs;
change the earliest source that explains the evidence, then regenerate the same
target.
