---
name: sync-spec
description: Materialize a required Notion specification into an active engineering work directory or complete approved specification changes through an explicitly selected local transport pair. Use before specification planning, implementation, or review and when publishing a reviewed contract. Delegate transport and conflicts to sync-notion.
model: opus
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, TodoWrite, Skill, AskUserQuestion
argument-hint: "<notion-url-or-id> [--work-id=<id>] [--mirror=<path>] [--transport-profile=<absolute-file>] [--mode=materialize|complete] [--stage=specification|implementation] [--capability=<slug>]"
---

# Sync Spec

Safely coordinate three copies of a Notion-backed specification: an immutable
recorded base, the work-local authored copy, and a fresh remote staging pull.
`specification:sync-notion` owns transport; `specification:mdc` owns authored
MDC body changes. Exact transport integrity and semantic contract approval use
the distinct hashes defined in
[references/hash-model.md](references/hash-model.md).

## Boundaries

- `materialize` obtains a fresh remote view, then creates or refreshes only the
  requested page tree under `.engineering/work/<work-id>/spec/` when the
  base/local/remote decision permits it.
- `complete` is a publication gate. It reconciles the authored copy with a
  fresh remote view, verifies stage-specific approval, delegates guarded
  transport, verification-pulls, derives `docs/specs/<capability>/`, and
  reports dependent work that needs revalidation.
- Never derive or rename an MDC filename. Select files by stable `ref:` and the
  transport relationship report.
- Never call `notion-sync` directly, treat the selected mirror as an authoring
  surface, overwrite a fixed receipt, or infer that cached mirror bytes are the
  latest remote bytes.
- Never use a semantic digest as remote revision/CAS evidence or bind an
  approval, plan, or review to an exact transport hash.

## Inputs

- **Required**: Notion URL or page id.
- **Optional**: work id, exact `--mirror=<path>`, mode (default
  `materialize`), lowercase capability slug, and a verified creation receipt
  for an explicitly created new page.
- **Required for every Notion operation**: an explicit absolute
  `--transport-profile=<file>`, or an active-state destination mapping that
  names one absolute profile file, its last verified exact-byte SHA-256, and
  logical profile name. The mapping selects a file only; `sync-notion`
  revalidates its current bytes/executable on every invocation. Never infer a
  profile path from a logical name, mirror, workspace, or origin receipt.
- **Completion only**: `--stage=specification|implementation` is required.
  Specification stage requires explicit specification approval for the final
  semantic `contract_digest`. Implementation stage requires a clean
  implementation review whose compatibility field `reviewed_spec_hash` equals
  that final `contract_digest` and declares
  `hash_kind: semantic_contract_digest_v1`.
- **Prerequisites**: injected Essential engineering-work contract, resolved
  active work, the strict destination/team profile required by `sync-notion`,
  and `NOTION_TOKEN`.

## Workflow

1. Read the absolute injected `engineering-work.md` contract before artifact
   writes. If unavailable, stop artifact writes and report the missing
   contract. For a direct run, invoke Essential's workspace
   resolver with `--work-id` only for an explicit user override; ask only on
   `work_id_required`. A delegated run receives the explicit id/root. Resolve:
   - `work_spec_root = <active>/.engineering/work/<work-id>/spec`;
   - `mirror_root` from explicit input, active state, or an immutable receipt;
   - `transport_profile_file` from explicit input or the exact validated
     active-state mapping described above;
   - `receipt_root = <work-dir>/evidence/spec-sync`;
   - immutable receipts at
     `materializations/<transport-manifest-key>.json` and base snapshots at
     `bases/<transport-manifest-key>/`, where the key is the 64 lowercase hex
     suffix without the `sha256:` prefix.
   State may point to the current receipt, but the PM owns that update. Require
   the real work/mirror targets to be ignored and untracked in their owning VCS
   workspaces; otherwise return `requires_ignore` with the exact ignore file.
   Require the mapped logical name to equal the selected profile's `name` and
   pass the absolute file explicitly to every transport call. A missing,
   ambiguous, moved, or digest-shifted mapping returns `transport_unverified`;
   never fall back to `PATH` or a conventional file location.
2. Normalize the Notion id only for identity comparison and require 32 hex
   characters after dash removal. Resolve the selected recursive page set by
   returned `ref:`/relationship data, never filename shape. Load
   [references/hash-model.md](references/hash-model.md) and
   [references/concurrent-edit-matrix.md](references/concurrent-edit-matrix.md).
   Reject malformed/ambiguous carriers, duplicate identities/paths/logical
   unit ids, and receipts that do not declare the dual-hash model. Use the
   three-copy rules for every later decision.
3. Before either mode decides anything, invoke `Skill(sync-notion)` in
   `notion-to-local` mode with the exact mirror root and
   `--transport-profile=<transport_profile_file>` into a unique remote staging
   directory. Verify full
   requested coverage, stable identity, revision evidence, and deterministic
   exact-byte `transport_manifest_hash` plus semantic `contract_digest`. Store
   per-file hashes and exact pulled bytes as immutable evidence. Do not refresh
   the selected mirror or work copy yet.
4. In `materialize` mode, compare the current authored tree L and fresh remote
   staging R with immutable base B. Report operational `status` separately from
   `classification` and `next_action`. Before declaring `metadata_only`, compare
   every helper unit and require identical carrier kind, stable identity,
   logical id, path, and semantic-projection hash; only `observed_revision` and
   the uniquely allowed `last_edited_time` line may differ. A stable-identity,
   logical-id, or carrier-kind shift is invalid evidence and returns
   `status: refused`, `classification: invalid_evidence`, and
   `next_action: repair_evidence`. A verified path/layout rename with identities intact is
   `structural_change`, invalidates dependent evidence, and is never
   metadata-only:
   - absent L/B establishes the first base by atomic staging and promotion and
     returns `status: success`, `classification: initial`, and
     `next_action: none`;
   - absent B with existing L returns `status: refused`,
     `classification: baseline_required`, and
     `next_action: establish_baseline`, and preserves L,
     except that a verified new-page creation receipt may establish the initial
     base only when it preserves pre-create L, proves creation authorization
     and the stable identity/parent transition, and records post-create
     approval plus exact verification evidence for R; atomically promote that
     verified R as initial L/B;
   - clean L plus unchanged R returns `status: success`,
     `classification: unchanged`, and `next_action: none`;
   - semantic B/L/R equality with a remote-only exact transport change that
     passes the structured-unit restriction above returns `status: success`,
     `classification: metadata_only`, and `next_action: none`, atomically
     refreshes the exact transport bytes and
     revision, and creates a new immutable base/receipt without invalidating
     approval, plan, code, or review;
   - clean L plus a remote structural change atomically promotes the fully
     staged/verified R tree, creates a new base/receipt, and returns
     `status: success`, `classification: structural_change`, and
     `next_action: revalidate`; it invalidates approval, plan, code, and review
     even if `contract_digest` happens to remain equal;
   - clean L plus changed R atomically refreshes L/mirror, creates a new
     hash-addressed base/receipt, and returns `status: success`,
     `classification: remote_only`, and `next_action: revalidate` when plan,
     review, or implementation evidence exists;
   - dirty L plus unchanged R returns `status: success`,
     `classification: local_only`, and `next_action: none`, and preserves L;
   - dirty L plus a semantic or structural remote change returns
     `status: success`, `classification: materialization_conflict`, and
     `next_action: resolve_conflict`, preserves every
     canonical byte, and reports B/L/R paths and manifest differences.
   Stage and verify the complete selected tree before any atomic promotion;
   retain rollback bytes until both promoted manifests verify.
5. In `complete` mode, require a valid stage and compare B/L/R before canonical
   writes. Missing B is `status: refused`, `classification: baseline_required`,
   and `next_action: establish_baseline`; unchanged and converged content need
   no push; local-only content may proceed through its exact-hash stage gate;
   remote-only or structural change is `status: success` with
   `next_action: revalidate` and no push;
   concurrent content requires an explicit three-way merge. Workers may return
   conflict packets/proposals only. The PM/user owns choices, and `Keep Both`
   requires explicit approval of the synthesized final contract digest. Any
   `Skip` leaves that pair's local, mirror, and remote bytes untouched and
   forbids a push. A concurrent relationship at `stage=implementation` returns
   `status: success`, `classification: concurrent`, and
   `next_action: specification_reconciliation` with B/L/R evidence and proposals;
   it must not apply or push merged content at implementation stage. The source
   owner must author the selected merge, complete it through
   `stage=specification`, verification-pull it, establish a new immutable
   base/receipt, and materialize that base before any plan or implementation
   resumes.
6. Freeze each selected pair's final proposal and recompute both hashes. For
   `stage=specification`, require explicit specification approval naming the
   exact final semantic `contract_digest`. For `stage=implementation`, require
   the clean implementation review's `reviewed_spec_hash` to name that exact
   final digest. Any semantic edit after the gate invalidates it; a declared
   metadata-only transport refresh does not, but must refresh exact evidence.
   Apply approved authored changes only to a staged mirror copy through
   `Skill(mdc)`.
7. Immediately before each outbound operation, use `Skill(sync-notion)` to
   re-fetch/re-diff the exact remote revision and transport manifest hash,
   passing the same exact `--transport-profile` file and mirror root.
   Abort and restart on any exact change, even when the semantic digest remains
   equal, so the base/revision evidence can be refreshed. Require the pinned
   transport to prove conditional-update support and record that condition.
   If a valid profile declares it unavailable, propagate `status: refused`,
   preserve the observed B/L/R classification, set
   `next_action: provide_conditional_transport`, and leave Notion plus
   canonical L/mirror bytes unchanged. A malformed, mismatched, moved, or
   unproven profile remains `transport_unverified`. Push only a fully resolved
   pair, then perform an independent verification pull.
8. Only after verified identity/content may canonical L/mirror state advance.
   Create a new immutable base directory and hash-addressed receipt; never
   rewrite an earlier base or receipt. A partial remote write is `partial` with
   exact recovery evidence, not success. Regenerate affected versioned specs
   under `docs/specs/<capability>/` with stable source id/revision/hash and a
   durable task/PR/Notion receipt anchor. The receipt and report store both the
   exact transport manifest hash and semantic contract digest. The embedded
   output hash set in `provenance.json` excludes `provenance.json` itself; store
   its post-write exact hash only in work/external evidence and the report.
9. Enumerate locally registered Git worktrees and jj workspaces. For readable
   open work on the same source id whose recorded hash changed, keep
   `status: success`, set `next_action: revalidate`, and return workspace/work/
   state paths; list external anchors and unknown/remote dependents separately.
   Never edit another PM's state.
10. Return every final path created or materially rewritten as
    `generated_files`. The PM runs the Essential size gate only on eligible
    work Markdown; derived `docs/**` is excluded.

<IMPORTANT>
The selected mirror is ignored, untracked transport state. It is not durable
documentation or a handoff artifact. Preserve its exact user-selected location.
</IMPORTANT>

## Verification

- B is immutable, L is the authored copy, and R came from a fresh staging pull.
- Exact transport manifests contain stable identities, revisions, and full
  accepted bytes; semantic digests used the declared deterministic projection.
- Existing local bytes changed only in an allowed matrix row; conflict,
  `baseline_required`, remote-only, and skipped outcomes did not push.
- The approval/review digest equals the final semantic contract digest, and the
  immediate remote recheck matched the exact comparison revision/manifest.
- Every successful publication has a verification pull and a new
  hash-addressed base/receipt; no fixed `materialization.json` was overwritten.
- MDC content and Notion transport stayed with their owning skills.

## Completion

<report>

```yaml
skill: sync-spec
status: success|partial|refused|requires_ignore|transport_unverified
classification: initial|unchanged|metadata_only|local_only|remote_only|structural_change|converged|concurrent|baseline_required|materialization_conflict|invalid_evidence|not_applicable
next_action: none|revalidate|establish_baseline|resolve_conflict|specification_reconciliation|recover_partial|repair_evidence|provide_conditional_transport
mode: materialize|complete
stage: specification|implementation|null
work_id: '<id>'
hash_model: specification-dual-hash-v1
transport_profile: {logical_name: '', profile_file: '<absolute destination-local path>', profile_file_sha256: '', verification: verified|transport_unverified}
outputs:
  transport_mirror: '<absolute selected path or null>'
  work_spec_root: '<absolute active-workspace path>'
  base_snapshot: '<absolute immutable path or null>'
  materialization_receipt: '<absolute hash-addressed path or null>'
  notion_root: {id: '<32hex>', path: '<notion-sync-owned path>'}
  comparison:
    classification: initial|unchanged|metadata_only|local_only|remote_only|structural_change|converged|concurrent|baseline_required|materialization_conflict|invalid_evidence|not_applicable
    base: {transport_manifest_hash: '', contract_digest: ''}
    local: {transport_manifest_hash: '', contract_digest: ''}
    remote: {transport_manifest_hash: '', contract_digest: '', revision: ''}
    transport_manifest_key: '<64 lowercase hex or empty>'
  publication: {approved_contract_digest: '', reviewed_spec_hash: '', reviewed_hash_kind: semantic_contract_digest_v1|null, remote_rechecked: false, required_capability: conditional_update|conditional_create|null, conditional_write: false, pushed: false, verified: false}
  reconciliation: {required: false, reason: null, conflict_packet_paths: [], invalidated: []}
  provenance: {path: '', embedded_output_paths: [], self_hash_external: ''}
  revalidation: {local_registered: [], external_receipt_anchors: [], unknown_or_remote_dependents: []}
generated_files: []
issues: []
```

</report>

Use these deterministic top-level mappings: missing base → `status: refused`,
`classification: baseline_required`, `next_action: establish_baseline`; dirty
materialization with remote semantic/structural change → `status: success`,
`classification: materialization_conflict`, `next_action: resolve_conflict`;
implementation-stage concurrent change → `status: success`,
`classification: concurrent`, `next_action: specification_reconciliation`;
remote-only semantic/structural change or a success that invalidates dependents
→ `status: success`, matching classification, `next_action: revalidate`;
ambiguous/partial remote mutation → `status: partial`,
`next_action: recover_partial`; policy/precondition failure →
`status: refused`, `classification: invalid_evidence|not_applicable`, and
`next_action: repair_evidence` when repairable.
Verified absence of the conditional capability required for publication →
`status: refused`, preserve the observed B/L/R classification, and
`next_action: provide_conditional_transport`, with no remote or canonical-local
mutation.
An absent or mismatched transport profile/mapping propagates
`transport_unverified`; missing mirror ignore coverage propagates
`requires_ignore`.
