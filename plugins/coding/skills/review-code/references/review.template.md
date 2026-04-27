<!--
Resolution lifecycle:
  1. Mark fixed: flip checkbox `- [ ]` → `- [x]` AND wrap heading in `~~...~~`. Both signals are required.
  2. Resolve TBD: when a Pending Decision is settled, fill in `**Solution**` on the main issue
     and DELETE the corresponding entry from `## Pending Decisions`.
  3. Verdict line is rewritten on every re-run from the current open-issue counts.
-->
---

area: <SECURITY|QUALITY|TESTING|DOCS|STYLE|CORRECTNESS>
prefix: <SEC|QUAL|TEST|DOCS|STYL|CORR>
reviewed_at: <ISO-8601 timestamp>
files_reviewed_count: <N>
---

# <AREA> Review

**Verdict**: ❌ FAIL — N issues (P0:a, P1:b, P2:c, P3:d)
<!-- For zero open issues use exactly: `**Verdict**: ✅ PASS` on a single line. -->

## General Status

**Files Reviewed**:

- `path/to/file-a.ts`
- `path/to/file-b.ts`
- `path/to/file-c.ts`

<2–4 sentence prose summary of what was reviewed, the dominant patterns observed, and the headline concern. If the verdict is ✅ PASS, replace this section's body (Files Reviewed list and prose) with the single line: `_No issues found._`>

## Issues

### P0 — Blockers

- [ ] ### SEC-P0-1: <one-line summary of the blocker>

  **Source**: `path/to/file.ts:42-58`

  ```ts
  // representative source lines that triggered the finding
  const token = req.headers.authorization;
  db.query(`SELECT * FROM users WHERE token='${token}'`);
  ```

  **Issue**: <what is wrong, which standard / principle is violated, why the current code does not work or is unsafe>

  **Solution**: <directional fix — enough for an agent to act, NOT a full diff>

- [x] ### ~~SEC-P0-2: <fixed issue summary, kept for history>~~

  **Source**: `path/to/file.ts:101-110`

  ```ts
  // original snippet that triggered the finding
  ```

  **Issue**: <original description retained verbatim>

  **Solution**: <direction that was applied>

### P1 — High

- [ ] ### SEC-P1-1: <one-line summary>

  **Source**: `path/to/other.ts:12-20`

  ```ts
  // snippet
  ```

  **Issue**: <description>

  **Solution**: TBD
  <!-- Solution is TBD → this issue MUST also appear in `## Pending Decisions` below. -->

### P2 — Medium

<!-- entries follow the same shape as P0/P1 -->

### P3 — Low

<!-- entries follow the same shape as P0/P1 -->

## Pending Decisions

<!--
  Duplicate every issue whose `**Solution**` is `TBD` here. Once an option is chosen,
  fill in the `**Solution**` on the main issue above and DELETE the entry from this section.
-->

- [ ] ### SEC-P1-1: <same one-line summary as the main issue>

  **Source**: `path/to/other.ts:12-20`

  ```ts
  // snippet
  ```

  **Issue**: <same description as the main issue>

  **Options**:
  1. <approach A> — Pros: <…>. Cons: <…>.
  2. <approach B> — Pros: <…>. Cons: <…>.

  **Recommended**: Option <N> — <one-line reason>

  **Solution**: TBC
