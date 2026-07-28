# Output manifest and the final size loop

Read this when returning an artifact-writing skill's manifest, or when
combining manifests and running the end-of-run size pass.

Every artifact-writing skill returns explicit final paths it generated or
materially rewrote:

<report>

```yaml
generated_files:
  - /absolute/path/to/file.md
```

</report>

Writers finish all files and links before returning the manifest and never
measure or split independently. The coordinator combines and deduplicates
manifests, selects only absolute `.md` paths inside the resolved target
workspace's `.state/` (excluding any `working.md`), and runs exactly
one pass when eligible paths remain:

```bash
"$ESSENTIAL_ROOT/bin/check-markdown-size" \
  --engineering-root "$state_root/.state" \
  "${generated_md_files[@]}"
```

The checker canonicalizes the declared root and every path, excludes
traversal, symlink, and other-workspace escapes, and returns every eligible
file greater than 16,384 bytes together (12,288 bytes is authoring guidance
only). The gate does not apply outside `.state/`; the only separate
limit is the 2,000-byte injection limit for Essential's `AGENTS.md`,
`MAINAGENT.md`, and `SUBAGENT.md`.

On `split_required`, send all oversized files through one complete split
round — each original path remains a concise overview linking its lowercase
children — then rebuild the final manifest and run one subsequent batch
pass. The checker reports only `pass`, `split_required`, or `invalid`; it
never edits or splits files itself.
