---
name: spec-code
description: Design, update, or retrospectively document a technical specification through an active engineering work item, Notion-backed MDC, and versioned derived docs. Use for specification authoring; keep transport in sync-notion and implementation planning in plan-code.
model: opus
context: fork
allowed-tools: Bash, Write, Read, Edit, Task, WebSearch, WebFetch, Glob, Grep, TodoWrite, AskUserQuestion, Skill
argument-hint: "<instruction> --work-id=<id> --capability=<slug> [--type=api|web-app|mobile|library|fullstack]"
---

# Spec Code

Author a technical specification as one coherent contract. Notion-backed MDC
is authoritative for specification content; versioned
`docs/specs/<capability>/*.md` is a reviewed derivation for engineers.

## Boundaries

- Use for CREATE, UPDATE, and DOCUMENT modes. Do not implement code or own
  Notion transport/conflicts.
- Never create independent root specification/design/requirement artifacts.
  Temporary reasoning belongs in the active work's `design/`, `proposals/`,
  `changes/`, or `decisions/`; durable specification docs belong under
  `docs/specs/<capability>/` only after verified completion.
- All authored `.mdc` changes route through `specification:mdc`; all materialize
  and completion flows route through `specification:sync-spec`.
- Preserve notion-sync-owned paths. Never infer a filename from title or id.

## Inputs

- **Required**: instruction, `--work-id=<id>`, and lowercase
  `--capability=<slug>`.
- **Optional**: project type, `--reference=<doc>`, `--discovery=<path>`,
  `--sync-template`, `--skip-notion-sync`.
- **Prerequisites**: active engineering work state and, unless sync is skipped,
  Notion credentials/tooling.

<IMPORTANT>
Coherence mandate: UPDATE and DOCUMENT edits must be integrated into their
owning sections. Never append an addendum, revisions trailer, parallel old/new
section, or copied transport history.
</IMPORTANT>

## Workflow

1. Before creating or materially rewriting a project artifact, read the
   absolute `engineering-work.md` path injected by Essential. If unavailable,
   stop artifact writes and report the missing contract. Resolve the active
   work root; read `working.md`, then `state.md`, then only their relevant
   references.
2. Select mode: CREATE when no authoritative Notion spec exists; UPDATE when it
   exists; DOCUMENT when current code must be described without inventing
   requirements. For UPDATE/DOCUMENT with an existing page, invoke
   `Skill(sync-spec)` in `materialize` mode and use returned `ref:` identities
   and paths. Load [references/document-mode.md](references/document-mode.md)
   only for DOCUMENT.
3. Gather requirements, discovery evidence, architecture, API/data contracts,
   UI behavior, security/privacy posture, acceptance criteria, and unresolved
   decisions. Preserve evidence provenance. Route underexplored material
   unknowns to `essential:discover` and grounded alternatives to
   `essential:decide`; do not turn assumptions into requirements.
4. Create or update the work-local design/proposal/decision children needed to
   explain the specification change. Use lowercase deterministic child names
   and the status schema in the Essential contract. Return an index
   reconciliation request to the PM; do not edit PM-owned overview files.
5. Prepare Notion MDC metadata and durable derivation metadata according to
   [references/frontmatter.md](references/frontmatter.md). Create or modify the
   work specification only through `Skill(mdc)`, preserving existing refs,
   hierarchy, paths, and unrelated metadata.
6. Unless `--skip-notion-sync`, invoke `Skill(sync-spec)` in `complete` mode.
   It delegates outbound/conflicts, verification pull, default-mirror refresh,
   derived `docs/specs/<capability>/` generation, durable receipt anchoring,
   locally discoverable revalidation notices, and unknown/remote dependent
   reporting. With the skip flag, leave content temporary under the work
   root; do not promote versioned docs or claim completion.
7. Verify the resulting derived spec reads as one contract, `index.md` points
   to all versioned children, and provenance matches the verification pull.
8. Return explicit final paths generated or materially rewritten as
`generated_files`, including work-local `.md` children and derived docs.
Do not run file sizing; after all writers return, the PM checks only eligible
work Markdown inside the target `.engineering/`. Derived `docs/**` has no
mechanical size limit.

## Verification

- The authoritative MDC contract contains no invented or duplicate sections.
- Every authored MDC body change went through `specification:mdc` and retained
  Notion identity/path.
- A completed run has verified Notion sync, verification pull, derivation
  provenance, `index.md`, and revalidation results; a skipped sync remains
  explicitly temporary.
- `generated_files` is complete and overview reconciliation is assigned to the
  PM.

## Completion

Report mode, work id, capability, authoritative Notion refs, work artifacts,
sync/verification result, derived specification paths and provenance receipt,
revalidation impact, PM index updates requested, and `generated_files`.
