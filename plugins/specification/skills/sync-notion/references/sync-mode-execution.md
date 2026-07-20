# Sync Mode Execution Branches — Step 3

Load this reference during **Step 3 (Execute Sync Operations)** in `SKILL.md`. It contains the mode-specific execution recipes the sync subagent must follow based on the active `sync_mode`. Pick exactly one of the three branches below per pair.

All branches delegate transport to the `notion-sync` CLI. **Never iterate
per-page across tool-call turns** — use recursive `--follow*` flags so the CLI
walks the requested subgraph in one invocation. Preserve every path returned
by the CLI; never derive a filename from a page title or id.

## For sync_mode = 'local-to-notion'

1. **Push to Notion** (single CLI call):
   - `Bash: notion-sync push <file_path>`
     - Uses the file's frontmatter `ref:` to update the existing page.
     - For `CREATE_NEW` pairs, ensure the file has `parent: <database-or-page-id>` in frontmatter; the CLI creates the page and writes the resulting `ref:` back to the source file.
     - Add `--follow` when the local file references other declared local files
       that also need pushing in one operation.
2. **Record Sync Result**:
   - Sync direction: `local→notion`
   - Sync timestamp: current ISO timestamp
   - Notion URL: read from the (now-updated) file frontmatter `ref:`

## For sync_mode = 'notion-to-local'

1. **Pull from Notion** (single recursive CLI call):
   - `Bash: notion-sync pull <ref> --follow --out <staging-dir>`
     - `<ref>` = the resolved Notion URL or 32-hex id from Step 1.
     - One recursive call walks the page + its direct references; do **not** loop and pull each linked page across separate turns.
     - Verify the staged root by frontmatter `ref:` and the CLI report, then
       replace the declared output set. Specification transport files must be
       `.mdc`; returned relative paths stay unchanged.
2. **Record Sync Result**:
   - Sync direction: `notion→local`
   - Sync timestamp: current ISO timestamp

## For sync_mode = 'two-way-merge'

1. **Get Resolved Content**:
   - Step 2 produced explicit decisions and a merged content proposal. Apply
     authored `.mdc` content only through `Skill(mdc)`; do not use direct
     `Write`/`Edit` on an MDC body.
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
