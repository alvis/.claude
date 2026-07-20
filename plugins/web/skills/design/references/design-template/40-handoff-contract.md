# Design handoff contract

## 10. Design Context & Decision Log

**Target and audience**: {{TARGET_AUDIENCE_PRIMARY_TASK_AND_USAGE_CONTEXT}}

**Inputs and constraints**: {{URL_SCREENSHOT_CODE_FIGMA_BRAND_ACCESSIBILITY_RESPONSIVE_PERFORMANCE_CONTENT}}

**Authorization**: {{design-only|implementation-authorized|ambiguous}}

**Evidence root**: `../evidence/design/{{DESIGN_SLUG}}/`

**Chosen direction** (3-line Direction Summary, verbatim from the direction gate):

> {{DIRECTION_SUMMARY_LINE_1}}
> {{DIRECTION_SUMMARY_LINE_2}}
> {{DIRECTION_SUMMARY_LINE_3}}

**Rejected direction candidates**:

| Candidate | Why rejected |
|---|---|
| {{CANDIDATE_NAME}} | {{ONE_LINE_RATIONALE}} |

**Per-area design picks** (one row per area board, recorded immediately after each pick):

| Area | Chosen variant (# + name) | Rejected variants + one-line why |
|---|---|---|
| {{Hero}} | {{#2 "Split editorial"}} | {{#1 too dense for the audience; #3 weaker hierarchy / repeated separator / off-direction imagery}} |
| {{Connective tissue}} | {{#1 "Fade + band system"}} | {{#2–3 one-line reasons}} |

**Exemplar sites** (facelift runs — the rubric anchors):

| Exemplar | What it anchors |
|---|---|
| {{EXEMPLAR_URL}} | {{TECHNIQUE / QUALITY BAR IT REPRESENTS}} |

**Hard constraints**: {{BRAND_RULES, LEGAL, PLATFORM, PERFORMANCE — anything that binds the design}}

**Decision log** (every presented candidate, pick, rejection, confirmation, and follow-up; dated):

| Date | Decision ID | Area/question | Presented and ranked | Chosen | Rejected + reason | Confirmation/next action |
|---|---|---|---|---|---|---|
| {{YYYY-MM-DD}} | {{d-001}} | {{Direction}} | {{#1..#N with concrete details}} | {{pick/merge}} | {{alternatives + reason}} | {{user/quick rationale + follow-up}} |

---

## 11. Component Inventory & Sources

Every component this design touches, where it comes from, and its reuse status:

| Component | Source | Path | Consumers | Promotion status / follow-up |
|---|---|---|---|---|
| {{Button}} | {{library / patched-upstream / local}} | {{src/components/ui/button.tsx}} | {{routes/features using it}} | {{e.g. "local — promote to packages/ui when checkout ships (second consumer)"}} |

Source values: `library` (consumed as-is or via theme bridge), `patched-upstream` (change landed in the shared package), `local` (lives at the lowest tier per RPS-LAYOUT-01).

---

## 12. Implementation State & Next Steps

**Built so far** (paths + one-line status):

- {{path}} — {{status}}

**Current slice / phase**: {{WHERE_WORK_STOPPED}}

**Per-slice ledger** (facelift runs — append one block per slice):

```
Slice: <name>
Change: <what changed>
Technique: <named technique + exemplar it borrows from>
Critic: <score per axis> — divergence cited: <exemplar>: <specific difference>
Metrics: LCP <n>s · INP <n>ms · CLS <n> · long tasks <n> · contrast <pass/fail>
Status: pass | rework (<reason>)
Save point: <jj change id>
```

**Known issues**: {{ANYTHING_FAILING_OR_DEFERRED}}

**Promotion candidates**:

| Knowledge | Destination | Disposition | Provenance/review |
|---|---|---|---|
| {{system-wide or non-system design rule}} | {{docs/design/system.md or docs/design/<slug>.md}} | {{candidate|promoted|rejected}} | {{work/review/evidence refs}} |

**Next actions** (exact, ordered — a fresh agent starts at #1):

1. {{NEXT_ACTION}}
2. {{NEXT_ACTION}}

---

## 13. File Map

| Artifact | Path |
|---|---|
| Theme stylesheet (`@layer theme`, scaffolded by `web:css`) | {{src/styles/theme.css}} |
| Preview catalog | `../evidence/design/{{DESIGN_SLUG}}/previews/tokens/preview.html` |
| Preview screenshots | `../evidence/design/{{DESIGN_SLUG}}/previews/tokens/screenshot*.webp` |
| This design contract | `./{{DESIGN_SLUG}}.md` |
| Key component directories | {{src/components/ui/, packages/ui/…}} |
| Whole-work state | `../state.md` |
| Design boards and rendered images | `../evidence/design/{{DESIGN_SLUG}}/boards/*` |
| Facelift inventories | `../evidence/design/{{DESIGN_SLUG}}/inventories/facelift-inventory-before.json` / `-after.json` |
| Save points | {{jj change ids, newest last}} |
