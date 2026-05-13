# Sync Mode Execution Branches — Step 3

Load this reference during **Step 3 (Execute Sync Operations)** in `SKILL.md`. It contains the mode-specific execution recipes the sync subagent must follow based on the active `sync_mode`. Pick exactly one of the three branches below per pair.

All branches delegate to the `notion-sync` CLI. **Never iterate per-page across tool-call turns** — use the recursive `--follow*` flags so the CLI walks the entire subgraph in a single invocation.

## For sync_mode = 'local-to-notion'

1. **Push to Notion** (single CLI call):
   - `Bash: notion-sync push <file_path>`
     - Uses the file's frontmatter `ref:` to update the existing page.
     - For `CREATE_NEW` pairs, ensure the file has `parent: <database-or-page-id>` in frontmatter; the CLI creates the page and writes the resulting `ref:` back to the source file.
     - Add `--follow` when the local file references other local files (via `parent:` chains) that also need pushing in one go.
2. **Record Sync Result**:
   - Sync direction: `local→notion`
   - Sync timestamp: current ISO timestamp
   - Notion URL: read from the (now-updated) file frontmatter `ref:`

## For sync_mode = 'notion-to-local'

1. **Pull from Notion** (single recursive CLI call):
   - `Bash: notion-sync pull <ref> --follow-children --follow-links --out <dir>`
     - `<ref>` = the resolved Notion URL or 32-hex id from Step 1.
     - One recursive call walks the page + its direct references; do **not** loop and pull each linked page across separate turns.
     - Files are written as `{kebab-title}-{32hex-id}.md` under `<dir>`.
2. **Record Sync Result**:
   - Sync direction: `notion→local`
   - Sync timestamp: current ISO timestamp

## For sync_mode = 'two-way-merge'

1. **Get Resolved Content**:
   - The merged content for this pair has already been written to the local file by Step 2 (`references/two-way-merge.md`). The local file now represents the agreed-upon state.
2. **Push merged state to Notion** (single CLI call):
   - `Bash: notion-sync push <file_path>`
     - Uses frontmatter `ref:` (existing page) or `parent:` (CREATE_NEW). For CREATE_NEW, the CLI writes back the new `ref:`.
     - Add `--follow` if other locally-modified files in the merge set also need pushing.
3. **Record Sync Result**:
   - Sync direction: `merged→both`
   - Sync timestamp: current ISO timestamp
   - Notion URL: read from the file frontmatter `ref:` after push.

**Handle Skipped Conflicts** (only for two-way-merge):
- If the merged local file contains TODO markers for skipped conflicts:
  - Document these in sync notes
  - Mark sync as `partial` success
  - User must manually resolve later
