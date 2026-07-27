# Overall review body template

Fill this and submit it as the review `body` in step 9, in the voice from
`tone.md`. Drop any section that would be empty rather than writing "None" under a
heading. Detail lives in the inline comments; this is the map, and it should be
actionable in under a minute.

```markdown
Reviewed `{{head_sha_short}}` — {{files_changed}} files, +{{additions}}/-{{deletions}}, {{zone}} zone.

{{one_paragraph_read}}

### Must change

- **{{file}}:{{line}}** — {{imperative_instruction}}

### Worth considering

- **{{file}}:{{line}}** — {{suggestion}}

### Goal and tests

{{goal_spec_verdict}}

{{test_verdict}}

### Standards

{{standards_verdict}}

### Not anchored to a line

- **{{file}}** — {{finding_that_could_not_anchor}}

### Not reviewed

{{excluded_paths_and_reason}}
```

Notes for the sections where the guidance is not self-evident:

- **Opening paragraph** — lead with the judgement, not a summary of the diff the
  author already knows: "This gets the retry logic right and the shape is good; two
  things need to change before it merges." Name the zone when it is not green, and
  lead with it when it is black.
- **Goal and tests** — state whether the change matches its goal and spec, or say
  *skipped — goal/spec unknown* when neither could be resolved; never grade the diff
  against a goal inferred from the diff. Then answer the test question: would these
  tests fail if the implementation broke? "Coverage is fine" is not a verdict.
- **Not anchored to a line** — findings about deleted files, missing files,
  architecture, or anything GitHub cannot attach to a diff line. Unanchorable is not
  unimportant; never drop these.
- **Not reviewed** — excluded paths and any concern that could not run. The author is
  entitled to know the boundary of what was actually looked at.

Close with the verdict in one sentence, matching the submitted `event`:
`REQUEST_CHANGES` says what has to happen to clear it; `APPROVE` says so plainly and
names anything to watch after merge; `COMMENT` says why the verdict is held — a
concern that did not run, unconvincing tests, red CI, a black-zone diff, or a
self-review GitHub will not let you approve.
