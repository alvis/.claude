# React lint profile

## Eligibility

- Include `.tsx` and `.jsx` source files.
- Include `.stories.tsx` and `.stories.jsx` Storybook files.
- Include `.spec.tsx`, `.test.tsx`, `.spec.jsx`, and `.test.jsx` test files.
- A supplied specifier and scope still narrow this set.

## Standards

Add the React-owned standards under `plugins/react/constitution/standards/`:

- `accessibility`
- `components`
- `hooks`
- `project-structure`
- `storybook`

Apply `storybook` to story files. Apply testing standards to test files. All eligible files also receive the generic Coding standards supplied by `coding:lint`.

## Scanners

Run this React scanner after the generic Coding scanner:

```sh
plugins/coding/scripts/pyrun.sh plugins/react/scripts/scan_potential_violations.py <files> --category all --before 5 --after 10
```

## Exclusions

Exclude declaration files, generated files, snapshots, vendored files, dependencies, and build output. Do not include plain `.ts` or `.js` files solely because they are adjacent to eligible files.

## Report label

React lint
