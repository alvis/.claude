# Work-memory templates

Use the Essential engineering-work contract as authoritative. These shapes add
handover-specific content; all timestamps are one real UTC ISO-8601 value.

## `state.md`

```markdown
# <Work headline>

- Work ID: `<work-id>`
- Status: `<active|blocked|complete|retiring>`
- Updated: `<timestamp>`
- Current focus: [working.md](working.md)
- External anchor: `<task|issue|PR|Notion URL>`

## Goal and success criteria
## Complete lifecycle plan
## Current state and file status
## Approved decisions and accepted assumptions
## Dependencies, blockers, risks, and pivot signals
## Reviews and dispositions
## Evidence and validation
## Durable promotion
## Specification sync and revalidation
## Continuation
```

File substates: completed; `need-draft`; `need-completion`; `need-fixing`;
`need-testing`; `need-linting`; `need-refactoring`; blocked. Record path,
substate, remaining action, evidence, and blocker. Keep detail in `state/*.md`
only when the overview would otherwise require the shared split process.

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
schema: engineering-work-handover/v1
repository: <stable repository identity>
revision: <commit/change id>
branch_or_bookmark: <name or none>
work_id: <id>
external_anchor: <URL or response_only>
goal: <one sentence>
status: <active|blocked>
next_action: <one sentence>
spec_sources:
  - notion_id: <stable id>
    revision_or_hash: <value>
durable_refs: [<versioned docs paths>]
pending_decisions: [<id and owner/deadline>]
validation: [<command and result summary>]
sync_state: <verified|pending|conflict>
recheck_triggers: [<trigger>]
```

The receipt contains no ignored local path as an authoritative source. It is
enough to locate repository and Notion truth and reconstruct local memory.
