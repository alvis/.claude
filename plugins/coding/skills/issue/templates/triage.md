# Triage response

Prefer a repository response template when applicable. Otherwise start with 📌 and one concise outcome heading. Render only the selected disposition and relevant related-work section; never publish empty slots or duplicate comments for classification, relationships, and analysis.

| Disposition | Heading | Required content |
| --- | --- | --- |
| Duplicate | 🔁 Duplicate of #N | Evidence of the same underlying issue; canonical reference; closing action only after comment verification |
| Feature/Task | 🏷️ Classified as Feature/Task | Intended behavior or maintenance evidence; bug triage ends |
| Missing information | ❓ Information Needed | Specific missing inputs and how they enable investigation |
| Supported cause | 🔎 Analysis | Cause or clearly marked hypothesis; inspected revision; standalone verified code permalinks; reproduction status; next step; no fix claim |
| Inconclusive | 🔎 Analysis | What was inspected and remains unknown; minimal reproduction request; waiting outcome |

Use `## 🔗 Related Work` for distinct related issues and explain the difference. Use `## 🧪 Evidence` and `## 🛠️ Next Step` when they carry additional evidence/action. A waiting skip produces no GitHub response; report the reason locally instead.
