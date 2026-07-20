## 🧠 Design Patterns

| # | Pattern | Intent | Implemented In |
| --- | --- | --- | --- |
| 1 | `<Pattern Name>` | <why we picked it here> | `<src/file.ts>` |
| 2 | `<Pattern Name>` | <…> | `<src/file.ts>` |
| 3 | `<Pattern Name>` | <…> | `<src/file.ts>` |

---

<!--
🔌 EXTENSION POINTS — CONDITIONAL.
Include if consumers can plug in new behavior (strategies, adapters, plugins,
middleware). Omit for closed libraries.

The Steps column is a short numbered recipe; keep it imperative and grounded
in real file paths.
-->

## 🔌 Extension Points

<Paragraph framing the package as extensible and listing the extension seams.>

| Extension | Steps | Files Touched | Tests |
| --- | --- | --- | --- |
| `<Add a new X>` | 1. <step> 2. <step> 3. <step> | `<file-a>`, `<file-b>` | `<spec-path>` |
| `<Add a new Y>` | <…> | <…> | <…> |

---

<!--
🛡️ INVARIANTS & CONTRACTS — ALWAYS include.

The rules that MUST hold for the system to be correct. Each row answers:
  Rule (what must always be true) → Why (failure mode if violated) →
  Enforced By (where/how the invariant is guarded: types, asserts, tests).

Keep the list small (3–8 entries). If you can't explain the "why", it isn't
a real invariant.
-->

## 🛡️ Invariants & Contracts

| # | Rule | Why | Enforced By |
| --- | --- | --- | --- |
| 1 | <rule in plain english> | <failure mode> | `<type / assert / test>` |
| 2 | <…> | <…> | <…> |
| 3 | <…> | <…> | <…> |

---

<!--
📊 NON-FUNCTIONAL MATRIX — OPTIONAL.
Include for packages that have quantified non-functional goals (latency
targets, bundle size caps, throughput SLAs, security posture, observability
hooks). Omit for pure utilities where every row would be "n/a".
-->

## 📊 Non-Functional Matrix

| Concern | Target | Strategy | Instrumentation |
| --- | --- | --- | --- |
| Performance | <e.g. p99 ≤ 5ms> | <algorithm, caching, pooling> | <metric / trace / benchmark> |
| Security | <threat model summary> | <defense in depth> | <audit hook> |
| Observability | <logs / metrics / traces> | <structured events> | <exporter> |
| Reliability | <error budget> | <retries, idempotency> | <alert> |

---

<!--
🧭 ROADMAP — OPTIONAL.
Include only if the team maintains a public-facing architectural backlog. If
the roadmap lives in an issue tracker, link there and skip the section.
-->

## 🧭 Roadmap

- **<Short-term item>** — <rationale / acceptance>
- **<Mid-term item>** — <…>
- **<Long-term item>** — <…>

---

<!--
📦 RELATED PACKAGES — ALWAYS include.
Link workspace-internal siblings only. Use relative paths. Keep each line
to "what is it + what is the relationship".
-->

## 📦 Related Packages

- [`@scope/<sibling-a>`](../<sibling-a>): <relationship in one line>
- [`@scope/<sibling-b>`](../<sibling-b>): <relationship in one line>

---

<!--
WHEN TO SPLIT — coordinator guidance, not a section consumers read.
Finish and link the complete document first. Only the PM's final Markdown batch
may request a split.
-->

## When to Split

If the final batch reports this file above 16,384 bytes, split into:
- `docs/architecture/<architecture-slug>.md` — overview + cross-cutting concerns + system context diagram
- `docs/architecture/<architecture-slug>/<nn>-<subsystem>.md` — one per split subsystem, deep on its internals

The original architecture path remains the overview and links to each split
child. Multiple subsystems alone never force a split when the complete file is
at or below 16,384 bytes.

---

<!--
FOOTER NOTES:
- Do not add License / Contributing / Support — these live at the monorepo root.
- Keep the document scannable: a reader should grok the architecture in 5 minutes.
- Diagrams are the primary payload; prose exists to frame them.
-->
