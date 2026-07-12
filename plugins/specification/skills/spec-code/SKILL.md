---
name: spec-code
description: "Design or document technical specifications in the canonical template, then delegate Notion synchronization to sync-notion. Use for greenfield specs, updates to an existing DESIGN.md, or documenting an implementation without inventing requirements."
model: opus
context: fork
allowed-tools: Bash, Write, Read, Edit, Task, WebSearch, WebFetch, Glob, Grep, TodoWrite, AskUserQuestion, Skill
argument-hint: "<instruction> [--type=api|web-app|mobile|library|fullstack]"
---

# Spec Code

Produce `DESIGN.md` and its child documents in the strict Notion template
structure, in one of three modes: CREATE (greenfield design), UPDATE (modify
an existing spec), or DOCUMENT (analyze and document existing code).
`specification:sync-notion` owns all Notion transport and merging;
`specification:plan-code` owns commit planning; coding skills own
implementation.

## Boundaries

- Use for: designing a new specification, updating an existing `DESIGN.md`
  or Notion spec, or retrospectively documenting an existing implementation
  without inventing requirements.
- Do not use for: generating implementation code, making technology
  decisions without analysis, adding features or sections outside the
  template structure, or performing Notion pull/push/merge yourself
  (`specification:sync-notion`).
- Refuse when: the instruction is too vague to scope (ask for what the
  system does), the request is code implementation rather than
  specification, the spec would require implementation details nobody has
  decided, or the request adds sections the template does not define.

## Inputs

- **Required**: `<instruction>` describing what to specify or document.
- **Optional**: `--type=api|web-app|mobile|library|fullstack` to select
  template patterns; `--reference=<doc>` to load supporting documentation;
  `--sync-template` to reorganize an existing spec to the latest template
  while preserving content; `--skip-notion-sync` to write local files only.
- **Prerequisites**: for the sync step, `notion-sync` CLI and `NOTION_TOKEN`
  (not needed with `--skip-notion-sync`).

<IMPORTANT>
Coherence mandate: every edit must produce one continuous, deliberate
document. UPDATE and DOCUMENT modes are the high-risk surface — new
requirements must be folded into the spec's existing sections so a reader
cannot tell which decisions are original and which were merged later. Never
attach an "Addendum", "Revisions", or "Also note" trailer beneath the
template, and never leave parallel duplicate sections or visible patch
seams.
</IMPORTANT>

## Workflow

1. Detect the mode: CREATE when there is no `DESIGN.md`, no Notion page, and
   no codebase; UPDATE when `DESIGN.md` exists or a Notion page is found;
   DOCUMENT when a codebase exists but no `DESIGN.md`. Then load materials:
   the existing design (UPDATE), the codebase analysis workflow in
   [references/document-mode.md](references/document-mode.md) (DOCUMENT),
   the Notion template, any `--reference` documentation, and the
   `--sync-template` flag.
2. When existing Notion pages are found, record the local files and known
   refs for the final `Skill(sync-notion)` call. That skill owns remote
   materialization, conflict decisions, merged content, and verification —
   do not maintain a parallel merge protocol here.
3. Gather requirements: parse the arguments, clarify scope per mode with
   `AskUserQuestion` where the instruction leaves real choices open, and lay
   out the work as a todo list.
4. Research the tech stack: CREATE researches an appropriate stack; UPDATE
   researches only the technologies that change; DOCUMENT extracts the stack
   from existing code with no research — follow
   [references/document-mode.md](references/document-mode.md) for the
   project scan, manifest parsing, and mapping to spec sections.
5. Design the architecture (CREATE from scratch, UPDATE by modifying the
   affected aspects, DOCUMENT by extracting from code), then specify the
   components, API contracts and data models where applicable, and UI
   structure and components where applicable — always within the template's
   sections.
6. Generate or update the files: prepare frontmatter per
   [references/frontmatter.md](references/frontmatter.md) (the
   `notion_url`/`last_edited_at`/`last_synced_at`/`related_files` schema,
   filename mapping, and update rules), compile the document following the
   template exactly, apply `--sync-template` when provided, then write the
   main file and every child page file with frontmatter.
7. Unless `--skip-notion-sync`, invoke `Skill(sync-notion)` with the
   generated files, the selected sync mode, and any known Notion refs. That
   skill owns pull/push, merge resolution, verification, retries, and
   frontmatter sync metadata — do not implement a second synchronization
   protocol.
8. Run the verification below; when a check fails, fix the cause and re-run
   that check. Repeat until every check passes or a concrete blocker
   remains, then report the blocker instead of looping.

## Verification

- The document contains only template sections, in template order — nothing
  invented, nothing appended outside the structure.
- Every written file carries the frontmatter schema from
  `references/frontmatter.md`.
- In UPDATE and DOCUMENT modes, merged content is integrated into owning
  sections with no addendum trailers or duplicate parallel sections.
- The sync step reports verified success, or the skip is explicit
  (`--skip-notion-sync`) and recorded.

## Completion

Report the mode, package name, design document path and child documents,
project type and tech stack, template adherence, Notion sync outcome
(created/updated/skipped plus verification state from `sync-notion`), and
next steps: review the files, share for feedback, then plan implementation
with `specification:plan-code`. A refusal names what was too vague,
undecided, or outside the template.
