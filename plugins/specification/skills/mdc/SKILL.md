---
name: mdc
description: Read, edit, and author MDC (Contextual Markdown, @theriety/mdc) files safely with native text tools. Use when asked to "edit this .mdc file", "add a block to <doc>.mdc", "update the annotation for ref <x>", "convert this to MDC", whenever a .mdc file must be read or written, or when mutating any file under .code-spec/.
model: sonnet
allowed-tools: Read, Edit, Write, Grep, Glob, Bash(ls:*), Bash(cat:*), Bash(bash ${CLAUDE_PLUGIN_ROOT}/skills/mdc/scripts/*)
argument-hint: "[<path-to-.mdc>] [--mode=read|edit|author]"
---

# MDC

Safely read, edit, and author MDC documents — the @theriety/mdc dialect of
Markdown that layers `{{ key: value }}` block annotations,
`[text]{{ key: value }}` inline annotations, optional `--{ ref: id }--`
closing markers, and YAML front matter on top of CommonMark — by driving
native text tools (Read/Edit/Write/Grep) without the `@theriety/mdc` Node
runtime, while honoring every invariant the parser checks so edits round-trip
cleanly. Notion transport belongs to `specification:sync-notion` and
`specification:sync-spec`.

## Boundaries

- Use for: reading an `.mdc` file and explaining its block tree, annotations,
  and refs; editing an existing `.mdc` (update annotation values, append
  child blocks, rename refs, replace block content); authoring a new `.mdc`
  with correct front matter, indentation, annotations, and closing markers.
  This skill is the only writer for `.code-spec/*.md`.
- Do not use for: JSON-schema or domain validation (no `validate()`), syncing
  to Notion (`specification:sync-notion` / `specification:sync-spec`),
  rendering to HTML, translating arbitrary plain Markdown into MDC as a
  first-class workflow, or reasoning about `diff()` ref-identity semantics.
- Refuse when: the file is not `.mdc` (suggest a plain-Markdown workflow);
  the edit target is ambiguous — no `ref:`, no unique text, no line range —
  in which case ask for a `ref:` or the exact opening line; or the request
  needs the `@theriety/mdc` runtime (parser AST, `diff()`, `validate()`,
  library `stringify()`) — suggest running the npm package directly.

## Inputs

- **Required**: the target `.mdc` path, or for authoring, the destination
  path plus the content to express.
- **Optional**: `--mode=read|edit|author`. When absent, infer: missing file →
  `author`; existing file with a read/show/explain verb → `read`; anything
  else on an existing file → `edit`.

## Mandatory invariants

<IMPORTANT>
Every read, edit, and author operation must respect these — they are exactly
what the `@theriety/mdc` parser enforces, and violating them is the most
common LLM-produced corruption:

1. **Indentation**: 2 spaces per nesting level, cumulative (depth 3 =
   6 spaces). No tabs, ever.
2. **Annotation adjacency**: a block annotation `{{ … }}` sits on the line
   immediately before its target block — no blank line between them. A blank
   line detaches the annotation and silently breaks the binding; this is the
   single most common edit failure.
3. **Front matter**: when present, it is the very first content; opening and
   closing `---` alone on their lines; the body parses as standard YAML.
4. **Annotation body syntax**: content inside `{{ … }}` is YAML object
   syntax (`key: value, key2: [a, b]`, quoted strings allowed, end-of-line
   `#` comments allowed inside the outer braces).
5. **Inline annotations**: `[content]{{ … }}`, `[text](url){{ … }}`, or
   `[]{{ type: x }}` for empty-content type markers — the annotation
   immediately follows the closing `]` or `)`, no whitespace between.
6. **Closing markers (when present)**: syntax is exactly
   `--{ ref: <name> }--`; the `ref` must match the opening block's `ref`;
   the marker's indent must equal the opening block's indent.
7. **Escapes**: `\{\{`, `\}\}`, `\[`, `\]`, `\\` render those characters
   literally. Inside fenced code blocks no escaping is required — fences are
   parser-opaque.
</IMPORTANT>

Post-edit checklist: indent is a multiple of 2 spaces matching surrounding
depth; no blank line between an annotation and its block; every opened `{{`
closes with `}}` on the same line; every `--{ ref: X }--` matches an opening
`{{ … ref: X … }}` at the same indent; YAML inside `{{ }}` and front matter
parses. Full grammar: [references/syntax.md](references/syntax.md).

## Closing-marker policy

Full rationale in
[references/closing-markers.md](references/closing-markers.md); the summary
here is authoritative for the skill:

- **Reading**: markers are optional — never flag a missing marker as a
  defect.
- **Editing**: preserve every existing marker; add one for any block that has
  (or after the edit will have) both a `ref:` and at least one child — this
  matches the stringifier default and protects against indentation drift.
- **Authoring**: emit markers by default on every block with a `ref:` and at
  least one child.
- **Resilience semantics**: a marker extends the parent's scope beyond what
  indentation implies — under-indented children inside the marker boundary
  still parse as descendants, so markers make later edits recoverable.

## Workflow

1. Detect the mode (argument or inference above) and confirm the target path
   ends in `.mdc`; otherwise refuse per Boundaries. Load the mode's
   references before touching the document: `read` →
   [references/syntax.md](references/syntax.md); `edit` → syntax plus
   [references/closing-markers.md](references/closing-markers.md) and
   [references/editing-rules.md](references/editing-rules.md); `author` →
   syntax plus closing-markers and
   [references/examples.md](references/examples.md).
2. Locate the target — for edit mode on a non-trivial file, never edit
   blind:

   ```bash
   grep -n "ref:\s*${REF_ID}" path/to/doc.mdc     # block by ref
   grep -nE "^\{\{\s*ref:" path/to/doc.mdc         # top-level annotations
   grep -nE "^\s*--\{\s*ref:" path/to/doc.mdc      # existing closing markers
   ```

   Then Read the file or a focused range so surrounding indent and adjacent
   blocks are in context.
3. Apply the smallest safe operation; the full catalogue lives in
   [references/editing-rules.md](references/editing-rules.md). Safe (apply
   directly): update an annotation key/value, append a child block at the
   correct indent, replace a block's text content (same type), add a `ref:`
   to an unref'd block. Risky (confirm with the user first): move a block
   under a new parent, delete a block with children, change a block's
   inferred type, rename a `ref:` referenced elsewhere. Edits must land
   inside the existing block tree — refine the targeted block in place
   rather than appending a duplicate sibling or trailing a new section after
   the document's final closing marker. When a `ref:`-bearing block gains
   its first child, add its closing marker at the parent's indent after the
   last child; when it loses its last child, remove the orphaned marker.
   When authoring a `.code-spec`/Notion-bound document, emit `title`,
   `last_edited_time`, and `ref` in the front matter in that order — a
   placeholder `last_edited_time` is fine, step 5 refreshes it.
4. Verify invariants: after every Edit or Write, re-Read the modified region
   (about 5 lines before and 10 after; for whole-file authoring, the head
   and tail) and run the post-edit checklist. Fix any failure before
   yielding.
5. Stamp `last_edited_time` — edit/author modes only; read mode never writes
   and never stamps. Run once, as the final action, after every changed file
   is verified — never mid-batch, or a later edit leaves an earlier file
   stamped with a stale time. Pass exactly the files whose content changed:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/mdc/scripts/stamp-last-edited.sh" \
     path/to/a.mdc path/to/b.mdc
   ```

   The script writes the current UTC time (`YYYY-MM-DDTHH:MM:SS.000Z`) into
   each file's front-matter `last_edited_time`, replacing or inserting the
   key; all files in one invocation share one timestamp. A non-zero exit
   means a file was skipped (not `.mdc`, missing, or no front matter) —
   investigate before reporting done.
6. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker
   remains, then report the blocker instead of looping.

## Verification

- The post-edit checklist passes on a fresh Read of every modified region.
- Every closing marker matches its opening `ref:` at the opening block's
  indent, and no `ref:`-bearing parent with children lacks one after an
  edit.
- The stamp script exited zero and touched exactly the changed files
  (edit/author modes).

## Completion

Report the file path, mode, and each change with its block ref and operation;
say explicitly whether closing markers were added, removed, or preserved;
name the invariants re-verified; and give the stamped timestamp and file list
(or note read mode). A refusal states which boundary rule applied and what
the user should supply — typically a `ref:` or the exact opening line.
