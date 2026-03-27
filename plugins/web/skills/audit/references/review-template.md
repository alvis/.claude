# Audit Report Template

## Context

- **Surface**: (web/app) + page type (list/detail/form/dashboard/settings/modal)
- **Primary user task**:
- **Primary CTA**:
- **Component type detected**: (full page / form / modal / navigation / card / dashboard / component)
- **Audit scope**: Full (12 categories) / Quick (5 categories)
- **Input type**: URL (live browser) / Screenshot / Code / Figma
- **Confidence**: High (live browser or code) / Medium (screenshot) / Low (description only)

## Scores

**Overall: XX/100**

| Quality Level | Score Range |
|---|---|
| Bootstrap Template | 40-50 |
| Customized Framework | 60-70 |
| Professional Design | 70-80 |
| Design Excellence | 80-90 |
| Award-Worthy | 90-100 |

### Per-Category Scores (1-10)

| Category | Score | Notes |
|---|---|---|
| Visual Hierarchy & Layout | X/10 | |
| Typography | X/10 | |
| Color & Contrast | X/10 | |
| Spacing & Grid | X/10 | |
| Consistency & Tokens | X/10 | |
| Accessibility | X/10 | |
| States & Feedback | X/10 | |
| Navigation & IA | X/10 | |
| Content & Microcopy | X/10 | |
| Responsiveness | X/10 | |
| Imagery, Icons & Motion | X/10 | |
| Branding & Modern Standards | X/10 | |

### DESIGN.md Compliance

> Only included when a DESIGN.md is detected in the project.

| Category | Tokens Defined | Tokens Applied | Compliance | Deviations |
|----------|---------------|----------------|------------|------------|
| Colors | — | — | —% | — |
| Typography | — | — | —% | — |
| Spacing | — | — | —% | — |
| Radius | — | — | —% | — |
| Shadows | — | — | —% | — |
| Components | — | — | —% | — |
| **Overall** | — | — | **—%** | — |

#### Token Deviations

| Component | Expected Token | Actual Value | Severity |
|-----------|---------------|--------------|----------|
| — | — | — | — |

## Findings (Prioritized)

### P0 -- Blocker

- **Problem**:
  - Evidence:
  - Diagnosis: execution gulf / evaluation gulf | slip / mistake
  - Impact: (what breaks for users)
  - Fix: (specific, implementable -- include file path if code)
  - Acceptance check: (how to verify the fix)

### P1 -- Important

- **Problem**:
  - Evidence:
  - Diagnosis: execution gulf / evaluation gulf | slip / mistake
  - Fix:
  - Acceptance check:

### P2 -- Polish

- **Problem**:
  - Fix:

## Quick Wins

Top 3 small changes that noticeably improve clarity or polish.

## Competitive Comparison (if competitors provided)

| Aspect | This Product | Competitor A | Competitor B |
|---|---|---|---|
| Visual Polish | X/10 | X/10 | X/10 |
| Typography | X/10 | X/10 | X/10 |
| Color Usage | X/10 | X/10 | X/10 |
| Consistency | X/10 | X/10 | X/10 |
| Modernity | X/10 | X/10 | X/10 |

## Verification Checklist

- [ ] Task clarity: primary CTA obvious and singular
- [ ] IA: groups match user mental model
- [ ] Feedback: loading/empty/error/success states present
- [ ] Consistency: components and wording stable across screens
- [ ] Affordance: clickable elements look clickable
- [ ] Errors: prevention + recovery + actionable messages
- [ ] Cognitive load: defaults and progressive disclosure
- [ ] CRAP: hierarchy, alignment, spacing, grouping intentional
- [ ] Modern minimal: restrained color, spacious layout, minimal copy
- [ ] Icons: no emoji; consistent set; labels where ambiguous
- [ ] Accessibility: keyboard nav, focus visible, ARIA labels, contrast AA
- [ ] Responsive: mobile touch targets, no horizontal scroll, content reflows
- [ ] DESIGN.md tokens match implementation values
- [ ] No hardcoded values where design tokens are defined
