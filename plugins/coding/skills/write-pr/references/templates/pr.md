<!--
Unified PR template for coding:write-pr (and coding:stack-code).

Required sections: Summary (first paragraph) + Checklist.
Optional sections: Context, Implementation, Breaking, Related, Testing, Notes.

Authors fill placeholders in `{{double_braces}}`. Drop any optional section
whose body is empty rather than leaving a stub.

Placeholder schema (for non-LLM callers performing literal substitution):

  Name                       Required  Source / Description
  -------------------------  --------  ----------------------------------------
  summary_paragraph          yes       Plain-language purpose, ≤3 sentences. Derived from commit body lead paragraph.
  context_body               no        Why this change is needed; bug links; design background. Drop section if empty.
  implementation_body        no        What was implemented; trade-offs; design choices. Drop section if empty.
  breaking_changes_body      no        Breaking-change list + migration notes. Drop section if commit subject lacks `!` and no `BREAKING CHANGE:` trailer.
  related_issues_body        no        `Closes #N`, spec links. Drop section if empty.
  manual_testing_body        no        Reviewer repro steps; screenshots. Drop section if empty.
  additional_notes_body      no        Known limitations, follow-ups. Drop section if empty.

Substitution rules:
- All placeholders are literal `{{name}}` tokens; no nesting, no expressions.
- An optional placeholder whose value is empty/whitespace MUST cause its entire
  section header (`## ...`) and body to be omitted from the rendered output.
- The Checklist block is fixed text — never substituted, never dropped.
- Output MUST be byte-stable for the same input map (deterministic ordering,
  trailing newline, no trailing whitespace).
-->

{{summary_paragraph}}

## 📝 Context

{{context_body}}

## 🛠️ Implementation

{{implementation_body}}

## ✅ Checklist

- [ ] Tests added or updated
- [ ] Docs updated where user-visible
- [ ] CI green locally
- [ ] No new lint or type errors
- [ ] Reviewer assigned per zone (`GIT-PR-SIZE-01..04`)

## 💥 Breaking Changes

{{breaking_changes_body}}

## 🔗 Related Issues

{{related_issues_body}}

## 🧪 Manual Testing

{{manual_testing_body}}

## 📋 Additional Notes

{{additional_notes_body}}
