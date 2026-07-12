---
name: sync-spec
description: Materialize a guaranteed-on-disk Notion specification tree as a flat `.code-spec/` bundle of `{kebab-title}-{32hex-id}.md` files plus `.gitignore`. Use before downstream analysis or code generation, when refreshing a stale bundle, or when a ticket requires local spec evidence; fail unless the root id-suffix file exists and is non-empty.
model: opus
context: fork
allowed-tools: Read, Grep, Glob, Bash, TodoWrite
argument-hint: "<notion-url-or-id> [--spec-path=<dir>]"
---

# Sync Spec

Download a Notion specification page tree to disk as a self-contained flat
Markdown bundle. Every invocation wipes and re-downloads — this skill never
caches, never merges, and never preserves prior contents.
`specification:sync-notion` owns bidirectional sync and conflict resolution;
`specification:spec-code` owns specification authoring.

## Boundaries

- Use for: downloading or refreshing a Notion spec page tree as a
  guaranteed-on-disk bundle before downstream review, audit, or code
  generation, or whenever a caller needs hard local spec evidence.
- Do not use for: pushing local edits to Notion or merging two sides
  (`specification:sync-notion`), authoring or updating spec content
  (`specification:spec-code`), or partial per-page pulls.
- There is no `--use-cache`, `--repo`, `--slug`, or sync-mode argument. The
  skill always wipes and re-downloads; callers wanting cache semantics (such
  as `specification:implement-code`) implement them on their side.

## Inputs

- **Required**: `<notion-url-or-id>` — full Notion URL or 32-hex page id;
  dashes are stripped during normalization.
- **Optional**: `--spec-path=<dir>` — bundle target directory. Default: walk
  up from the working directory to the first ancestor containing any of
  `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, or `go.mod` and use
  `<root>/.code-spec`; when no marker exists up to the filesystem root, fall
  back to `<cwd>/.code-spec`.
- **Prerequisites**: `notion-sync` CLI on PATH (verify with
  `notion-sync --help`), `NOTION_TOKEN` exported in the shell, and write
  access to the resolved directory.

## Workflow

1. Normalize the id: take the trailing URL segment, strip all dashes, and
   require exactly 32 hex characters (`/^[0-9a-f]{32}$/i`). On failure, refuse
   with `reason: invalid_id` before any disk mutation.
2. Resolve the absolute `spec_path` per the default above and record the
   project root. Safety-check that `spec_path` sits inside the resolved
   project root or under the working directory; on escape, refuse with
   `reason: spec_bundle_unavailable` without wiping anything.
3. Confirm `NOTION_TOKEN` is set; when unset, refuse with
   `reason: notion_unavailable`.
4. Wipe and recreate the target: `rm -rf <spec-path>` then
   `mkdir -p <spec-path>`. Unconditional — stale bundles, junk files, and
   partial downloads are always deleted so the result is a fresh mirror.
5. Run exactly one pull and capture its exit code:

   ```bash
   notion-sync pull <notion-id> --follow --out <spec-path>
   ```

   `--follow` walks children, databases, links, and files in a single pass
   (default depths: children 3, database 1, link 1 — deepen only when the
   caller explicitly asks). Optionally add `--bail` to fail fast on the first
   per-page error and `-c 25` for default concurrency. Never iterate per page
   across tool calls — recursion happens inside the CLI. The CLI writes flat
   `{kebab-title}-{32hex-id}.md` files plus `<spec-path>/.gitignore`
   (single line `*`).
6. Enumerate `<spec-path>/*.md` (flat — the CLI creates no subdirectories)
   and parse each filename's trailing `-{32hex}.md` segment as its page id;
   record any non-matching filename as an advisory issue.
7. Apply the hard gate below, then run the verification checks. When a check
   fails, fix the cause (for a transient pull failure, re-run step 5 once) and
   re-run that check; repeat until every check passes or a concrete blocker
   remains, then report the refusal instead of looping.

<IMPORTANT>
Root-spec persistence gate — the filesystem is authoritative, the CLI exit
code is advisory. The root file is the bundle entry whose 32-hex filename
suffix equals the input id; confirm it with `test -s <root-file>`.

| CLI exit | Root file present and non-empty | Outcome |
|----------|---------------------------------|---------|
| non-zero | any                             | `status: refused`, `reason: spec_bundle_unavailable` |
| 0        | no                              | `status: refused`, `reason: spec_bundle_unavailable` |
| 0        | yes                             | `status: completed` (per-page warnings go to `issues`) |

No `completed` status may ever be reported without the non-empty root file on
disk.
</IMPORTANT>

## Verification

- The root file whose filename suffix matches the input id exists and is
  non-empty.
- Every bundle file matches `-{32hex}.md` and `<spec-path>/.gitignore`
  exists; deviations are listed in `issues`.
- A refusal left no misleading state: `invalid_id` and the path-escape
  refusal wrote nothing; a failed pull is reported, never patched over.

## Completion

Always emit the report below — refusals included — so callers can branch on
it. On refusal, keep `outputs.notion.id` for correlation and null out the
bundle fields that never materialized.

<report>

```yaml
skill: sync-spec
status: completed | refused
# refusal reasons: invalid_id | notion_unavailable | notion_not_found | spec_bundle_unavailable
outputs:
  notion:
    id: '<32-char hex>'
    title: '<page title>'
  spec_bundle:
    spec_path: '<absolute path>'
    files:
      - path: '<path>/<kebab-title>-<32hex-id>.md'
        notion_id: '<32hex>'
issues: []
```

</report>
