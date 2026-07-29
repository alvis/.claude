# Work-memory topology

Read this when creating, locating, or migrating ignored engineering work
memory. `engineering-work.md` owns the lifecycle and resolver;
`engineering-work-state.md` owns state semantics.

```text
.state                                  # ignored operational work memory in the default source tree
├── overview.md                         # global status index across every source tree
├── notion                              # default-source-tree Notion mirror
├── archive/<work-id>                   # parked idle stream; never enumerated by the resolver
└── works/<work-id>                     # one stream worked from any registered tree
    ├── goal.md                         # approved charter, scope, and success criteria
    ├── state.md                        # complete resumable context and canonical task graph
    ├── lease.json                      # coordinator ownership and expiry record
    ├── state                           # focused execution views and append-only history
    │   ├── working.md                  # narrow current focus and handback point
    │   ├── journal.md                  # append-only state transition record
    │   ├── revisions.md                # approved plan and charter revision history
    │   ├── unresolved.md               # unresolved questions and blocking unknowns
    │   ├── plan.md                     # optional non-authoritative task detail
    │   └── discovery.md                # resumable findings and evidence pointers
    ├── spec                            # temporary materialized specification inputs
    ├── proposals.md                    # lazy index of proposed choices
    ├── proposals/*.md                  # one proposed choice and its disposition
    ├── changes.md                      # lazy index of approved execution departures
    ├── changes/*.md                    # one approved departure and its evidence
    ├── decisions.md                    # lazy index of durable decisions
    ├── decisions/*.md                  # one accepted, rejected, or superseded decision
    ├── design.md                       # lazy index of work-local design
    ├── design/*.md                     # one design candidate or reasoning unit
    ├── review.md                       # review-area roll-up and closure status
    ├── reviews/*.md                    # one area-specific review and its findings
    └── artifacts                       # non-Markdown evidence and generated carriers
```
