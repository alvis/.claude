# Handover examples

```bash
/essential:handover
# Indexes every .engineering/works/<work-id>/ stream in the CURRENT source tree,
# refreshes each continuable stream (initialized/active/blocked), lists
# complete/retiring streams as index rows, updates the default source tree's
# global .engineering/overview.md, and emits one bounded Markdown receipt that
# names each stream's work directory. No file is written outside .engineering/.
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

```bash
/essential:takeover <task-or-PR-containing-receipt>
# Resume guided by a receipt. The receipt says which work IDs to expect and which
# revision each assumes; the state itself is read from disk. If a named work
# directory is not present in this tree, takeover reports the exact directory to
# copy rather than reconstructing it from the receipt.
```

```bash
/essential:handover checkout-refunds
# If the selected stream's relevant changes exist only in the working copy, the
# stream is still persisted, indexed, and resumable — copying its work directory
# always carries the state. Only its code portability is deferred, recorded as
# transferable: false with the local-only changes named. Never handover: blocked.
```

A `complete` or `retiring` stream is **not** an error: it appears as a
`## Work index` row and gets no `## Transfer` entry. Invalid work IDs, a missing
Essential contract path, or a contradictory receipt are explicit errors; a
non-portable source anchor is **not** — it marks that stream's code
`transferable: false` while persistence completes. A generic coding stream may
omit a specification. There is no prefix-based or root-file compatibility
fallback.

## Two-stream receipt

A source tree with `web-auth` (`active`, same branch as the current checkout) and
`legacy-import` (`complete`) produces one receipt whose `## Work index` lists
both rows, with a `## Transfer` entry for `web-auth` only. Takeover offers
`web-auth` for selection and excludes `legacy-import` by name. When two
continuable streams sit on **different** source anchors, takeover resumes the
group matching the current checkout and instructs re-running takeover in a
worktree at the other anchor.

## Pause and resume

To pause, `/essential:handover` on the current source tree refreshes its streams'
`state.md` (including the `## Continuation` fields, which name the next owner,
next action, continuation intent, and source anchor) and `state/working.md`, and
upserts that tree's entry in the default tree's `.engineering/overview.md`. That
persistence always completes, so the session can then close. In a new session,
`/essential:takeover` with no argument defaults to the current source tree's own
incomplete streams read straight from on-disk state, and reads `overview.md` to
also offer other source trees' streams — switching the working directory to the
owning tree if one is chosen. The resume neither needs nor consumes a receipt.

Each stream's `Continuation intent` names the capability-level work type — for
example specification-led implementation versus generic coding implementation —
never a fixed skill name; takeover maps it to the relevant implementation skill
and rejects a missing or contradictory intent.

## Moving work to another machine

The work directory is the carrier. Copy
`.engineering/works/web-auth/` to the destination tree's `.engineering/works/`,
bring that checkout to the stream's recorded anchor, and run
`/essential:takeover` there — it finds the stream on disk like any other. The
receipt's job is only to say which directory to copy and which revision to be at;
it never contains the files themselves, so it stays small no matter how large the
stream grows.

When a stream's changes are not reachable from a remote, an approved
`git format-patch` patch or `git bundle` is written to
`.engineering/works/web-auth/artifacts/` so it travels inside the copied
directory. A patch left at `/tmp/auth.patch`, or any receipt written outside
`.engineering/`, is a contract violation — output size is never a reason to
create a file.

For a Notion-backed specification, the receipt records the stable page ref and
captured revision so a resume fetches it fresh, plus the merge base a re-publish
needs. It never records an origin-workspace path such as
`/Users/alice/project/.engineering/` as a *source anchor* — that is a code
anchor, and a local path is not one.
