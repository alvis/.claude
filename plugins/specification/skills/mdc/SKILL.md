---
name: mdc
description: Read, edit, and author Notion-backed MDC files safely with native text tools while preserving @theriety/mdc grammar and ref identity. Use for any authored .mdc body change. Keep transport, pairing, and conflict orchestration in sync-notion and sync-spec.
model: sonnet
allowed-tools: Read, Edit, Write, Grep, Glob, Bash(ls:*), Bash(cat:*), Bash(*/bin/resolve-engineering-workspace:*), Bash(bash ${CLAUDE_PLUGIN_ROOT}/skills/mdc/scripts/*)
argument-hint: "[<path-to-.mdc>] [--mode=read|edit|author]"
---

# MDC

Safely read or author Notion-backed MDC (`@theriety/mdc`) while preserving its
block tree, annotations, refs, closing markers, and YAML frontmatter.

## Boundaries

- This is the only skill that authors `.mdc` body content. `notion-sync` may
  materialize transport files or update pairing metadata through
  `specification:sync-notion`, but callers must not hand-edit MDC.
- `.mdc` is reserved for Notion-backed files. In engineering work, those files
  live in the resolved default workspace's `.engineering/notion/` mirror or an
  active workspace's `.engineering/work/<work-id>/spec/` materialization.
- Do not derive or rename notion-sync paths, sync to Notion, or promote durable
  `docs/specs/` content here.
- Refuse a non-`.mdc` target, ambiguous edit location, or operation requiring
  the parser runtime rather than safe text editing.

## Inputs

- **Required**: target `.mdc` path, or destination plus content for authoring.
- **Optional**: `--mode=read|edit|author`; otherwise infer from existence and
  request verb.

## Mandatory invariants

<IMPORTANT>
1. Indent exactly two spaces per nesting level; never introduce tabs.
2. A block annotation is immediately adjacent to its target block.
3. Frontmatter, when present, starts at byte zero and is valid YAML.
4. Annotation bodies are YAML object syntax and close on the same line.
5. Inline annotations immediately follow `]` or `)`.
6. Every closing marker is `--{ ref: <name> }--`, matches the opening ref, and
   has the opening block's indentation.
7. Preserve required escapes outside parser-opaque fenced code.
</IMPORTANT>

Full grammar: [references/syntax.md](references/syntax.md). Marker rationale:
[references/closing-markers.md](references/closing-markers.md).

## Workflow

1. Before creating or materially rewriting a project artifact, read the
   absolute `engineering-work.md` path injected by Essential. If unavailable,
   stop artifact writes and report the missing contract. This gate applies to
   `edit` and `author`; read mode remains non-mutating. Run the absolute
   `bin/resolve-engineering-workspace` path declared by that reference with the
   work id before writing. If the resolver path is missing, non-executable, or
   refuses the workspace, stop before mutation and report its reason. Validate
   that an engineering MDC target belongs to the returned default mirror or
   active work spec root. For active work, read `working.md`, then `state.md`,
   then the referenced MDC target.
2. Load mode references before touching content: `read` → syntax; `edit` →
   syntax, closing markers, and
   [references/editing-rules.md](references/editing-rules.md); `author` →
   syntax, closing markers, and [references/examples.md](references/examples.md).
3. Locate non-trivial edits by `ref:`, unique text, or exact line range, then
   read enough surrounding structure to determine parentage and indentation.
4. Apply the smallest coherent operation. Safe edits include annotation scalar
   changes, same-type text replacement, and correctly indented child append.
   Confirm before moving/deleting a subtree, changing inferred type, or
   renaming a referenced `ref:`. Preserve notion-sync frontmatter and path.
5. Re-read every modified region and apply the invariant checklist. Preserve
   existing markers; add the stringifier-default marker to a ref-bearing block
   when it gains children; remove an orphan only when its last child is removed.
6. After all changed MDC files pass review, stamp them together once:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/mdc/scripts/stamp-last-edited.sh" \
     path/to/a.mdc path/to/b.mdc
   ```

Investigate any non-zero exit.
7. Return explicit final paths generated or materially rewritten as
   `generated_files`.

## Verification

- A fresh read passes all syntax, indentation, adjacency, marker, and YAML
  checks for each changed region.
- The stamp touched exactly the changed edit/author files once at the end.
- Path, `ref:`, and unrelated transport metadata remain stable unless the
  request explicitly and safely changed them.

## Completion

Report mode, file paths, refs and operations, marker disposition, invariants,
stamp result, and `generated_files`. Read mode reports an empty manifest. A
refusal names the boundary and the required ref or exact target.
