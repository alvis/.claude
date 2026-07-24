<!--
Default PR template for coding:write-pr (coding:commit --create-pr delegates
there).

This is the **default** PR template used when the repo has no GitHub PR
template of its own checked in (e.g. `.github/PULL_REQUEST_TEMPLATE.md`).
When a repo template exists, that template takes precedence and is emitted
verbatim instead of this one.

Required sections: Summary + Verification.
Optional sections: Context, Implementation, Breaking, Related, Boundary, Notes.

The order is a single arc — why, what, what it costs, what to check, where it
stops — with lookup material last. Authors fill placeholders in
`{{double_braces}}`; the guidance comment above each one says what belongs
there.

Placeholders (for non-LLM callers performing literal substitution):

  Name                       Required  Source / Description
  -------------------------  --------  ----------------------------------------
  summary_paragraph          yes       Plain-language purpose, ≤3 sentences. Derived from commit body lead paragraph.
  context_body               no        Why this change is needed; bug links; design background. Drop section if empty.
  implementation_body        no        What was implemented; trade-offs; design choices; evidence and results. Drop section if empty.
  breaking_changes_body      no        Breaking-change list + migration notes. Drop section if commit subject lacks `!` and no `BREAKING CHANGE:` trailer.
  verification_body          yes       Checklist of the checks that must pass before sign-off, ticked as each is confirmed.
  boundary_body              no        Related work the instruction placed outside this change. Drop section if empty.
  additional_notes_body      no        Known limitations, follow-ups. Drop section if empty.
  related_issues_body        no        `Closes #N`, spec links. Drop section if empty.

Substitution rules:
- All placeholders are literal `{{name}}` tokens; no nesting, no expressions.
- An optional placeholder whose value is empty/whitespace MUST cause its entire
  section header (`## ...`) and body to be omitted from the rendered output.
- Every guidance comment is author-facing and MUST be stripped from the
  rendered body, including this block.
- Verification is required: it is never dropped, even when every item is still
  unticked.
- Output MUST be byte-stable for the same input map (deterministic ordering,
  trailing newline, no trailing whitespace).
-->

📌

<!-- purpose and main changes in plain language, ≤3 sentences -->
{{summary_paragraph}}

## 🧵 Context

<!-- why this change is needed: problem, symptoms, tickets, design background -->
{{context_body}}

## 🛠️ Implementation

<!-- what was built and how; trade-offs, architectural choices; evidence and
     results belong here, not in Verification -->
{{implementation_body}}

## 💥 Breaking Changes

<!-- what breaks, and the migration for it -->
{{breaking_changes_body}}

## 🧪 Verification

<!-- checks that must pass before sign-off, specific to this change, ticked as
     each one is confirmed; a check, never a result or an observation.
     Pick from these where they apply: tests added or updated · docs updated
     where user-visible · CI green locally · no new lint or type errors ·
     reviewer assigned per zone (GIT-PR-SIZE-01..04) -->
{{verification_body}}

## 🚫 Boundary

<!-- bullets naming related work the instruction placed outside this change,
     so its edges are not read as gaps; not the author's own judgment calls -->
{{boundary_body}}

## 📋 Additional Notes

<!-- known limitations, follow-ups, anything else a maintainer needs -->
{{additional_notes_body}}

## 🔗 Related Issues

<!-- Closes #N, See #N, spec links -->
{{related_issues_body}}
