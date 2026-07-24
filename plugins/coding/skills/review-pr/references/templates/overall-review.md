# Overall review body template

Fill this and submit it as the review `body` in step 9. Keep the voice from
`tone.md`. Drop any section that would be empty rather than writing "None" under
a heading — an empty section is filler, and filler is what makes an author stop
reading the summary.

Aim for something the author can act on in under a minute. Detail belongs in the
inline comments; this is the map.

---

## Template

```markdown
Reviewed `{{head_sha_short}}` — {{files_changed}} files, +{{additions}}/-{{deletions}}.

{{one_paragraph_read}}

### Must change

- **{{file}}:{{line}}** — {{imperative_instruction}}
- **{{file}}:{{line}}** — {{imperative_instruction}}

### Worth considering

- **{{file}}:{{line}}** — {{suggestion}}

### Tests

{{test_verdict}}

### Standards

{{standards_verdict}}

### Not anchored to a line

- **{{file}}** — {{finding_that_could_not_anchor}}

### Not reviewed

{{excluded_paths_and_reason}}
```

## Writing each section

**Opening paragraph** — what this PR does and whether it does it, in your own
words. This is where the author learns you actually read it. Lead with the
judgement, not a summary of the diff they already know: "This gets the retry
logic right and the shape is good; two things need to change before it merges."

**Must change** — every P0/P1 finding, one bullet each, imperative, each naming
its file and line so the author can jump to the inline comment. If this section
is empty, drop it; do not write "nothing".

**Worth considering** — P2 findings only. Non-blocking, and say so if it is not
obvious from context. Omit P3 nits entirely here; they live inline.

**Tests** — the `testing` reviewer's verdict in one or two sentences, answering
the question that matters: would these tests fail if the implementation broke?
Name what is untested and why it matters. "Coverage is fine" is not a verdict.

**Standards** — which constitution standards were checked and what the diff does
against them. Name a specific rule when one was violated. If the diff is clean
against them, one sentence saying so is enough.

**Not anchored to a line** — findings about deleted files, missing files,
architecture, or anything else GitHub cannot attach to a diff line. Never drop
these; unanchorable is not the same as unimportant.

**Not reviewed** — binary, generated, vendored, or over-large paths that were
excluded, and any area that could not run. An author is entitled to know the
boundary of what you actually looked at.

## Closing

End with the verdict in a sentence, matching the submitted `event`:

- `REQUEST_CHANGES` — say what has to happen to clear it: "Fix the two items
  above and I'll re-review."
- `APPROVE` — say it plainly and name anything to watch after merge.
- `COMMENT` — say why the verdict is held: an area did not run, tests are
  unconvincing, or this is a self-review that GitHub will not let you approve.
