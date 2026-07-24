# Handover examples

```bash
/essential:handover
# Indexes every .engineering/works/<work-id>/ stream in the CURRENT source tree,
# refreshes each continuable stream (initialized/active/blocked), leaves
# complete/retiring streams as index rows, and updates the default source tree's
# global .engineering/overview.md. No file is written outside .engineering/.
```

```bash
/essential:handover auth-refresh
# Optional filter: index all streams but refresh only the matching continuable
# stream(s). Refreshes .engineering/works/auth-refresh/state.md and
# state/working.md and reconciles its lazy indexes.
```

```bash
/essential:takeover
# Resume. Defaults to the CURRENT source tree's own incomplete work streams read
# from on-disk state files, and also reads the default tree's
# .engineering/overview.md to offer other source trees' streams. Picking a stream
# in another tree switches the working directory to that tree first. One source
# tree at a time.
```

A `complete` or `retiring` stream is **not** an error: it stays an index row and
gets no refresh. Invalid work IDs and a missing Essential contract path are
explicit errors. A generic coding stream may omit a specification. There is no
prefix-based or root-file compatibility fallback.

## Two streams in one tree

A source tree with `web-auth` (`active`) and `legacy-import` (`complete`) gets
one `overview.md` row each; only `web-auth` has its `state.md` and
`state/working.md` rewritten. A later takeover offers `web-auth` for selection
and excludes `legacy-import` by name. When two continuable streams sit on
**different** source anchors, takeover resumes the group matching the current
checkout and instructs re-running takeover in a worktree at the other anchor.

## Pause and resume

To pause, `/essential:handover` on the current source tree refreshes its streams'
`state.md` (including the `## Continuation` fields, which name the next owner,
next action, continuation intent, and source anchor) and `state/working.md`, and
upserts that tree's entry in the default tree's `.engineering/overview.md`. That
persistence always completes, so the session can then close. In a new session,
`/essential:takeover` with no argument defaults to the current source tree's own
incomplete streams read straight from on-disk state, and reads `overview.md` to
also offer other source trees' streams — switching the working directory to the
owning tree if one is chosen.

Each stream's `Continuation intent` names the capability-level work type — for
example specification-led implementation versus generic coding implementation —
never a fixed skill name; takeover maps it to the relevant implementation skill
and rejects a missing or contradictory intent.

## Specifications and local-only changes

A stream whose relevant repository changes exist only in the working copy is
still persisted and still resumable — the pause records exactly what is
uncommitted, and never returns `handover: blocked`.

For a Notion-backed specification, `state.md` records the stable page ref and
captured revision so a resume fetches it fresh, plus the merge base a re-publish
needs. If the live specification source is unreachable at handover time, mark
the provenance stale and note it.
