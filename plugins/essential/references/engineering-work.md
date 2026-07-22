# Engineering work lifecycle

Read this contract before creating or materially rewriting project engineering
artifacts. It defines their paths, ownership, promotion, and final size check.
Domain skills own artifact content; Essential owns this cross-plugin lifecycle.

## Resolve the workspace first

The injected instruction gives the absolute path to this file. Derive the
Essential plugin root from that path, then run the resolver from inside the
target repository:

```bash
ENGINEERING_WORK_REFERENCE='<absolute engineering-work.md path injected by Essential>'
ESSENTIAL_ROOT="$(cd "$(dirname "$ENGINEERING_WORK_REFERENCE")/.." && pwd)"
"$ESSENTIAL_ROOT/bin/resolve-engineering-workspace"
```

The resolver accepts both `--work-id <id>` and `--work-id=<id>`, and both
`--path <path>` and `--path=<path>`. A normal invocation is read-only;
`--bootstrap` is the explicit PM-only creation mode described below.

The resolver chooses in this order: explicit `--work-id`,
`ENGINEERING_WORK_ID`, a work directory matching the Git branch/jj workspace
label (including a namespaced Git branch's final component), then a sole
existing workspace-local work directory only when the workspace label is
generic or unavailable. A meaningful workspace-derived identity that differs
from the sole existing directory is ambiguous and returns `work_id_required`.
Branch and
workspace names may identify existing work but never create a new identity.
Explicit IDs are for user-confirmed disambiguation, newly derived or minted
work, and portable takeover—not a required argument on every skill.
`work_id_source` records the choice.

On `work_id_required`, no work path is selected. The result includes
`candidate_work_ids`, `workspace_label`, and any `suggested_work_id`; the PM asks
the user, while a worker reports the ambiguity to the PM. Never guess through
multiple candidates, a detached checkout, or a generic `main`, `master`,
`trunk`, or `default` workspace. Use the reported paths once resolved.

- `durable_root` is the active workspace root for versioned project documents
  and `.gitignore`; `repo_root` is its compatibility alias.
- `default_workspace` is nullable discovery metadata for consumers that need a
  registered default; generic work does not require one.
- `active_workspace` owns its own ignored `.engineering/works/<work-id>/`.
- `work_dir` is the only temporary root for the selected work.
- Each Git worktree or jj workspace has isolated work state. Never copy
  `.engineering/` between them or commit it.

`resolved` with `engineering_ignored: true` is a hard bootstrap gate before
any work artifact or probe is written. On `requires_ignore`, every worker stops
and reports the returned `ignore_file`. The PM alone adds the exact
`.engineering/` rule to the active workspace `.gitignore`, includes that
`.gitignore` path in `generated_files`, and reruns the resolver. A sync-only or
ad hoc `git check-ignore` probe does not replace this bootstrap contract. The
resolver validates effective ignore semantics for an active work probe, so a
later negation cannot silently reopen that write root.

### First-use work-memory bootstrap

After the user has confirmed any new work identity and the resolver returns
`resolved` with `engineering_ignored: true`, the PM invokes the resolver once
more with that confirmed ID and `--bootstrap`, before delegating or creating
any other work artifact:

```bash
"$ESSENTIAL_ROOT/bin/resolve-engineering-workspace" \
  --work-id=<confirmed-work-id> --bootstrap
```

Identity selection remains separate and interactive: `--bootstrap` never
derives or mints an ID, and it cannot bypass `work_id_required` or
`requires_ignore`. The resolver owns the mechanical bootstrap; the PM alone
may request it while holding the coordinator lease. It creates the work
directory, its `state/` subdirectory, and whichever of `state/working.md` and
`state.md` is missing. Each file is
created with no-clobber semantics; an existing regular file is reported and
preserved byte-for-byte. The resolver refuses symlinked/non-directory work-root
components and symlinked/non-regular entrypoints on every invocation, not only
during bootstrap, so later writers cannot escape the target workspace. This
also makes the command safe to rerun when an interrupted first use created only
one entrypoint.

The initial `state/working.md` contains the work ID, creation timestamp,
`initialized` status, a confirmation-focused current action and handback
point, and a relative link to `../state.md`. The initial `state.md` contains the
same identity/status/navigation plus explicit placeholders for goal and
success criteria, lifecycle plan, revision, specification provenance, sync,
review, decisions, dependencies/blockers/risks, and evidence/validation.
Downstream owners replace those placeholders with observed truth; they do not
create competing bootstrap shapes. The resolver returns the exact paths in
`bootstrap_created` and preserved paths in `bootstrap_existing`; the PM adds
created paths to the combined `generated_files` manifest.

Git's main worktree is reported as its default when available. A jj workspace
registered as `default` is reported when available. A Notion operation that
needs a default workspace resolves and validates that requirement itself;
ordinary work remains valid without it.

## Canonical topology

```text
docs/
├── index.md
├── architecture/
│   ├── overview.md
│   ├── <architecture-slug>.md
│   ├── <architecture-slug>/*.md
│   └── decisions/<nnnn>-<decision-slug>.md
├── design/
│   ├── system.md
│   ├── system/*.md
│   ├── <design-slug>.md
│   └── <design-slug>/*.md
└── specs/<capability>/
    ├── index.md
    ├── provenance.json
    └── *.md

.engineering/                       # ignored, isolated per source tree
├── overview.md                      # default source tree only: global cross-tree status index
├── notion/                          # conventional default-workspace mirror
│   └── [notion-sync-owned .mdc paths]
└── works/<work-id>/                 # in the source tree that owns the stream; not repeated in the default tree
    ├── state.md
    ├── state/
    │   ├── working.md
    │   ├── unresolved.md
    │   ├── plan.md
    │   ├── discovery.md
    │   └── *.md
    ├── spec/
    ├── proposals.md
    ├── proposals/*.md
    ├── changes.md
    ├── changes/*.md
    ├── decisions.md
    ├── decisions/*.md
    ├── design.md
    ├── design/*.md
    ├── review.md
    ├── reviews/*.md
    └── artifacts/
```

All generated project Markdown filenames are lowercase. Plugin control files
whose runtime names are fixed, including `SKILL.md`, `CLAUDE.md`,
`MAINAGENT.md`, and `SUBAGENT.md`, retain those names.

### Durable documentation

- `docs/index.md` is the small entrypoint to architecture, design, and
  capability specifications.
- `docs/architecture/overview.md` indexes durable architecture documents and
  ADRs. `docs/architecture/<slug>.md` owns structural rules, boundaries,
  topology, protocols, and flows. A choice with alternatives and consequences
  is an ADR under `decisions/`, not a second architecture truth.
- `docs/design/system.md` owns system-wide tokens, components, states, motion,
  and accessibility. `docs/design/<slug>.md` owns durable feature,
  interaction, information, or experience design that is not system-wide.
- `docs/specs/<capability>/` is reviewed, versioned engineering specification
  content. For an inline source, `index.md` is the durable authoritative
  carrier; for an explicit local source it is a content-equivalent durable
  carrier; for Notion it is a verified derivation. `provenance.json` records
  source kind, source and approval hashes, template identity, and output
  hashes. The tree is not managed by notion-sync and does not adopt
  notion-sync filenames.
- Task implementation state does not become durable merely because a skill
  wrote it. Promote only stable knowledge, with provenance and supersession
  links, during completion.

## Deterministic names

Use Essential's executable as the only path-name derivation implementation:

```bash
"$ESSENTIAL_ROOT/bin/derive-engineering-name" slug '<source text>'
"$ESSENTIAL_ROOT/bin/derive-engineering-name" slug '<source text>' \
  --collision-with '<existing-slug>' --stable-id '<stable source identity>'
"$ESSENTIAL_ROOT/bin/derive-engineering-name" tracker-work-id '<tracker key>'
"$ESSENTIAL_ROOT/bin/derive-engineering-name" minted-work-id \
  --date '<yyyymmdd>' --kind '<kind>' --scope '<scope>' --ulid '<new ULID>'
```

The helper applies Unicode NFKD normalization, ASCII transliteration,
lowercasing, non-alphanumeric tokenization, and a 48-byte ASCII bound without
retaining a partial trailing token. An empty transliteration becomes `item`.
If the complete first token alone exceeds the bound, the helper retains its
first 48 ASCII bytes because no earlier token boundary exists. On a reported
collision it reserves ten bytes inside the same 48-byte bound and appends
`--<stable-id8>`, where `stable-id8` is the first eight lowercase hexadecimal
characters of the stable source identity's SHA-256 digest. The shortened base
still ends at a whole-token boundary unless its first token alone exceeds the
available bound. Callers must pass every occupied sibling slug through
`--collision-with`; never reimplement the rule or add a random suffix.

Use `tracker-work-id` to normalize an existing tracker key, such as
`eng-421-checkout-refunds`. Otherwise generate one ULID and call
`minted-work-id`; its result is
`<yyyymmdd>-<kind>-<scope-slug>-<ulid6>`. A minted work ID is an identity and is
never renamed. Derive or mint only when the resolver cannot select safely and
the PM has resolved the ambiguity; do not require callers to repeat a resolved
work ID.

Use the owning product or system capability for
`docs/specs/<capability>/`, not the current task title. Use a zero-padded
monotonic sequence plus a stable slug for ADRs and never renumber merged ADRs.
Ordinary children of work-local `state/`, `proposals/`, `changes/`,
`decisions/`, and `design/` use an unnumbered semantic `<slug>.md`. Within
`.engineering/`, numbered `<nn>-<topic-slug>.md` children in increments of 10
are reserved for content created by mechanically splitting an oversized file. Durable `docs/`
children use lowercase semantic names and are split only when that improves
ownership or navigation. ADRs alone use four-digit numeric prefixes. Never use
`part-1`, `misc`, or a task title as a child name.

## Work memory

### Cross-tree overview (`.engineering/overview.md`)

The default source tree — Git's main worktree or the jj workspace registered as
`default` — carries a single `.engineering/overview.md`: the only global,
cross-tree status index. Secondary source trees do not carry it. Because
`.engineering/` is never shared or copied between trees, each source tree's own
`.engineering/works/<work-id>/` state folders live only in that tree; they are
never repeated in the default tree. The default tree holds `works/<work-id>/`
only when it hosts its own work streams.

`overview.md` is a single table of every work stream across all source trees:
work ID, lifecycle status, one-line headline, next action, `Location` (the source
tree that holds the stream — its path, kind, and revision — or `-` when that tree
has been removed and the stream is orphaned), and `Documentations` (links to any
related `docs/` material, or `-`). It is an index, not a substitute for each
stream's `state.md`; the authoritative resumable context for a stream stays in
that stream's own source tree. The PM/coordinator
updates the default tree's `overview.md` whenever a stream's status changes — in
particular at handover — so a new session can survey every tree from one place
and resume the right stream in the right source tree. A stream is worked in
exactly one source tree at a time; only an explicit merge of source trees moves a
stream between them.

### `state/working.md`

`state/working.md` is a temporary, narrow lens on what is being worked on now. The
PM/coordinator is its only writer. It contains a headline current-focus
summary, current handback point, and fast paths to the relevant specification,
source, test, review summary, evidence, and current proposal/change/decision or
design item. It contains no plan, full history, or copied evidence. Aim for
about 4,096 bytes as an editorial mindset; it has no mechanical size gate.

The assignment capsule and its exact references are a subagent's starting
context. A subagent reads `state/working.md` only when it needs current-work
navigation. It reads `state.md` for resume, planning, alignment, cross-slice
dependencies, or when explicitly assigned; unrelated and self-contained work
reads neither. A subagent reports paths, evidence, and state deltas to the PM;
it never edits PM-owned work memory.

### `state.md`

`state.md` is the complete resumable work context: goal, full plan, lifecycle
status, acceptance criteria, decisions, dependencies, blockers, open questions,
review state, evidence references, repository revision, specification
provenance, and sync state. It links prominently to `state/working.md` and each
lazy work overview that currently exists. It references details rather than
copying them. Semantic children such as `state/plan.md` or `state/discovery.md`
hold resumable detail. Record open questions in detail in `state/unresolved.md`,
each with an owner and a disposition (resolved, deferred, or blocking);
`state.md` only briefly notes that unresolved questions exist and links to that
child. When none remain, delete `state/unresolved.md` and remove the mention
from `state.md`. If `state.md` exceeds the final size gate, keep it as the
overview and move coherent split detail to `state/<nn>-<topic-slug>.md`.

Every new or explicitly rewritten state file follows
[the engineering work-state contract](engineering-work-state.md). Root
`state.md` carries the complete parent/subtask registry and the canonical
plan-source pointer. Resumable children carry marked task subsets without
becoming a second plan authority. State is free-form, LLM-readable Markdown and
is not machine-validated: before a task dispatch, review, portable handover,
completion, or retirement, read `state.md` and its `state/` children directly to
judge runnable tasks, current owner, and next action. Preserve any existing
state file byte-for-byte until an explicit rewrite; never rewrite it by guess.

Persist state immediately, never lazily. The moment a task or subtask changes
status (started, blocked, done, failed, cancelled) or a decision is made, the
lease holder writes that change into `.engineering/` state before moving on to
the next action — not batched, and not deferred to handover or session end. State
in `.engineering/` is the durable memory of record; handover only publishes and
transports what is already written. This continuous-persistence discipline
bounds the loss to a single in-flight step if the coding agent crashes mid-task
or a session ends without an explicit handover, so a later resume reads an
accurate registry rather than reconstructing lost progress. A worker without the
lease returns its status change and evidence in its output manifest immediately;
the lease holder reconciles it into `state.md` at once rather than accumulating
deltas.

One actor holds the work item's coordinator lease and is the sole writer of
`state/working.md`, `state.md`, the four lazy overview files, and `review.md`. The PM
holds it by default and may explicitly grant it to one orchestration skill,
naming the files covered. The PM does not write those files until that skill
returns. Every other subagent is a worker: it writes only assigned children and
returns paths plus reconciliation deltas.

## Lazy work overviews

Create `proposals.md`, `changes.md`, `decisions.md`, or `design.md` with the
first child in its corresponding folder. Once created, retain it until work
closes. The PM/coordinator alone reconciles these overviews; subagents may
create or update assigned children and return them in their output manifest.

`proposals/` and `changes/` both record deviations from the canonical Notion
specification; they differ only by implementation state. A `proposals/` child is
a deviation proposed against the canonical Notion spec that is **not yet
implemented** — the intent to differ, captured before the code reflects it. A
`changes/` child is a deviation from the canonical Notion spec that **is
implemented** — the divergence now realized in the source tree. As work
progresses a deviation shifts from `proposals/` to `changes/`: when the proposed
deviation lands in the implementation, the coordinator retires the `proposals/`
child (`accepted`) and records the implemented deviation as a `changes/` child,
whose provenance links back to the originating proposal. A deviation that is
never implemented ends in `proposals/` (`rejected` or `withdrawn`) and never
reaches `changes/`; only an implemented deviation is saved under `changes/`.

Each overview contains only:

1. Purpose and one headline summary.
2. Counts by canonical status.
3. A table with `status`, one-line `headline`, and relative child `path`.
4. `last_pm_reconciliation` as an ISO-8601 timestamp.

Do not copy child detail into an overview. `state.md` links to the overview,
not directly to the folder. `state/working.md` links only to the overview or child
needed for the current focus.

| Overview | Child statuses |
| --- | --- |
| `proposals.md` | `open`, `accepted`, `rejected`, `withdrawn` |
| `changes.md` | `pending`, `applied`, `reverted`, `superseded` |
| `decisions.md` | `proposed`, `accepted`, `rejected`, `superseded` |
| `design.md` | `draft`, `approved`, `implemented`, `promoted`, `superseded` |

Each child starts with structured metadata containing at least its canonical
status, one-line headline, owner, created timestamp, and source/provenance
references. When a `proposals/` or `changes/` child records a deviation from a
Notion-backed specification, its provenance MUST link to the related
`.engineering/notion/` mirror file (the exact `.mdc` path in the registered
default workspace); a spec deviation recorded without that link is incomplete.
If an overview itself ever requires splitting, reserve `00-index-<group>.md`
names inside its folder for index shards.

## Reviews

`review.md` is the current roll-up. Details live in exactly seven canonical
areas under `reviews/`:

| File | Question |
| --- | --- |
| `alignment.md` | Does the implementation match the approved contract and scope? |
| `correctness.md` | Is behavior semantically correct, including unspecified cases? |
| `security.md` | Are trust boundaries, data, permissions, and abuse cases safe? |
| `quality.md` | Is it maintainable, reliable, and appropriately structured? |
| `testing.md` | Is intended behavior verified sufficiently and reliably? |
| `docs.md` | Are engineer and user explanations accurate and sufficient? |
| `style.md` | Does the change follow mechanical and idiomatic conventions? |

A finding is `open`, `fixed`, `acknowledged`, `deferred`, or `skipped`. `fixed`
is closed only by verified evidence. `acknowledged` and `skipped` are closed
non-fixed risk dispositions only with non-placeholder rationale, an accountable
owner, and an explicit recheck condition; P0/P1 additionally require explicit
risk-acceptance authority and durable acceptance evidence. `open` and
`deferred` are outstanding and block review closure. A malformed
`acknowledged` or `skipped` entry remains outstanding.
`review.md` records both the five disposition counts and derived `closed` and
`outstanding` counts using exactly this mapping.
Contract/completeness audit findings belong to `alignment.md`; semantic bugs
belong to `correctness.md`. Plan deviations belong in `state.md` and also in
`alignment.md` only when they cause contract drift. Do not create `audit.md` or
`deviations.md`. Work closes only when `review.md` agrees with every detail.
Reviewers own only assigned `reviews/*.md` details and return roll-up deltas;
the coordinator-lease holder alone reconciles `review.md` after all review
writers finish. A nested review workflow without that lease returns a summary
delta instead of touching the roll-up.

## Specification and Notion lifecycle

An explicit local path, approved inline candidate, or selected Notion identity
may supply a specification. Inline prompt text is evidence only: before
planning or implementation it becomes a complete approved candidate and a
content-equivalent durable `docs/specs/<capability>/index.md` carrier. A local
source retains its exact path and gains the same durable carrier/provenance.
Neither path claims a Notion round trip.

`.engineering/notion/` is the conventional ignored mirror in a registered
default workspace, not a path fixed by the generic resolver. The Notion owner
may receive another explicit output root and must resolve the required default
workspace, validate the actual root's ignore state, and report that root's
remediation path. A mirror contains exact `.mdc` paths owned by notion-sync.
Never derive, rename, or publish assumptions about those filenames. They may be
mutated only through the MDC-aware owner.

`sync-spec` materializes only the required temporary working specification
under the active work's `spec/`. Record stable Notion page/block IDs, exact
returned paths, source revision/hash, and dependent-work revalidation state in
`state.md`. A changed source revision marks dependent work
`needs_revalidation` before implementation continues.

Revalidation is guaranteed only for locally discoverable, registered
workspaces. Enumerate each local Git worktree from `git worktree list
--porcelain`. For jj, enumerate names with `jj workspace list` and resolve every
registered name with `jj workspace root --name <name>`. Mark affected work
found under those explicit roots. Never claim that every remote or copied work
directory was updated. The completion receipt lists affected external task,
PR, and Notion anchors plus every known or unknown remote dependent that still
needs revalidation.

For a Notion-backed specification, completion closes review dispositions and
identifies approved changes against an exact source hash. The MDC-aware writer
applies them to the selected transport path. The completion entrypoint
delegates outbound push, merge, and conflict resolution to `sync-notion`, then
re-pulls and verifies stable identity, explicit conflict dispositions, and
zero unexpected diff. Regenerate affected
`docs/specs/<capability>/` content and record source and derivation hashes. A
zero exit code without this receipt is not successful synchronization. Local
and inline sources instead re-verify their carrier and provenance hashes and
never invoke Notion transport merely to complete.

## Evidence, continuity, and retirement

Keep logs, screenshots, captures, binaries, and large raw evidence outside
Markdown. Work artifacts store concise results plus source-bound paths,
revisions, hashes, and dispositions. Discovery and research belong under
`state/` when they are resumable context or `artifacts/` when they are source
material. Findings surfaced during implementation — gotchas, constraints,
and learned facts about the codebase — are recorded in
`state/discovery.md`, an ordinary resumable `state/` child governed by the same
ownership and size rules as its siblings. Only durable conclusions are promoted
to `docs/`; a resumable finding stays in `state/discovery.md` until it becomes
stable knowledge worth promoting.

Continuity has two paths. On the **same machine**, pausing and resuming works
from the on-disk state files: a handover completes the current source tree's work
stream state and updates the default tree's `overview.md`, so a new session reads
`overview.md`, chooses a source tree and stream, and resumes from that tree's own
`state.md`/`state/` files — no receipt required. Ignored work memory is not a
**cross-machine** transport: for that, a handover additionally emits a
plain-Markdown portable receipt into the owning task, PR, or Notion work item or,
when necessary, embeds every payload in the response. The receipt carries a
destination-reachable source anchor, the raw contents of the current tree's work
stream state files, authoritative specification carriers, and fixed
non-executable application semantics. A recipient reads those carriers in an
isolated post-anchor tree before reconstructing fresh local work state; it never
copies `.engineering/` or trusts a local-only path. Handover scopes to the
current source tree only; it never indexes or rewrites another tree's work
streams, and `overview.md` is the sole cross-tree surface.

Retire completed local work only after acceptance, review closure, durable
promotion, Notion push and verification pull, and final receipts are recorded.
The default retention is 30 days unless repository compliance policy requires
longer. Existing ambiguous artifacts are reported and preserved, never deleted
or migrated by guesswork.

## Output manifest and final size loop

Every artifact-writing skill returns explicit final paths it generated or
materially rewrote:

<report>

```yaml
generated_files:
  - /absolute/path/to/file.md
```

</report>

Writers finish all files and links before returning the manifest. They do not
measure or split independently. The coordinator combines and deduplicates the
manifests, selects only absolute `.md` paths inside the resolved target
workspace's `.engineering/`, excludes every file whose basename is
`working.md`, and then runs exactly one pass when eligible paths remain:

```bash
"$ESSENTIAL_ROOT/bin/check-markdown-size" \
  --engineering-root "$active_workspace/.engineering" \
  "${generated_md_files[@]}"
```

The checker canonicalizes the declared root and every path, excludes traversal,
symlink, and other-workspace escapes, invokes one
`wc -c "${eligible_generated_md_files[@]}"` process for that pass, ignores
`wc`'s aggregate `total` row, and returns every eligible file greater than
16,384 bytes together. An eligible file at or below 16,384 bytes remains
intact; 12,288 bytes is authoring guidance only and never forces a split.

The gate does not apply outside `.engineering/`. In particular, versioned
`docs/**`, project READMEs, source or reference Markdown, and plugin control
files have no mechanical document-size limit. The only separate limit in this
plugin is the 2,000-byte injection limit for Essential's `CLAUDE.md`,
`MAINAGENT.md`, and `SUBAGENT.md`.

On `split_required`, send all oversized files through one complete split round.
Each original path remains a concise overview with purpose, headline summary,
status/owner, contents map, and links to lowercase children. Only after every
split finishes does the coordinator rebuild the complete final manifest and
run one subsequent batch pass. The checker reports only `pass`,
`split_required`, or `invalid`; it never edits or splits files itself.
