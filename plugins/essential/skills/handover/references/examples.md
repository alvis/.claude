# Handover examples

```bash
/essential:handover
# Indexes every .engineering/works/<work-id>/ stream in the CURRENT source tree,
# refreshes and carries in full each continuable stream (initialized/active/blocked),
# lists complete/retiring streams as index-only rows, updates the default source
# tree's global .engineering/overview.md, and emits one portable Markdown receipt.
```

```bash
/essential:handover auth-refresh
# Optional filter: index all streams but carry in full only the matching
# continuable stream(s). Refreshes .engineering/works/auth-refresh/state.md and
# state/working.md and reconciles its lazy indexes.
```

```bash
/essential:takeover
# No argument: same-machine resume. Defaults to the CURRENT source tree's own
# incomplete work streams read from on-disk state files, and also reads the
# default tree's .engineering/overview.md to offer other source trees' streams.
# Picking a stream in another tree switches the working directory to that tree
# first. One source tree at a time; no receipt, no anchor application.
```

```bash
/essential:takeover <task-or-PR-containing-receipt>
# Cross-machine resume. Parses the ## Work index, offers the continuable streams
# for multi-select (excluding complete/retiring), checks out or applies each
# selected stream's source anchor, writes each ### Work state file back to its
# work-relative path, stages any specification, and hands off to the relevant
# implementation skill.
```

```bash
/essential:handover checkout-refunds
# If the selected stream's relevant changes exist only in the working copy, that
# stream degrades to an index-only row until an approved remote revision or
# externally attached patch/bundle carries them. Persistence and the overview
# upsert still complete, so the pause succeeds and the stream resumes locally;
# only its cross-machine section is deferred — never handover: blocked.
```

A `complete` or `retiring` stream is **not** an error: it appears as an
index-only `## Work index` row and is never carried in full. Invalid work IDs, a
missing Essential contract path, or a contradictory receipt are explicit errors;
a non-portable source anchor is **not** — it degrades that stream to an
index-only row while persistence still completes. A generic coding stream may
omit a specification. There is no prefix-based or root-file compatibility
fallback.

## Two-stream receipt

A source tree with `web-auth` (`active`, same branch as the current checkout) and
`legacy-import` (`complete`) produces one receipt whose `## Work index` lists
both rows, but only `## Work stream: web-auth` is carried in full. Takeover
offers `web-auth` for selection, excludes `legacy-import` by name, rehydrates
`web-auth` into the resolved workspace, and hands off once. When two continuable
streams sit on **different** source anchors, takeover rehydrates the group
sharing the current workspace's anchor and instructs re-running takeover in a
worktree at the other anchor.

## Same-machine pause and resume

To pause, `/essential:handover` on the current source tree refreshes its streams'
`state.md` (including the `## Continuation` fields) and `state/working.md` and
upserts that tree's entry in the default tree's `.engineering/overview.md`. That
persistence always completes, so the session can then close. In a new session,
`/essential:takeover` with no argument defaults to the current source tree's own
incomplete streams read straight from on-disk state, and reads `overview.md` to
also offer other source trees' streams — switching the working directory to the
owning tree if one is chosen. The local
resume neither needs nor consumes a receipt; handover may still emit a portable
receipt best-effort, but it is required only for moving work to a different
machine or checkout, and a stream whose changes are still local simply becomes an
index-only row without blocking the pause.

Each carried stream's `Continuation intent` names the capability-level work
type — for example specification-led implementation versus generic coding
implementation — never a fixed skill name; takeover maps it to the relevant
implementation skill and rejects a missing or contradictory intent.

For a response-only handover, each carried stream's receipt section carries the
raw contents of every `### Work state` file, the complete patch when that is the
source anchor, and any inline specification. A `git bundle` is never inlined:
it is an external attachment referenced by locator. For an externally published
handover, a stream's source anchor and specifications may instead be a
repository-relative path or a stable attachment locator. A path such as
`.engineering/works/web-auth/state.md` or `/tmp/auth.patch` is never a portable
source anchor on its own.

For a Notion-backed specification, the receipt records the stable page ref and
captured revision so takeover fetches it fresh during rehydration. It never
records an origin-workspace path such as `/Users/alice/project/.engineering/`.
