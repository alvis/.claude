# Essential

The backbone every other plugin depends on. Essential owns the cross-plugin
**engineering-work lifecycle**: how work gets a durable identity, how its
state survives crashes and machine moves, how decisions and approvals stay
honest as reality changes, and how work retires without losing anything
consequential. It also carries the research/decision skills and the agent
installer.

## The contracts

Contracts load progressively — only the small `CLAUDE.md`/`MAINAGENT.md`/
`SUBAGENT.md` entry points are injected into every session; everything else
is read at the moment it matters.

| Reference | Read when | Owns |
| --- | --- | --- |
| `references/engineering-work.md` | Before creating or rewriting any lifecycle-managed artifact | Topology (`docs/` + `.engineering/`), resolver/bootstrap, coordinator lease and write protocol, journal discipline, overviews, reviews, spec freshness, promotion, retirement |
| `references/engineering-work-state.md` | When writing or migrating a `state.md` | Task table shape, stable IDs, mark/status pairs, DAG and roll-ups, change control, journal grammar, portable handover shape |
| `references/truth.md` | Once per work stream | Six kinds of truth, the five constitutional rules, validity, `capability_id` |
| `references/decision-causality.md` | When creating/accepting/superseding a decision | `supersedes`/`affects`/`invalidates`/`preserves`, blast-radius sweep, decision completion gate |
| `references/checkpoints.md` | At checkpoint moments and when recording approvals | Durable checkpoints at the external anchor, the approval binding tuple, freshness metadata |
| `references/anchors.md` | For non-git anchors or cross-stream initiatives | Anchor declarations, adapter contract, initiative manifests |
| `references/lease.md` | Before coordinator writes | `ensure` choreography, the lease-verified write path, release moments |
| `references/overviews.md` | When reconciling lazy overviews | Proposals-vs-changes, child statuses, deviation provenance |
| `references/reviews.md` | When writing review artifacts | The seven engineering areas plus plugin-namespaced areas, finding lifecycle |
| `references/spec-lifecycle.md` | When materializing or revalidating specs | Mirrors, freshness sweep, completion verification |
| `references/change-control.md` | On a mid-execution finding | Task-local / plan-level / spec-level routing |
| `references/retirement.md` | When promoting, parking, or retiring | Promotion provenance, idle-stream parking, retirement gates |
| `references/team-lifecycle.md` | At spawn and wind-down moments | Team forming/retiring, model and effort selection |

Templates: `templates/memory.md` (agent memory), `templates/checkpoint.md`
(checkpoint block), `templates/asset-manifest.md` (media asset/render
identity, used by the `production` plugin).

## The tools (`bin/`)

- **`resolve-engineering-workspace`** — resolves the work identity and paths,
  enforces the `.engineering/` ignore gate and symlink/traversal safety, and
  performs the PM-only no-clobber bootstrap of `goal.md`, `state.md`,
  `state/working.md`, and `state/journal.md`.
- **`engineering-lease`** — the on-disk coordinator lease
  (`ensure | acquire | heartbeat | release | status | takeover`). The file
  stores only the token's SHA-256 digest, so reading it never confers the
  lease; exactly one live token may write coordinator-owned state; a live
  foreign lease is never replaced; an expired foreign lease yields only to
  an explicit, journaled takeover.
- **`engineering-state-write`** — the lease-verified write path: verifies
  the presented token, refuses free/expired/foreign leases, heartbeats, and
  applies the temp-write + atomic rename in one call, so a working
  coordinator can never expire its own lease by working.
- **`engineering-doctor`** — read-only structural checker: duplicate or
  malformed task IDs, dangling dependencies, cycles, impossible roll-ups,
  contradictory mark/status pairs, missing evidence annotations, broken file
  references, unsuperseded decisions, stale leases, overview drift. Advisory
  by default; `--strict` for irreversible or release-critical moments. It
  never judges prose and never edits files.
- **`derive-engineering-name`** — the only slug/work-id derivation
  implementation.
- **`check-markdown-size`** — the 16,384-byte gate for work Markdown.

## Skills

| Skill | Use when |
| --- | --- |
| `essential:discover` | Finding material unknowns before planning: blindspot passes, brainstorms, interviews, reference extraction, disposable prototypes. |
| `essential:decide` | Choosing between researched approaches; records the approved decision with causal metadata and hands off to the owner. |
| `essential:deep-research` | Multi-source fact-finding with adversarial claim verification and citations. |
| `essential:autoresearch` | Metric-driven optimization loops (define metric → evolve candidates → verify → mutate). |
| `essential:handover` | Pausing or transferring work: persists all stream state, updates the cross-tree overview, emits the portable receipt, releases leases, emits the handover checkpoint. |
| `essential:takeover` | Resuming paused work, locally or from a receipt: checks leases, resolves blocking decisions, and drives streams to their success criteria. |
| `essential:doctor` | Health-checking `.engineering/`: runs the structural doctor, diagnoses format drift against the current contracts, and offers user-approved migration to the latest structure — judged by reading the contracts, never a version token. |
| `essential:handoff` | A zero-context cross-domain orchestration plan another agent can execute verbatim. |
| `essential:install-agents` | Installing/refreshing the stitched specialist agent roster into `~/.claude/agents/`. |
| `essential:install-statusline` | Installing the bundled Bullet Train statusline. |

## How state stays trustworthy

- **Append first, reconcile second.** Every transition lands in
  `state/journal.md` (with actor `capability_id`, `rev:<N>`, event type, and
  what it invalidates) before tables update; crash loss is bounded to one
  line.
- **One writer.** The lease holder alone writes `goal.md`, `state.md`,
  `state/*.md`, overviews, and `review.md`; workers return deltas.
- **Done stays done.** Invalidation marks `validity: stale` and spawns
  remediation tasks; history is never falsified.
- **Deleting `.engineering/` loses convenience, not truth.** Decisions,
  approvals, and artifact identities also live in versioned docs and
  checkpoints at the stream's external anchor.
