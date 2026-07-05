# Skill-Authoring Invariants

The single source of truth for the normative rules every skill-authoring skill (`create-skill`, `update-skill`, `verify-skill`) enforces. Each authoring skill cites this file rather than restating a rule — with one deliberate exception: the **Coherence Mandate** paragraph, which each *editing* skill also carries inline in its Role/Purpose (see the note under that rule), because a skill whose own document violates the mandate cannot credibly enforce it.

## Coherence Mandate

> Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike.

**Inline requirement.** Any skill whose workflow performs content edits on existing work (prose, code, configuration, specs) MUST carry the paragraph above *verbatim*, woven into its own Role/Purpose narrative — not appended as a trailing bullet, callout, or standalone `## Coherence Mandate` section. The inline copy must mirror the canonical text here exactly. `verify-skill`'s Content Quality subagent checks for its inline presence (`grep -c "Coherence Mandate" ≥ 1`) and applies a seam test. This is the one invariant deliberately kept inline rather than referenced, for that reason.

## Content Placement & Coherence Rule

SKILL.md is one document with one voice — the always-on core workflow every invocation walks — and what it omits (or an update removes) must be rewritten out cleanly, not preserved as a vestigial trailing block. The same editorial stance governs both what stays in the file and how it stays:

> 1. **Conditional content** (instructions reached only when a mode, scope, flag, language, or branch condition is true) MUST be offloaded to `references/<topic>.md` and referenced from SKILL.md by a one-line pointer woven into the surrounding step (e.g. `For two-way merge mode, see references/two-way-merge.md`) — not parked beneath the workflow as a "Modes" or "Variants" addendum.
> 2. **Bulky AND conditional** content (>~50 lines, branch-only) MUST be offloaded. If the conditional branch is itself a coherent independently-triggerable workflow, **split it into a separate skill** rather than letting it sit as a parallel path inside the current one.
> 3. **Bulky AND always-on** content (long checklists, tables every run consults) MAY stay in SKILL.md if every invocation uses it; offload only if it is genuinely optional.
> 4. **Non-bulky conditional** content (short `if X then do Y` lines) MAY stay inline.
> 5. **Editing skills carry the Coherence Mandate inline.** Any skill whose workflow performs content edits on existing work MUST carry the verbatim Coherence Mandate paragraph woven into its own Role/Purpose narrative (see above) — integrating it if a target is missing it, and dissolving it back into the role description if a prior edit left it bolted on as a separate section, so the seam is invisible.

Rationale: SKILL.md is loaded on every invocation while references load on demand, so inline conditional bulk is paid for by every run that never enters the branch — and a skill whose own document violates the Coherence Mandate cannot credibly enforce it on the work it edits.

## Section & Report Boundary Convention

Each important section of a skill is encircled with a semantic XML boundary tag, so every major part of the document carries an unambiguous, machine- and eye-visible boundary and its content cannot bleed into a neighbour. Tags wrap the section **alongside** its markdown heading — the heading stays for readability and for the existing template-compliance checks; the tag adds the boundary. Tags never replace headings.

The tag set:

| Tag | Encircles |
|---|---|
| `<introduction>` | The `## 1. INTRODUCTION` section — Purpose & Context and Your Role |
| `<skill_overview>` | The `## 2. SKILL OVERVIEW` section — I/O Specification and Visual Overview |
| `<skill_implementation>` | The `## 3. SKILL IMPLEMENTATION` section — Content Placement, Skill Steps, every Step, and Skill Completion |
| `<report>` | Every machine-readable report / output contract — each subagent report, each step report, and the final Skill Completion output |

Rules:

- **Subagent-prompt envelopes keep the `>>>` / `<<<` delimiters** — they already encircle the prompt payload, and the `<report>` block lives *inside* the envelope. Do not convert `>>>` to a tag.
- **Tags wrap alongside headings, never replace them** — keep the markdown heading as the first line inside the opening tag.
- **Retain a language hint** on a fenced report where it aids reading (` ```yaml ` inside the `<report>` tags) — the tags are the boundary, the fence is the syntax hint.
- **Balanced and non-overlapping** — every opening tag has a matching close, and `<report>` nests cleanly inside `<skill_implementation>`.

`verify-skill`'s Template Compliance subagent checks for these boundaries and reports `boundary_tags`. The check is a non-blocking recommendation ("encourage"), so skills authored before this convention are flagged for gradual migration — via `update-skill` — rather than failed.
