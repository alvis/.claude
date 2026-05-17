---
name: mdc
description: Read, edit, and author MDC (Contextual Markdown, @theriety/mdc) files safely with native text tools. Use when asked to "edit this .mdc file", "add a block to <doc>.mdc", "update the annotation for ref <x>", "convert this to MDC", whenever a .mdc file must be read or written, or when mutating any file under .code-spec/.
model: sonnet
context: inherit
allowed-tools: Read, Edit, Write, Grep, Glob, Bash(ls:*), Bash(cat:*)
argument-hint: [<path-to-.mdc>] [--mode=read|edit|author]
---

# MDC

Safely read, edit, and author MDC documents — the @theriety/mdc dialect of Markdown that layers `{{ key: value }}` block annotations, `[text]{{ key: value }}` inline annotations, optional `--{ ref: id }--` closing markers, and YAML front matter on top of CommonMark — by driving Claude's native text tools (Read / Edit / Write / Grep) without invoking the `@theriety/mdc` Node runtime, and codifying the invariants the parser checks so edits round-trip cleanly. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. Because MDC's `ref:`-keyed blocks are the unit of identity the parser preserves, edits must land inside the existing block tree — refining the targeted block in place rather than appending a sibling block that duplicates its concern or trailing a new section beneath the document's final closing marker.

## 1. Purpose & Scope

**What this skill does**:

- **Read** an `.mdc` file and explain its block tree, annotations, and refs.
- **Edit** an existing `.mdc` file — update annotation values, append child blocks, rename refs, replace block content — while preserving every invariant the parser checks.
- **Author** a new `.mdc` file from scratch with correct front matter, indentation, annotations, and (by default) closing markers on ref-bearing blocks that have children.

**What this skill does NOT do**:

- Validate against a JSON schema or domain-specific spec (no `validate()` call).
- Sync the file to Notion (handled by `specification:sync-notion` / `specification:sync-spec`).
- Render to HTML or any visual surface.
- Translate arbitrary plain Markdown into MDC as a first-class workflow.
- Reason about `@theriety/mdc`'s `diff()` ref-identity semantics.

**When to REJECT**:

- File is not `.mdc` (refuse and suggest a plain-Markdown workflow).
- Edit target is ambiguous — user says "update the section about X" but no block carries `ref:` or unique text and the user has not pointed at a line range. Ask for a `ref:` or quote the exact opening line.
- Request requires the `@theriety/mdc` runtime (parser AST, `diff()`, `validate()`, `stringify()`-via-library) — out of scope; suggest the user run the npm package directly.

## 2. Visual Overview

```plaintext
   YOU                              TOOLS / REFERENCES
(Drive the workflow)              (Loaded on demand)
   |                                       |
   v                                       v
[START]
   |
   v
[Step 1: Detect Mode] ───────→ argument-hint --mode OR infer from request
   |
   v
[Step 2: Load References] ───→ references/{syntax,closing-markers,
   |                              editing-rules,examples}.md
   |
   v
[Step 3: Locate Target] ─────→ Grep for `ref:` / opening line
   |                              Read file (or tail) for context
   v
[Step 4: Apply Operation] ───→ Edit / Write
   |       ├─ read   → describe tree + annotations
   |       ├─ edit   → preserve invariants, manage closing markers
   |       └─ author → emit closing markers by default on ref+children
   v
[Step 5: Verify Invariants] ─→ Re-Read modified region
   |                              Check: indent, adjacency, ref match
   v
[END]

Legend
═══════════════════════════════════════════════════════════════════
• Skill is LINEAR: 1 → 2 → 3 → 4 → 5
• References (~750 lines total) load only when their mode is active
• No subagent fan-out — single-agent text edits
═══════════════════════════════════════════════════════════════════
```

## 3. The Three Modes

| Mode       | Trigger                                                      | Primary tools             | Reference loaded                                    |
| ---------- | ------------------------------------------------------------ | ------------------------- | --------------------------------------------------- |
| **read**   | "show me this .mdc", "what does <doc>.mdc say"               | Read, Grep                | `syntax.md`                                         |
| **edit**   | "edit", "update annotation", "add a child block", "rename ref" | Read, Grep, Edit          | `syntax.md` + `closing-markers.md` + `editing-rules.md` |
| **author** | "convert to MDC", "create a new .mdc", "write an MDC for…"   | Write (+ Read for parents) | `syntax.md` + `closing-markers.md` + `examples.md`  |

If the user did not pass `--mode`, infer it: missing file → `author`; file exists and verb is read/show/explain → `read`; everything else on an existing file → `edit`.

## 4. Mandatory Invariants

Every read/edit/author MUST respect these. They are exactly what `@theriety/mdc`'s parser enforces; violating any of them is the most common LLM-produced corruption.

1. **Indentation**: 2 spaces per nesting level, **cumulative** (depth 3 = 6 spaces). **No tabs, ever.**
2. **Annotation adjacency**: A block annotation `{{ … }}` must sit on the line **immediately before** its target block — **no blank line between them**. A blank line *detaches* the annotation and silently breaks the binding. This is the single most common LLM-edit failure.
3. **Front matter**: If present, it is the very first content; opening and closing `---` are alone on their lines; the body parses as standard YAML.
4. **Annotation body syntax**: Content inside `{{ … }}` is **YAML object syntax** (`key: value, key2: [a, b]`, quoted strings allowed, end-of-line `#` comments allowed inside the outer braces).
5. **Inline annotations**: `[content]{{ … }}` or `[text](url){{ … }}` or `[]{{ type: x }}` for empty-content type markers — annotation immediately follows the closing `]` or `)`, no whitespace between.
6. **Closing markers (when present)**: syntax is exactly `--{ ref: <name> }--`; the `ref` must match the opening block's `ref`; the marker's indent must equal the opening block's indent. See `references/closing-markers.md`.
7. **Escapes**: `\{\{`, `\}\}`, `\[`, `\]`, `\\` to render those characters literally. Inside fenced code blocks, no escaping is required (code fences are parser-opaque).

A quick checklist to run mentally after every edit:

- [ ] Indent is multiple of 2 spaces, matches surrounding depth.
- [ ] No blank line between an annotation and its block.
- [ ] All opened `{{` are closed by `}}` on the same line.
- [ ] Every `--{ ref: X }--` matches an opening `{{ … ref: X … }}` at the same indent.
- [ ] YAML inside `{{ }}` and inside front matter parses (commas between keys, quotes balanced).

For full grammar, see `references/syntax.md`.

## 5. Closing-Marker Policy

The closing-marker rules are subtle and central to safe editing; the summary here is authoritative for the skill, with full rationale in `references/closing-markers.md`.

- **Reading**: closing markers are **optional**. **Never** flag a missing marker as a defect or error.
- **Editing**: **preserve** every closing marker that is already present. **Add** a closing marker for any block that has (or after the edit will have) both a `ref:` annotation and at least one child block — this matches the `@theriety/mdc` stringifier default and protects the block against indentation drift.
- **Authoring**: emit closing markers by default on every block that has a `ref:` and at least one child. (Mirrors `stringify({ omitClosingMarkers: false })`, which is the default.)
- **Resilience semantics**: a closing marker extends the parent block's hierarchical scope **beyond what indentation alone implies** — under-indented children inside the marker boundary are still treated as descendants of that parent. This is why adding markers makes LLM edits robust: even if a later edit drops an indent level, the parse still recovers.

## 6. Workflow

ultrathink: walk every read/edit/author through these steps in order.

### Step 1: Detect Mode and Load References

1. Parse `--mode` from arguments. If absent, infer per §3.
2. Read the relevant reference file(s) for the mode (see the table in §3) before touching the document.
3. Confirm the target path ends in `.mdc`. If not, REJECT per §1.

### Step 2: Locate the Target

For edit-mode operations on a non-trivial file, never edit blind. Use Grep first:

```bash
# find a block by its ref
grep -n "ref:\s*${REF_ID}" path/to/doc.mdc

# enumerate all block annotations at top level
grep -nE "^\{\{\s*ref:" path/to/doc.mdc

# find existing closing markers (to know what to preserve)
grep -nE "^\s*--\{\s*ref:" path/to/doc.mdc
```

Then `Read` the file (or a focused range) so the surrounding indent and adjacent blocks are in context.

### Step 3: Apply the Operation

Choose the smallest safe operation. The catalogue lives in `references/editing-rules.md`; the short list:

- **Safe**: update an annotation key/value, append a child block at the correct indent, replace a block's text content (same type), add a `ref:` to a previously unref'd block.
- **Risky** (require an explicit confirmation back to the user before applying): move a block under a new parent, delete a block that has children, change a block's inferred type (e.g., turn a paragraph into a heading), rename a `ref:` that is referenced elsewhere.

When the edit causes a `ref:`-bearing block to gain its first child, add a matching `--{ ref: <id> }--` closing marker at the parent's indent on the line after the last child. When it removes the last child of such a block, also remove the now-orphaned closing marker.

### Step 4: Verify Invariants

After every `Edit` or `Write`, **re-`Read` the modified region** (a window of ~5 lines before and ~10 lines after the edit is usually enough; for whole-file authoring read the head and tail). Run the checklist from §4 against what you see. If anything fails, fix it before yielding.

### Step 5: Report

State, in this order: file path, mode, what changed (with refs), and which invariants you re-verified. If you added or removed closing markers, say so explicitly — the user will want to know.

## 7. Worked Examples (Three Idioms)

See `references/examples.md` for the long versions and four more domain idioms (Notion sync, spreadsheet expressions, medical provenance, intelligence classification). Three quick patterns:

### 7.1 Update an annotation on an existing ref

Goal: change `confidence: low` to `confidence: high` on block `ref: claim-7`.

```bash
grep -n "ref:\s*claim-7" report.mdc
# → 142:{{ source: HUMINT, confidence: low, ref: claim-7 }}
```

Edit line 142 only, swapping the value. Do **not** touch surrounding indent. Re-Read lines 140–146. Verify: annotation still immediately precedes its block (no blank line introduced), YAML still parses.

### 7.2 Append a child block (and add a closing marker)

Starting state — parent has a `ref:` but no children, so no closing marker yet:

```markdown
{{ ref: parent-block }}
- Parent item
```

After appending a child:

```markdown
{{ ref: parent-block }}
- Parent item
  {{ ref: child-block }}
  - Child item
--{ ref: parent-block }--
```

Note: child is indented 2 spaces; child annotation is at the **same** indent as the child block (2 spaces), with no blank line between them; the closing marker is at the **parent's** indent (0 spaces) and its `ref` matches the parent.

### 7.3 Author a new MDC document from scratch

```markdown
---
title: Quarterly Review
ref: review-2026-q1
status: draft
---

{{ ref: intro }}
# Introduction

{{ ref: highlights }}
## Highlights

  {{ ref: highlight-1 }}
  - Revenue up [+18%]{{ trend: positive, delta: 0.18 }} vs Q4.
  {{ ref: highlight-2 }}
  - Churn down to [2.1%]{{ metric: churn_rate }}.
--{ ref: highlights }--
```

Closing marker on `highlights` because it has a `ref:` and children. `intro` has a `ref:` but no children — no marker needed. Each child annotation sits immediately above its `- ` item with no blank line. Inline annotations attach directly to the closing `]`.

## 8. Skill Completion

Report in this shape:

```yaml
skill: mdc
mode: read|edit|author
file: <absolute path to .mdc>
changes:
  - block_ref: <ref or "(unref'd)">
    operation: update-annotation|append-child|replace-content|rename-ref|add|delete|author
    closing_marker: added|removed|preserved|n/a
invariants_verified:
  indentation: pass
  annotation_adjacency: pass
  closing_marker_match: pass|n/a
  yaml_parses: pass
notes: |
  <anything the user should know — e.g. "added closing marker on parent because
  it gained its first child", or "refused: target ref ambiguous">
```
