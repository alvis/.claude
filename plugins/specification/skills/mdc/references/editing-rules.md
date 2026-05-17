# Editing Rules

Catalogue of safe vs risky operations on MDC files, with the invariant checklist the skill applies after every edit. Loaded by the skill in `edit` mode.

---

## 1. Operation Catalogue

### Safe Operations (apply directly)

| Operation                       | What it changes                                       | Notes                                                                                          |
| ------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Update an annotation value      | one key in `{{ … }}`                                  | leave key order and other keys untouched                                                       |
| Add a key to an annotation      | append `, key: value` before the closing `}}`         | check it still parses as YAML                                                                  |
| Remove a key from an annotation | drop the key and its leading/trailing comma           | mind comma cleanup — no `, ,` or trailing `,`                                                 |
| Replace block textual content   | the content line(s) of one block, same type           | keep indent identical; preserve annotation adjacency                                            |
| Append a child block            | insert child after parent's last existing child       | child indent = parent indent + 2 spaces; add a closing marker if parent gains its first child  |
| Add a `ref:` to a block         | inject `{{ ref: <id> }}` above an unannotated block   | no blank line between the new annotation and the block                                         |
| Add an inline annotation        | wrap a span as `[span]{{ … }}`                        | no whitespace between `]` and `{{`                                                              |
| Update front-matter scalar      | one key in the YAML head                              | preserves indentation of nested YAML mappings                                                   |

### Risky Operations (CONFIRM with user before applying)

| Operation                            | Why risky                                                                                  |
| ------------------------------------ | ------------------------------------------------------------------------------------------ |
| Move a block under a new parent      | every descendant must be re-indented; any closing markers in the subtree must follow.      |
| Delete a block that has children     | losing descendants is rarely intended; confirm scope.                                      |
| Change a block's inferred type       | e.g. `- item` → `## heading` reshapes the AST; consequences for siblings may surprise.     |
| Rename a `ref:` that appears elsewhere | refs are the addressing primitive — cross-references and diff identity rely on them.     |
| Bulk re-indent                       | easy to break adjacency or split children from parents.                                    |
| Convert plain Markdown → MDC         | out of scope for v1; reject and direct user to author from spec.                           |

For each risky op, present a one-line plan back to the user and wait for confirmation before issuing the `Edit`.

---

## 2. Invariant Checklist (run after EVERY edit)

The skill MUST `Read` the modified region after editing and check each item. Failure on any item → fix before yielding.

1. **Indent multiple of 2 spaces** on every modified line; no tabs introduced.
2. **Annotation adjacency**: every `{{ … }}` block annotation is followed on the next line by its target block. No blank line between them.
3. **YAML inside `{{ … }}` parses**: commas separate keys, quotes balanced, no stray `:` or unmatched brackets.
4. **YAML in front matter parses** (if touched).
5. **Inline annotation adjacency**: every `]` or `)` that should carry a `{{ … }}` has the `{{` immediately after, no whitespace.
6. **Closing marker integrity** (see `closing-markers.md`):
   - every existing marker preserved unless its block lost its last child;
   - every newly ref'd-with-children block has a matching marker added;
   - every marker's `ref` matches its opening block's `ref`;
   - every marker's indent matches its opening block's indent.
7. **Escapes intact**: any `\{\{`, `\}\}`, `\[`, `\]`, `\\` outside fenced code blocks is still escaped.
8. **No accidental fence change**: a triple-backtick line you didn't intend to touch is still a triple-backtick line.

---

## 3. Recovery Moves

When a verification check fails, prefer minimal repair over rewrite.

| Symptom                                           | Recovery                                                                                          |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Blank line introduced between annotation and block | Remove the blank line (single-line delete).                                                       |
| Annotation YAML now invalid (stray comma, etc.)  | Re-issue the `Edit` with the corrected `{{ … }}` only; do not touch surrounding lines.            |
| Marker `ref` no longer matches opening            | Update the marker (not the opening); the opening's `ref` is the source of truth.                  |
| Marker indent off                                 | Re-indent the marker line to match the opening's indent (`Edit` with leading whitespace fix).     |
| Child indent off after move                       | Re-indent the moved subtree; markers in the subtree must shift by the same amount.                |
| Inline annotation drifted from its `]`           | Close the gap: `] {{ ` → `]{{ `.                                                                  |
| Front-matter YAML invalid                         | Restore the prior front matter from the pre-edit Read; reapply the intended scalar change.        |

If a single repair fails twice, **stop and report** rather than escalating edits — the file may be in a state that needs a human or the `@theriety/mdc` runtime to diagnose.

---

## 4. Procedural Pattern for a Generic Edit

```
1. Detect mode (edit) and load syntax.md + closing-markers.md + this file.
2. Grep -n for `ref:\s*<TARGET>` or for the opening line of the block.
3. Read the file around the match (≥5 lines before, ≥10 after).
4. Plan the smallest Edit: which old_string, which new_string.
   - If risky per §1, surface the plan to the user first.
5. Issue the Edit.
6. Re-Read the modified region.
7. Run the §2 checklist.
8. If anything fails, apply a single recovery move from §3 and re-verify (max 2 attempts).
9. Report (mode, file, refs touched, marker changes, invariants verified).
```

---

## 5. Working in `.code-spec/`

Files under `.code-spec/` are fair game for editing — they are local materialisations of Notion specs. The skill should **not** refuse edits there. Sync back to Notion is a separate skill (`specification:sync-notion`); leave that to the user or the sibling skill.

Two things to be especially careful about in `.code-spec/`:

- The root spec file (whose 32-hex suffix matches its top-level page) MUST remain non-empty. If your edit is structural enough to risk an empty file, do it as a series of small additions and removals, not a single full replacement.
- Front-matter `ref:` is the page's Notion ID. Never edit it unless explicitly told to.
