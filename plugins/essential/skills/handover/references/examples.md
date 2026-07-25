# Handover examples

```bash
/essential:handover
# Indexes every state_root/.state/works/<work-id>/ stream — the default
# source tree's, whichever checkout you run from — refreshes each continuable
# stream (initialized/active/blocked), leaves reviewing/completed/retiring
# streams as index rows, and updates the global .state/overview.md beside
# them. No file is written outside .state/.
```

```bash
/essential:handover auth-refresh
# Optional filter: index all streams but refresh only the matching continuable
# stream(s). Refreshes .state/works/auth-refresh/state.md and
# state/working.md and reconciles its lazy indexes.
```

```bash
/essential:takeover
# Resume. Offers every incomplete stream in the centralized works/, read from
# on-disk state files, and reads overview.md for each stream's Location. Picking
# a stream worked in another checkout switches the working directory there
# first. It settles reviewing streams — merged PR means completed — before
# offering the next task. One stream at a time.
```

A `reviewing`, `completed`, or `retiring` stream is **not** an error: it stays
an index row and gets no refresh. Invalid work IDs and a missing Essential contract path are
explicit errors. A generic coding stream may omit a specification. There is no
prefix-based or root-file compatibility fallback.

## Two streams

`web-auth` (`active`) and `legacy-import` (`completed`) get one `overview.md`
row each; only `web-auth` has its `state.md` and `state/working.md` rewritten. A
later takeover offers `web-auth` for selection and excludes `legacy-import` by
name. When two continuable streams sit on **different** source anchors, takeover
resumes the one matching the current checkout and switches the working directory
for the other — the state is shared, so only the checkout changes.

## Pause and resume

To pause, `/essential:handover` refreshes each stream's `state.md` (including
the `## Continuation` fields, which name the next owner, next action,
continuation intent, and source anchor) and `state/working.md`, and upserts its
row in the global `.state/overview.md`. That persistence always completes,
so the session can then close. In a new session, `/essential:takeover` with no
argument offers every incomplete stream read straight from on-disk state, and
reads `overview.md` for each one's `Location` — switching the working directory
to that checkout if the chosen stream is worked elsewhere.

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
