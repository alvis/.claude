# Presentation pattern coverage

The eight action examples form a coverage suite for the reusable components,
compositions, and layouts distilled from the approved design reference.
They do not reproduce that source or its branding. Each page uses only the
patterns that fit its discovery job; the suite, not an individual page, is
exhaustive.

Every visible demonstration carries a space-separated
`data-presentation-pattern` marker using the stable IDs below. The complete
template test fails when any catalog pattern is absent or when an example
invents an unknown marker. A marker is evidence only when the associated
element visibly demonstrates the pattern—never add a marker as a placeholder.

Catalog coverage answers “is every reusable pattern demonstrated somewhere?”
It does not answer “is this action example complete?” The validator therefore
also checks action-specific semantic hooks and minimum counts: full option
frames and local reactions, horizon lanes and grounded ideas, ordered interview
steps, source-to-target mappings, prototype variants, risk findings, and
readiness gates. Rendered review remains the final quality check because a
count cannot prove that two compositions are materially different.

Two convention examples sit beside the required eight to demonstrate the guided
conventions — provenance pills, honest trade-offs, author annotation pins, and
the multi-board hub — and their `specimen-scope` theming. They introduce the
pattern IDs `provenance-pill`, `provenance-row`, `tradeoffs-honestly`,
`invented-data-flag`, `annotation-pins`, `browser-frame`, `board-hub`,
`board-index`, and `specimen-scope`. The validator iterates them through a
separate `CONVENTION_EXAMPLES` list, distinct from the required-8, so the
representative stage stays unchanged.

| Action example               | Component and composition coverage                                                                                                                                                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `domain-explainer.html`      | `colors`, `type`, `nav-pattern`, `prompt`, `sequence`, `accordion`, `diagrams`, `flow-strip`, `sidebar-toc`, `flow-terminus`, `tweakable-plan`, `callstack-walkthrough`, `annotation-drawer`, `term-rung`, `teach-me-explainer`, `sticky-reply` |
| `risk-context-report.html`   | `badges`, `callout`, `finding`, `columns`, `decision-box`, `expect-reality`, `blindspot-report`                                                                                                                                                 |
| `ranked-options.html`        | `cards`, `table`, `choice-toggle`, `approach-comparison`, `design-variant-gallery`, `variant-matrix`, `reviewable-option-frame`                                                                                                                 |
| `brainstorm-spectrum.html`   | `assembly`, `segmented`, `brainstorm-spectrum`                                                                                                                                                                                                  |
| `guided-interview.html`      | `confirm`, `stepper`, `avatars`, `guided-question-card`, `quiz-gate`                                                                                                                                                                            |
| `semantics-map.html`         | `annotated`, `schema-box`, `inline-chip`, `unified-diff`, `data-model-card`, `pr-file-review`, `light-code-card`, `semantics-map`                                                                                                               |
| `interactive-prototype.html` | `artifact`, `codeblock`, `annotated`, `scrubber`, `split-reveal`, `tool-palette`, `toggle-switch`, `preset-live-preview`, `prototype-mock`, `live-editor-panel`                                                                                 |
| `readiness-check.html`       | `stats`, `timeline-rail`, `pitch-doc`, `signoff-block`, `status-checklist`, `activity-filter-bar`, `entity-card`                                                                                                                                |
| `specimen-board.html`        | `provenance-pill`, `provenance-row`, `tradeoffs-honestly`, `invented-data-flag`, `annotation-pins`, `browser-frame`, `specimen-scope`                                                                                                           |
| `board-hub.html`             | `board-hub`, `board-index`                                                                                                                                                                                                                      |

Some patterns intentionally overlap. For example, annotated code appears in
both the semantics map and interactive prototype because each demonstrates a
different composition: conformance review versus disposable interaction
testing. The provenance and trade-off patterns are likewise woven into
`ranked-options.html` (its route-health table and option frames) and
`risk-context-report.html` (its findings), so their coverage is robust
independent of the two convention boards; the table records each pattern's
primary owner. Shared shell behavior such as annotation, sidebar navigation,
and the single folded prompt appears on every page even though its catalog
marker is recorded once.

## Coverage rule for future changes

When adding or replacing a page:

1. start with the discovery action's information need, not the catalog order;
2. add, remove, or rearrange components for the clearest task-specific UX;
3. preserve the shared annotation and one-prompt contract;
4. keep every catalog ID represented somewhere across the eight examples;
5. move coverage deliberately and update this table when a pattern changes
   owner; and
6. keep the action-specific structural hooks aligned with the visible
   composition; and
7. run `scripts/test_html_templates.py --stage complete` before presenting the
   examples, then inspect every page at desktop and narrow widths.

The coverage suite is a demonstration library, not a requirement that generated
user artifacts include every pattern. Executors should choose fewer or more
components according to the actual discovery content.
