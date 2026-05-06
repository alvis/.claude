# Phase 4 -- Output Rendering (Detail)

Loaded by `SKILL.md` Step 4. Renders the final audit output (markdown + JSON) from `report-final.json`.

**Step Configuration**:
- **Purpose**: Render the final audit output (markdown + JSON) from `report-final.json`
- **Input**: `<out>/report-final.json`
- **Output**: Markdown output in conversation, JSON summary code block
- **Parallel Execution**: No

## 4.1 Markdown Output

Output to conversation following `references/review-template.md` (rendering language follows `constitution/standards/design/write.md`):

**Section 1 -- Context**:
- URL(s) audited
- Viewports tested (Desktop 1440x900, Tablet 768x1024, Mobile 390x844)
- Timestamp
- Audit scope (full / quick / category-specific)
- Input mode (URL / source code)
- Component types detected

**Section 2 -- Overall Score**:
- Score 0-100 with risk level badge (CRITICAL / HIGH / MEDIUM / LOW)
- Quality level label (per review-template.md scale)

**Section 3 -- Per-Category Table**:

| Category | Score | Issues | Top Severity |
|----------|-------|--------|-------------|
| ... | ... | ... | ... |

**Section 4 -- Findings by Area**:

Area summary table:

| Area | Score | Issues | Screenshot |
|------|-------|--------|------------|
| navbar | 0 | 0 | [screenshot](http://localhost:18977/area-navbar.png) |
| ... | ... | ... | ... |

Per-area detail block:
- **Screenshot link**: `http://localhost:18977/area-{name}.png`
- **Grounding summary**: AI verdicts from Phase 3 that apply to this area
- **Findings list**: All findings that belong to this area
- **Area score**: Read from `report-final.json` (computed by the CLI)

**Section 5 -- Findings by Priority** (P0, then P1, then P2):

Each finding includes:
- Rule ID and title
- Severity and classification (gulf type, error type)
- Description of the issue
- Evidence: DOM values, computed styles, crop image path, `ai_verdict` (if any)
- Selector(s) affected
- Viewport(s) where observed
- **Recommendation**:
  - **What to change**: Actionable description of the fix
  - **Code suggestion**: CSS/HTML inline code snippet
  - **Rule reference**: Path to rule file + clause
- Effort x Impact classification

**Section 6 -- Manual Review Entries**:
- AI verdicts from Phase 3 with rationale and confidence

**Section 7 -- Quick Wins**:
- Top high-impact, low-effort changes

**Section 8 -- Verification Checklist**:
- Per review-template.md checklist items

**Section 9 -- Site-Level Findings** (always included, even for single-page audits):

- **Orphan routes** (present in source, not linked): list from `report.orphan_routes`
- **Recurring elements** (audited once, scope: site-wide): e.g., hamburger menu, modal X, dropdown Y -- from `report.recurring_elements`
- **Cross-origin excluded (social)**: list from `report.cross_origin_excluded_social`
- **Cross-origin excluded (user-declined)**: list captured during Phase 3.2
- **Per-page scores** (sorted worst --> best)
- **Worst 3 pages** (for triage): top three lowest-scoring pages with their scores and primary issues

**DESIGN.md Compliance** (only when DESIGN.md detected):
- Token compliance score
- Deviation table

## 4.2 JSON Summary

Append as a fenced code block:

```json
{
  "contractVersion": "3.0",
  "target": {
    "urls": ["https://example.com"],
    "mode": "url|source"
  },
  "summary": {
    "overallScore": 0,
    "risk": "CRITICAL|HIGH|MEDIUM|LOW",
    "totalIssues": 0,
    "bySeverity": { "p0": 0, "p1": 0, "p2": 0 }
  },
  "pages": [
    {
      "url": "https://example.com",
      "viewports": [
        {
          "label": "Desktop 1440x900",
          "score": 0,
          "issues": [
            {
              "ruleId": "",
              "severity": "",
              "recommendation": {
                "action": "",
                "codeSuggestion": "",
                "ruleRef": ""
              }
            }
          ]
        },
        {
          "label": "Tablet 768x1024",
          "score": 0,
          "issues": []
        },
        {
          "label": "Mobile 390x844",
          "score": 0,
          "issues": []
        }
      ],
      "areas": [
        {
          "name": "navbar",
          "score": 0,
          "issueCount": 0,
          "screenshotUrl": "http://localhost:18977/area-navbar.png",
          "groundingSummary": "",
          "findings": []
        }
      ]
    }
  ],
  "siteLevel": {
    "orphanRoutes": [],
    "recurringElements": [],
    "crossOriginExcludedSocial": [],
    "crossOriginExcludedUserDeclined": [],
    "perPageScores": [],
    "worstPages": []
  }
}
```

## 4.3 Batch Mode (Multiple URLs)

When auditing multiple pages (via `--all-pages` or explicit page list):
- Per-page sections with individual scores
- Site-level aggregation is already covered by Section 9 (Site-Level Findings)
- Cross-page consistency findings are surfaced via `recurring_elements` in `report-final.json`
