# Work-memory templates

Use the Essential engineering-work contract as authoritative. These shapes add
handover-specific content; all timestamps are one real UTC ISO-8601 value.

## `state.md`

```markdown
# <Work headline>

- Schema: `engineering-work-state/v1`
- Work ID: `<work-id>`
- Lifecycle status: `<initialized|active|blocked|complete|retiring>`
- Plan source: `state.md`
- Plan digest: `<64-lowercase-hex>`
- Hash kind: `engineering-plan-definition-digest-v1`
- Updated: `<timestamp>`
- Current focus: [working.md](working.md)
- External anchor: `<task|issue|PR|Notion URL>`

## Status

<Current lifecycle/task roll-up, owner, and exact next action.>

## Tasks

| ID | Mark | Status | Task | Depends on | Required | Acceptance | Owner | Evidence / next action |
|---|---|---|---|---|---|---|---|---|
| `LFE` | `⧗` | `working` | `<summary> [targets: none]` | `-` | `yes` | `<criterion>` | `<owner>` | `<evidence or action>` |
| `LFE01` | `✓` | `done` | `<summary> [targets: src/example.ts]` | `-` | `yes` | `<criterion>` | `<owner>` | `<evidence>` |

## Goal and success criteria
## Plan graph
## Current state and file status
## Approved decisions and accepted assumptions
## Dependencies, blockers, risks, and pivot signals
## Reviews and dispositions
## Evidence and validation
## Durable promotion
## Specification sync and revalidation
## Continuation
```

The root table contains the complete registry: every three-letter parent and
every `AAA01`-style child exactly once. A resumable `state/*.md` child may mirror
only its parent's existing subset and cannot introduce an ID. Store full IDs in
`Depends on`; parent edges target parents and child edges target siblings.
Every Task cell is exactly `<summary> [targets: <comma-separated paths>|none]`.
Marks and status words use `- planned`, `⧗ working`, `✓ done`, `X failed`,
`! blocked`, or `⊘ cancelled`. Graph notation and diagrams are derived display,
not authority.

File substates: completed; `need-draft`; `need-completion`; `need-fixing`;
`need-testing`; `need-linting`; `need-refactoring`; blocked. Record path,
substate, remaining action, evidence, and blocker. Use semantic `state/*.md`
children for genuinely resumable execution detail. Numeric split children are
reserved for a shared file that exceeded its size limit.

## `working.md`

```markdown
# Current focus

- Updated: `<timestamp>`
- Status: `<one sentence>`
- Working now: `<one narrow outcome>`
- Handback point: `<exact next action or blocker>`

## Fast paths
- State: [state.md](state.md)
- Spec: [<relative path>](<relative path>)
- Source/test: [<relative path>](<relative path>)
- Active decision/design/review/evidence: [<relative path>](<relative path>)
```

Aim at approximately 4,096 bytes by editing, not a gate. Never include the full
plan, history, completed inventory, copied spec, or review findings.

## Lazy work overviews

`proposals.md`, `changes.md`, `decisions.md`, and `design.md` are created with
their first child and then retained until work closes. Each contains purpose,
one headline, canonical status counts, last PM reconciliation timestamp, and a
table of child headline/status/relative path. Never copy child detail.

## Portable receipt

```yaml
schema: engineering-work-handover/v3
repository: <stable repository identity>
revision: <commit/change id>
branch_or_bookmark: <name or none>
source_anchor:
  type: <remote_revision|patch|bundle>
  format: <git-commit|git-patch|git-bundle>
  encoding: <git-object|utf-8|base64|binary>
  content: <complete inline bytes or null>
  locator: <retrievable remote ref/attachment URL or null>
  checksum:
    algorithm: <git-object-id|sha256>
    value: <verified digest>
  application:
    mode: <checkout_revision|apply_patch|fetch_bundle_ref>
    base_revision: <exact base revision or none>
    result_revision: <exact revision or none>
    result_tree: <expected Git tree id>
    bundle_ref: <exact ref for a bundle or none>
state_snapshot:
  format: engineering-work-state+json/v1
  encoding: <utf-8|base64>
  content: <complete inline payload or null>
  locator: <retrievable attachment URL or null>
  checksum:
    algorithm: sha256
    value: <verified digest of decoded payload bytes>
  application:
    mode: reconstruct_work_memory
    destination_root: .engineering/work/<work-id>/
    render: [state.md]
work_id: <id>
external_anchor: <URL or response_only>
workflow_owner: <specification:implement-code|coding:write-code>
goal: <one sentence>
status: <active|blocked>
current_task_id: <full executable task ID or none>
plan_source: state.md
plan_digest: <64-lowercase-hex>
plan_hash_kind: engineering-plan-definition-digest-v1
next_owner: <exact continuation owner>
next_action: <one sentence>
spec_sources:
  - kind: <local|inline|notion>
    format: <mdc|markdown|notion-page-tree>
    encoding: <utf-8|base64|notion-api>
    content: <complete inline specification or null>
    locator: <repository-relative path, retrievable attachment, or stable Notion ref>
    checksum:
      algorithm: <sha256|none>
      value: <verified decoded-byte digest or none for a remote Notion carrier>
    hash_model: specification-dual-hash-v1
    hashes:
      transport_manifest_hash: sha256:<64-lowercase-hex>
      contract_digest: sha256:<64-lowercase-hex>
    application:
      mode: <read_from_anchored_tree|materialize_inline|fetch_notion>
      destination: <path-contained repository/work-root relative path>
      notion_transport:
        logical_profile: <destination-resolvable profile name or none>
        stable_ref: <canonical Notion page/database ref or none>
        captured_revision: <remote revision or none>
        suggested_root: <contained repository-relative path or none>
        reconciliation:
          status: <exact sync-owner operational status>
          classification: <initial|unchanged|metadata_only|local_only|remote_only|structural_change|converged|concurrent|baseline_required|materialization_conflict>
          next_action: <exact sync-owner next action>
          portable_state:
            required: <true|false>
            format: <specification-blr-transfer+json/v1|none>
            encoding: <base64|utf-8|none>
            content: <complete canonical B/L package bytes or null>
            locator: <retrievable attachment URL or null>
            checksum:
              algorithm: <sha256|none>
              value: <sha256:<64-lowercase-hex>|none>
            application: <validate_and_restore_base_and_local_in_isolation|none>
            base:
              transport_manifest_hash: <sha256:... or none>
              contract_digest: <sha256:... or none>
            local:
              transport_manifest_hash: <sha256:... or none>
              contract_digest: <sha256:... or none>
durable_refs: [<versioned docs paths>]
work_artifacts:
  - role: <implementation_detail|goal_acceptance|decision|review|validation|sync|file_status|other>
    path: <contained work-relative render path>
    format: <markdown|json|text>
    encoding: <utf-8|base64>
    content: <complete inline bytes or null>
    locator: <retrievable attachment URL or null>
    checksum:
      algorithm: sha256
      value: <verified decoded-byte digest>
pending_decisions: [<id and owner/deadline>]
validation: [<command and result summary>]
spec_sync:
  status: <exact sync-owner operational status or not_applicable>
  classification: <exact sync-owner relationship or not_applicable>
  next_action: <exact sync-owner next action or none>
recheck_triggers: [<trigger>]
```

Exactly one of `content` or `locator` is non-null for every present byte carrier;
an explicitly non-required `portable_state` has both null. A
response-only receipt uses `content` for the state snapshot, every required
work artifact, every patch or bundle, every inline specification, and every
required Notion B/L transfer; it
cannot point at a response-local or ignored filesystem path. External locators
must be stable and retrievable by the recipient. Checksums cover the exact
decoded bytes, not a pretty-printed or reconstructed variant.

Every specification source records
`hash_model: specification-dual-hash-v1` and keeps
`transport_manifest_hash` paired with `contract_digest`. The former is exact
carrier/identity/revision integrity evidence; the latter is the approved
semantic contract. Neither may be replaced by a generic `hash`,
`captured_hash`, or `revision_or_hash` field. These values do not replace the
independent checksum of an encoded portable payload.

The `state_snapshot` payload is the exact canonical JSON emitted by Essential's
`validate-engineering-state pack --state <state.md>` operation. Validate it
only with `validate-snapshot`; do not maintain a second schema parser. It
contains the complete parent/subtask task definitions and graph, plan identity,
task statuses/owners/evidence, and exact continuation owner/action. It does not
contain the full goal or acceptance narrative, decisions, reviews,
sync/revalidation, validation narrative, or file-status narrative.

The v3 receipt's typed fields and `work_artifacts` carry that broader context.
Each ignored/local-only linked artifact needed for continuity is a complete
checksum-bound inline carrier or retrievable attachment; versioned narrative
may instead use a contained `durable_refs` path in the verified source anchor.
An `implementation_detail` carrier exists only when linked from root state and
is procedure keyed by existing IDs; it cannot duplicate/override IDs, edges,
requiredness, targets, or acceptance mappings.
Omitted task fields, contradictory task statuses, or dangling task-evidence
references make the snapshot invalid. Missing narrative carriers make the v3
receipt non-rehydratable, not a reason to extend or reinterpret the snapshot.
Its `application` is data,
never an executable command copied from an untrusted receipt. Essential's
`render` operation renders canonical `state.md`; other required semantic child
artifacts remain explicit checked carriers and cannot be reconstructed by a
second parser or inferred from prose.

The source anchor must carry all relevant repository changes. Its three
allowed shapes are:

- `remote_revision`: `format: git-commit`, `encoding: git-object`, a retrievable
  repository/ref locator, a verified Git object-ID checksum, and
  `application.mode: checkout_revision` with the expected result tree.
- `patch`: `format: git-patch`, UTF-8 or base64 complete content/retrievable
  attachment, SHA-256, and `application.mode: apply_patch` with exact base and
  expected result tree.
- `bundle`: `format: git-bundle`, base64 inline content or an
  `encoding: binary` attachment, SHA-256, and
  `application.mode: fetch_bundle_ref` with exact base, bundle ref, result
  revision, and expected result tree.

A dirty workspace path, local-only revision, command string, or local payload
staging path is not sufficient. Before emitting the receipt, normalize and
contain all repository and destination paths, reject absolute paths, `..`, and
symlink escapes, and remove tokens, credentials, private keys, environment
values, and other secrets from payloads. Redaction must not make a required
source or state section incomplete; if it does, block and ask for a safe
carrier.

Specification sources are polymorphic. A `local` locator is authoritative only
when it is a contained repository-relative path present in the post-anchor Git
tree and its SHA-256 matches there. An ignored work-local specification cannot
use `kind: local`. An `inline` source carries the complete decoded content or a
retrievable attachment, SHA-256, destination, and `materialize_inline`
application. A `notion` source names the stable ref, captured remote revision,
paired remote transport/semantic hashes, format, destination, and a logical
transport profile; it is fetched fresh during takeover. Its
`notion_transport.stable_ref` equals the stable Notion `locator`.
`suggested_root` is optional, contained, repository-relative destination advice
only.

`portable_state.required` is false only when `status: success`, classification
is `initial`, `unchanged`, `metadata_only`, or `converged`, `next_action: none`,
and evidence proves there is no authored or otherwise pending local work. It is
true for `local_only`, `remote_only`, `structural_change`, `concurrent`,
`baseline_required`, or `materialization_conflict`, for an operational
`partial`/`blocked` status, and whenever `next_action` is not `none`. Never map a
sync result into a different classification merely to satisfy this predicate.

A required transfer is one complete checksum-bound
`specification-blr-transfer+json/v1` package created and later validated only by
the dependency-free helper in
[blr-transfer-format.md](blr-transfer-format.md). It contains the immutable B
receipt and exact B bytes plus the authored L tree; complete embedded
`spec-hash-input-v1` manifests and observed revisions; per-unit exact hashes;
and the independently recomputed B/L `transport_manifest_hash` and
`contract_digest`. Its receipt checksum covers the exact canonical package
bytes. Validation may materialize it only under a new isolated destination and
must recompute both dual-hash results with the bundled Specification helper
before any promotion. This package preserves reconciliation state—it is not a
selected mirror and is never an authoring authority by itself. If B does not
exist (`baseline_required`), the helper is unavailable, or the package cannot be
embedded or published at a retrievable attachment, handover is blocked rather
than inventing B or silently reducing the source to a Notion ref.

The receipt never stores the origin's absolute transport root,
worktree-relative interpretation, or any workspace-specific root. Takeover
resolves the logical profile (and, at most, uses the suggestion as a proposal)
into a separately validated exact destination-local transport root. Generic
coding work may use `spec_sources: []`.

## v2 migration

`engineering-work-handover/v2` is not directly rehydratable because it has no
checksum-bound complete state snapshot and its carrier application semantics
are underspecified. Before takeover writes anything, migrate it to v3 by
retrieving the original authoritative sources, constructing and validating the
complete `state_snapshot`, expanding every source/spec carrier into the v3
format/encoding/content-or-locator/checksum/application shape, and obtaining
new state-snapshot and carrier checksums. Replace any v2 Notion transport path
with a logical profile, stable ref, captured revision, paired
`transport_manifest_hash`/`contract_digest`, and optionally a contained
repository-relative suggested root. Add the required B/L package for every
non-clean sync state; never copy an absolute/workspace-specific root into v3.
If the original workspace or authoritative sources are unavailable, reject the
v2 receipt and request a new `coding:handover`; never infer missing state from
summaries.
