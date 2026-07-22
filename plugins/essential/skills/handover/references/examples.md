# Handover examples

```bash
/essential:handover
# Indexes every .engineering/works/<work-id>/ stream in the default worktree,
# refreshes and embeds each continuable stream (initialized/active/blocked),
# lists complete/retiring streams as index-only rows, and emits one portable
# Markdown receipt.
```

```bash
/essential:handover auth-refresh
# Optional filter: index all streams but embed only the matching continuable
# stream(s). Refreshes .engineering/works/auth-refresh/state.md and
# state/working.md and reconciles its lazy indexes.
```

```bash
/essential:takeover <task-or-PR-containing-receipt>
# Parses the ## Work index, offers the continuable streams for multi-select
# (excluding complete/retiring), checks out or applies each selected stream's
# source anchor, writes each ### Work state file back to its work-relative path,
# stages any specification, and hands off to the relevant implementation skill.
```

```bash
/essential:handover checkout-refunds
# If the selected stream's relevant changes exist only in the working copy, that
# stream degrades to an index-only row until an approved remote revision or
# externally attached patch/bundle carries them; a single blocked selection
# returns handover: blocked.
```

A `complete` or `retiring` stream is **not** an error: it appears as an
index-only `## Work index` row with `Embedded? no` and is never embedded.
Invalid work IDs, a missing Essential contract path, a non-portable source
anchor on the sole selected stream, or a contradictory receipt are explicit
errors. A generic coding stream may omit a specification. There is no
prefix-based or root-file compatibility fallback.

## Two-stream receipt

A workspace with `web-auth` (`active`, same branch as the current checkout) and
`legacy-import` (`complete`) produces one receipt whose `## Work index` lists
both rows, but only `## Work stream: web-auth` is embedded in full. Takeover
offers `web-auth` for selection, excludes `legacy-import` by name, rehydrates
`web-auth` into the default worktree, and hands off once. When two continuable
streams sit on **different** source anchors, takeover rehydrates the group
sharing the current workspace's anchor and instructs re-running takeover in a
worktree at the other anchor.

Each embedded stream's `Continuation intent` names the capability-level work
type — for example specification-led implementation versus generic coding
implementation — never a fixed skill name; takeover maps it to the relevant
implementation skill and rejects a missing or contradictory intent.

For a response-only handover, each embedded stream's receipt section embeds the
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
