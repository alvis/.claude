# Canonical web-audit review template

Render audit findings into the shared work review taxonomy. Never create a
standalone audit Markdown report.

## Classification

Classify each finding once by the primary question it answers:

| Review file | Web-audit ownership |
| --- | --- |
| `alignment.md` | Active/durable design or approved-scope divergence |
| `correctness.md` | Broken interaction, navigation, feedback, semantics, or user task |
| `security.md` | Observed trust, permission, unsafe-content, or abuse issue only |
| `quality.md` | Hierarchy, typography, color, spacing, responsive layout, imagery, motion, branding, maintainability |
| `testing.md` | Missing/unreliable page, viewport, state, crop, or manual-review coverage |
| `docs.md` | Inaccurate or missing durable/user-facing design documentation |
| `style.md` | Mechanical token, CSS, or repository-style violation |

Do not duplicate one finding across areas. Design-contract compliance is
`alignment`; semantic failure is `correctness`; a token-style violation without
contract drift is `style`. A visual audit does not imply a security review.

## Detail file header

Each applicable `reviews/<area>.md` begins with:

```markdown
# <Area> review

- Audit target: <URL/project>
- Audit evidence: <relative evidence/web-audit/... path>
- Source report: <report-final.json or report.json + hash>
- Pages/routes: <count/list>
- Viewports: <exact dimensions>
- Coverage: complete|partial|blocked
- Recorded: <ISO-8601>
```

## Finding record

Use one stable heading per CLI rule/finding identity:

```markdown
## <finding-id> — <headline>

- Status: open|fixed|acknowledged|deferred|skipped
- Severity: p0|p1|p2
- Rule: <rule id + rule reference>
- Route/area: <URL and page area>
- Viewport: <label and dimensions>
- Selector: <selector or none>
- Evidence: <crop/context/data paths>
- Confidence: <deterministic or AI score>
- Owner: <owner or unassigned>
- Recheck: <condition>

<Problem and user impact.>

Recommendation: <specific action; no claim it was applied>.

Acceptance check: <observable verification>.
```

New findings begin `open`. Preserve an existing PM/owner disposition when a
repeat audit finds the same stable identity; append new evidence and explicitly
record recurrence or resolution. Non-fixed statuses require rationale, owner,
and recheck condition per the shared contract.

## Context and scoring

Keep the raw overall/category/page scores in JSON evidence. Markdown contains
only concise context and findings needed for engineering action. Preserve exact
scores when they materially prioritize a finding; never convert a score into an
unsupported quality claim.

When an active or durable design exists, cite its exact path and clause in
alignment findings. Otherwise omit design-compliance claims. The valid sources
are the active work design, `docs/design/system.md`, and applicable
`docs/design/<slug>.md`.

## PM reconciliation payload

Return, but do not write as a worker:

```yaml
review_reconciliation:
  source: <relative report path + hash>
  coverage: complete|partial|blocked
  counts:
    alignment: 0
    correctness: 0
    security: 0
    quality: 0
    testing: 0
    docs: 0
    style: 0
  by_status:
    open: 0
    fixed: 0
    acknowledged: 0
    deferred: 0
    skipped: 0
  detail_files: [<absolute paths>]
```

The PM validates these counts against details and then reconciles `review.md`.
