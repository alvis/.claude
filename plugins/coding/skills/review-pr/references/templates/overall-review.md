# Overall review body template

Fill this and submit it as the review `body`, in the voice from
`tone.md`. Drop any section that would be empty rather than writing "None" under a
heading. Detail lives in the inline comments; this is the map, and it should be
actionable in under a minute.

```markdown
Reviewed `{{head_sha_short}}` — {{files_changed}} files, +{{additions}}/-{{deletions}}, {{zone}} zone.

{{one_paragraph_read}}

### Must change

> [!CAUTION]
> {{what_blocks_merge}}

- {{marker}} **{{file}}:{{line}}** — {{imperative_instruction}}

### Worth considering

> [!TIP]
> {{highest_value_optional_improvement}}

- {{marker}} **{{file}}:{{line}}** — {{suggestion}}

### Goal and tests

{{goal_spec_verdict}}

{{test_verdict}}

### Standards

{{standards_verdict}}

### Not anchored to a line

> [!IMPORTANT]
> {{why_these_could_not_anchor}}

- {{marker}} **{{file}}** — {{finding_that_could_not_anchor}}

### Not reviewed

> [!IMPORTANT]
> {{excluded_paths_and_reason}}

### Verdict

> [!{{verdict_alert}}]
> {{verdict_sentence}}
```

Notes for the sections where the guidance is not self-evident:

- **Opening paragraph** — lead with the judgement, not a summary of the diff the
  author already knows: "This gets the retry logic right and the shape is good; two
  things need to change before it merges." Name the zone when it is not green, and
  lead with it when it is black.
- **Markers** — every bullet opens with the same marker its inline comment carries,
  per `tone.md`: a P0–P4 badge when the finding claims a consequence, a tag when it
  demands a process step, an emoji when it demands nothing. The body and the inline
  comment must not disagree about a finding's level.
- **Alerts** — at most one per section, and only where it changes what the author
  does next; `tone.md` owns which alert means what. `> [!CAUTION]` opens *Must
  change* under a substantive `REQUEST_CHANGES` — a self-review downgrade does not
  clear it, because the blockers are still there. `> [!TIP]` opens *Worth
  considering* only under a substantive `APPROVE`, and carries the single
  highest-value optional improvement. An alert whose section is dropped is dropped
  with it.
- **Goal and tests** — state whether the change matches its goal and spec, or say
  *skipped — goal/spec unknown* when neither could be resolved; never grade the diff
  against a goal inferred from the diff. Then answer the test question: would these
  tests fail if the implementation broke? "Coverage is fine" is not a verdict.
- **Relocations** — a change that belongs elsewhere goes in whichever section its
  priority earns, with the destination path in the bullet: "Move the null guard into
  `src/orders/order.service.ts:88` — every other caller needs it too." When the right
  home is a lower PR in the stack, say that instead and name `coding:commit
  --reorder`.
- **Not anchored to a line** — findings about deleted files, missing files,
  architecture, or anything GitHub cannot attach to a diff line. Unanchorable is not
  unimportant; never drop these.
- **Not reviewed** — excluded paths and any concern that could not run. The author is
  entitled to know the boundary of what was actually looked at.

*Verdict* is the one section that is never dropped, and it carries its own heading so
the closing alert is never read as part of the exclusion list above it. Close it with
the verdict in one sentence. `{{verdict_alert}}` is not a free choice: resolve it from
the submitted `event` and the reason the verdict was held, so a review that cannot be
trusted never closes as if it needed no action.

Resolve it from the **substantive verdict** — step 1 of the `event` derivation in
`SKILL.md` — and never from the submitted `event`. The two diverge whenever a cap or a
self-review downgrade rewrote the event, and keying the alert to the submitted value is
exactly what would let a blocked PR close as though it needed no action. First matching
row wins:

| Substantive verdict, and what happened to it | `{{verdict_alert}}` |
|---|---|
| `REQUEST_CHANGES`, whatever the submitted `event` ended up being | `CAUTION` — the blockers already stand under *Must change*, so close by naming what clears them rather than repeating them; where the event was downgraded, say that GitHub weakened the event and not the finding |
| Capped at `COMMENT` because the review is incomplete or untrustworthy | `WARNING` — name which part could not be trusted |
| `APPROVE`, whether submitted as-is or downgraded on your own PR | `NOTE` — say so plainly and name anything to watch after merge |
