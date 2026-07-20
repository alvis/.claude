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
"$ESSENTIAL_ROOT/bin/resolve-engineering-workspace" --work-id <work-id>
```

Use the reported paths; never infer a default workspace from a branch name,
directory basename, or current working directory.

- `durable_root` is the active workspace root for versioned project documents
  and `.gitignore`; `repo_root` is its compatibility alias.
- `default_workspace` alone owns `.engineering/notion/`.
- `active_workspace` owns its own ignored `.engineering/work/<work-id>/`.
- `work_dir` is the only temporary root for the selected work.
- Each Git worktree or jj workspace has isolated work state. Never copy
  `.engineering/` between them or commit it.

`resolved` with `engineering_ignored: true` is a hard bootstrap gate before
any work artifact or probe is written. On `requires_ignore`, every worker stops
and reports the returned `ignore_file`. The PM alone adds the exact
`.engineering/` rule to the target repository `.gitignore`, includes that
`.gitignore` path in `generated_files`, and reruns the resolver. A sync-only or
ad hoc `git check-ignore` probe does not replace this bootstrap contract. The
resolver validates effective ignore semantics for an active work probe and a
default-workspace Notion probe, so a later negation cannot silently reopen
either write root.

Git's main worktree is its registered default. A jj repository must have a
workspace registered as `default`; if it does not, stop and have the operator
run `jj workspace rename default` in the intended default workspace. The
resolver refuses ambiguous or unregistered layouts instead of guessing.

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
    └── *.md

.engineering/                       # ignored
├── notion/                          # default workspace only
│   └── [notion-sync-owned .mdc paths]
└── work/<work-id>/                  # active workspace only
    ├── working.md
    ├── state.md
    ├── state/*.md
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
    └── evidence/
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
- `docs/specs/<capability>/*.md` is reviewed, versioned engineering
  documentation derived from Notion. It is not managed by notion-sync and does
  not adopt notion-sync filenames. `index.md` is the capability entrypoint.
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
never renamed.

Use the owning product or system capability for
`docs/specs/<capability>/`, not the current task title. Use a zero-padded
monotonic sequence plus a stable slug for ADRs and never renumber merged ADRs.
Ordinary children of work-local `proposals/`, `changes/`, `decisions/`, and
`design/` use an unnumbered semantic `<slug>.md`. Numbered
`<nn>-<topic-slug>.md` children in increments of 10 are reserved for content
created by splitting an oversized file. ADRs alone use four-digit numeric
prefixes. Never use `part-1`, `misc`, or a task title as a child name.

## Work memory

### `working.md`

`working.md` is a temporary, narrow lens on what is being worked on now. The
PM/coordinator is its only writer. It contains a headline current-focus
summary, current handback point, and fast paths to the relevant specification,
source, test, review summary, evidence, and current proposal/change/decision or
design item. It contains no plan, full history, or copied evidence. Aim for
about 4,096 bytes as an editorial mindset; it has no mechanical size gate.

Every subagent reads `working.md`, then the `state.md` overview, then only the
referenced files required by its assignment. A subagent reports paths and
evidence to the PM; it never edits `working.md`.

### `state.md`

`state.md` is the complete resumable work context: goal, full plan, lifecycle
status, acceptance criteria, decisions, dependencies, blockers, review state,
evidence references, repository revision, specification provenance, and sync
state. It links prominently to `working.md` and to the four work overview
files. It references details rather than copying them. If it exceeds the final
size gate, keep `state.md` as the overview and move coherent details to
`state/<nn>-<topic-slug>.md`.

The PM integrates cross-agent state and resolves conflicting reports. Workers
may write only their assigned child artifacts and must return their paths.

## Lazy work overviews

Create `proposals.md`, `changes.md`, `decisions.md`, or `design.md` with the
first child in its corresponding folder. Once created, retain it until work
closes. The PM/coordinator alone reconciles these overviews; subagents may
create or update assigned children and return them in their output manifest.

Each overview contains only:

1. Purpose and one headline summary.
2. Counts by canonical status.
3. A table with `status`, one-line `headline`, and relative child `path`.
4. `last_pm_reconciliation` as an ISO-8601 timestamp.

Do not copy child detail into an overview. `state.md` links to the overview,
not directly to the folder. `working.md` links only to the overview or child
needed for the current focus.

| Overview | Child statuses |
| --- | --- |
| `proposals.md` | `open`, `accepted`, `rejected`, `withdrawn` |
| `changes.md` | `pending`, `applied`, `reverted`, `superseded` |
| `decisions.md` | `proposed`, `accepted`, `rejected`, `superseded` |
| `design.md` | `draft`, `approved`, `implemented`, `promoted`, `superseded` |

Each child starts with structured metadata containing at least its canonical
status, one-line headline, owner, created timestamp, and source/provenance
references. If an overview itself ever requires splitting, reserve
`00-index-<group>.md` names inside its folder for index shards.

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

## Notion and specification lifecycle

`.engineering/notion/` exists only in the default workspace, is ignored, and
contains exact `.mdc` paths owned by notion-sync. Never derive, rename, or
publish assumptions about those filenames. MDC files are exempt from the
Markdown size gate and may be mutated only through the MDC-aware owner.

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

At completion the PM closes review dispositions and identifies approved
specification changes. In the default workspace, the MDC-aware writer applies
them to the mirror. The completion entrypoint delegates outbound push, merge,
and conflict resolution to `sync-notion`, then re-pulls and verifies stable
identity, explicit conflict dispositions, and zero unexpected diff. Regenerate
affected `docs/specs/<capability>/*.md`, record source and derivation hashes,
and run the ordinary Markdown batch gate. A zero exit code without this receipt
is not successful synchronization.

## Evidence, continuity, and retirement

Keep logs, screenshots, captures, binaries, and large raw evidence outside
Markdown. Work artifacts store concise results plus source-bound paths,
revisions, hashes, and dispositions. Discovery and research belong under
`state/` when they are resumable context or `evidence/` when they are source
material. Only durable conclusions are promoted.

Ignored work memory is not a cross-machine transport. A handoff emits a compact
receipt into the owning task, PR, or Notion work item with work ID, repository
revision, authoritative spec identities/revisions, current state, unresolved
items, review summary, and rehydration instructions. A recipient reconstructs
fresh local work state from that receipt and authoritative sources; it does not
copy `.engineering/`.

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
manifests, then runs exactly one pass:

```bash
"$ESSENTIAL_ROOT/bin/check-markdown-size" "${generated_md_files[@]}"
```

The checker invokes one `wc -c "${generated_md_files[@]}"` process for that
pass. It excludes `.mdc` and any file whose basename is `working.md`, ignores
`wc`'s aggregate `total` row, and returns every file greater than 16,384 bytes
together. A file at or below 16,384 bytes remains intact; 12,288 bytes is
authoring guidance only and never forces a split.

On `split_required`, send all oversized files through one complete split round.
Each original path remains a concise overview with purpose, headline summary,
status/owner, contents map, and links to lowercase children. Only after every
split finishes does the coordinator rebuild the complete final manifest and
run one subsequent batch pass. The checker reports only `pass`,
`split_required`, or `invalid`; it never edits or splits files itself.
