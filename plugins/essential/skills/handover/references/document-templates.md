# Work-memory templates

Use the Essential engineering-work contract as authoritative. These shapes add
handover-specific content; all timestamps are one real UTC ISO-8601 value.

## `state.md`

```markdown
# <Work headline>

- Work ID: `<work-id>`
- Lifecycle status: `<initialized|active|blocked|complete|retiring>`
- Updated: `<timestamp>`
- Current focus: [working.md](state/working.md)
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

## `state/working.md`

```markdown
# Current focus

- Updated: `<timestamp>`
- Status: `<one sentence>`
- Working now: `<one narrow outcome>`
- Handback point: `<exact next action or blocker>`

## Fast paths
- State: [state.md](../state.md)
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

The receipt is plain Markdown a human can paste. It carries no JSON snapshot, no
base64 bundle, no checksums, and no schema version line. It contains, in order:

```markdown
## Handover receipt

- Repository: <stable remote/name identity>
- Work ID: <work-id>
- Branch: <name or none>
- Base commit: <commit/change id>
- External anchor: <URL or response-only>

## Source anchor

<How to obtain the code at the right revision, with plain git and no checksum
verification — exactly one of:>
- Remote revision to check out: `<remote/ref @ revision>`
- Attached patch: `git format-patch` output, inline below or at <attachment locator>
- Bundle ref: `git bundle` at <attachment locator>, ref `<ref>`, base `<base commit>`

## Work state

<The raw contents of state.md, state/working.md, and every continuity-relevant
detail file — decisions, changes, design, state/*.md children, needed evidence —
each in its own fenced block labelled with its work-relative path:>

`state.md`

```markdown
<verbatim contents>
```

`state/working.md`

```markdown
<verbatim contents>
```

`decisions/<slug>.md`

```markdown
<verbatim contents>
```

## Specifications

<Any spec contract needed to continue, inline as raw text or as a
repository-relative path in the anchored tree. Omit this section for generic
coding work with no specification.>

## Continuation

- Current task: <full executable task ID or none>
- Next owner: <exact continuation owner>
- Next action: <one sentence>
- Continuation intent: <capability-level work type — e.g. specification-led implementation or generic coding implementation — never a fixed skill name>
- Route: hand off to the relevant implementation skill to continue the work.
```

Each `## Work state` block is the verbatim content of one work file, labelled
with its work-relative path so takeover can write it straight back. Include
every file needed to continue without the origin `.engineering/` tree; do not
summarize, elide, or replace a file's content with a pathname. Redact secrets,
credentials, private keys, and environment values from every embedded block; if
redaction would leave a required section incomplete, block and ask for a safe
carrier.

The source anchor must carry all relevant repository changes as one of the three
plain-git shapes above. A dirty workspace path, a local-only revision, or a
command string is not an anchor. Normalize and contain every repository and
destination path; reject absolute paths, `..`, and symlink escapes.

Specifications are optional. Reference a specification by a repository-relative
path when it is present in the anchored tree, or embed its raw text inline when
it is not. A Notion-backed specification is named by its stable ref and captured
revision so takeover can fetch it fresh. Generic coding work omits the section.

`Continuation intent` is a required capability-level descriptor of the work type
to continue — for example `specification-led implementation` when a spec governs
the next action, or `generic coding implementation` when none does. It names the
kind of work, never a fixed skill name; takeover maps it to the relevant
implementation skill. Emit it consistently with `Next action` so the two agree.
