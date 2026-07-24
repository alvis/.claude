---
name: doctor
description: Check the integrity of the engineering work memory with the structural doctor, diagnose folder-structure and format drift against the current contracts, and offer user-approved migration to the latest structure. Use for health checks of .engineering/, before resuming old work, after suspected corruption or drift, or when a stream predates the current state format; this skill repairs and migrates work memory, never the work itself.
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
argument-hint: "[work-id] [--strict]"
---

# Doctor

Diagnose the current source tree's `.engineering/` work memory and, with
approval, bring it to the latest structure. Diagnosis is mechanical
(`engineering-doctor`); judgement is not: what "latest" means is whatever the
current Essential contracts say, so migration is decided by reading them —
never by a version token, and never by guessing from memory.

## Boundaries

- Use for integrity checks, drift diagnosis, and contract-format migration of
  work memory. Do not implement, review, or resume the work itself
  (`essential:takeover` owns resumption) and do not touch another source
  tree's `works/`.
- Diagnosis never mutates anything. Repairs and migrations happen only after
  explicit user approval, per stream, under that stream's coordinator lease.
- Never rewrite a state file merely because the convention moved on — older
  formats are valid history and migrate lazily. Migration here is an explicit
  user-approved coordinator rewrite, the one sanctioned exception.
- Never falsify history: journal lines, tombstones, completed marks, and
  superseded decisions are preserved; migration reshapes structure, not
  truth. Unrecognized files are reported and preserved, never deleted,
  renamed, or reinterpreted by guesswork.

## Engineering-work gate

Before creating or materially rewriting a project artifact, read the absolute
`engineering-work.md` path injected by Essential; if unavailable, stop
artifact writes and report the missing contract. Read its work-state contract
sibling and `truth.md` as well — together they define the current canonical
topology and file shapes that "latest" means. Run the resolver read-only to
locate the active workspace and `.engineering/`; on `requires_ignore` or
`work_id_required`, report per the contract rather than proceeding.

## Workflow

1. **Scope.** With `[work-id]`, check that one stream
   (`--work-dir <work_dir>`); otherwise check everything
   (`--engineering-root <active_workspace>/.engineering`, covering every
   stream plus `overview.md`). A missing `.engineering/` is a clean report,
   not an error.
2. **Run the doctor.** Invoke
   `"$ESSENTIAL_ROOT/bin/engineering-doctor" --json` with the scope from
   step 1, passing `--strict` through when given. Collect the findings; the
   doctor is read-only and its silence about prose is not an endorsement.
3. **Inspect structure the doctor cannot judge.** Compare each stream's
   on-disk layout with the canonical topology and file shapes in the current
   contracts: files that predate the present format (for example a stream
   without a charter, journal, or revision counters), children in
   unexpected places, oversized files never split, orphaned overview rows,
   or a layout that matches an older convention. Classify every observation:
   - **defect** — broken structure the doctor flagged (dangling
     dependencies, contradictory statuses, lease conflicts, broken links);
   - **format drift** — valid but older shapes that would migrate at the
     next explicit rewrite;
   - **informational** — unrecognized-but-harmless files, or free-form
     sections the doctor could not parse.
4. **Propose, per stream.** Present findings grouped by stream with a
   concrete repair/migration plan derived from the current contracts: what
   would change, what is preserved byte-for-byte, and what stays untouched.
   Ask the user with `AskUserQuestion` which streams to repair or migrate;
   informational items need no action and defects in prose meaning are
   surfaced as questions, not silently "fixed".
5. **Repair under the lease.** For each approved stream: check
   `lease.json` via `engineering-lease` — a live foreign lease stops that
   stream with a report; an expired lease is claimed with the explicit
   `takeover` verb and journaled. Then apply the approved plan as ordinary
   coordinator rewrites: journal the migration first, preserve all history
   (append, restructure, and relink — never rewrite recorded events), and
   follow the contract's write protocol. Release the lease when done.
6. **Confirm.** Re-run the doctor over the repaired scope and require the
   approved findings to be gone; anything remaining is reported with a
   reason. Return every created or materially rewritten path in
   `generated_files`.

## Verification

- Diagnosis ran read-only; nothing changed before user approval.
- Every applied repair traces to an approved finding; unrecognized files
  were preserved and reported.
- No journal line, tombstone, completed mark, or superseded decision was
  removed or reworded; migrations were journaled under the stream's lease.
- The post-repair doctor run confirms the approved findings are resolved.

## Completion

Report the scope, finding counts by classification and severity, per-stream
approval decisions, repairs applied with their journal entries, findings
deliberately left (with reasons), the post-repair doctor result, and
`generated_files`.
