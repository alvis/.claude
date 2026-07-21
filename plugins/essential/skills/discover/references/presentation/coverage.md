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

Three convention examples sit beside the required eight to demonstrate the
guided conventions — provenance pills, honest trade-offs, author annotation
pins, and the multi-board hub — and their `specimen-scope` theming. They
introduce the pattern IDs `provenance-pill`, `provenance-row`,
`tradeoffs-honestly`, `invented-data-flag`, `annotation-pins`, `browser-frame`,
`board-hub`, `board-index`, and `specimen-scope`. `architecture-board.html` is
the third convention board: it demonstrates the architecture-and-provenance
patterns `node-edge-diagram`, `diagram-detail`, `prompt-echo`, and
`source-manifest` over a shared node/edge decomposition, and reuses the existing
convention markers (`annotation-pins`, `provenance-pill`, `provenance-row`,
`tradeoffs-honestly`, `invented-data-flag`, `specimen-scope`, plus `schema-box`,
`flow-strip`, and `diagrams`). The validator iterates the convention boards
through a separate `CONVENTION_EXAMPLES` list, distinct from the required-8, so
the representative stage stays unchanged.

| Action example               | Component and composition coverage                                                                                                                                                                                                                                                                                                                  |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `domain-explainer.html`      | `colors`, `type`, `nav-pattern`, `prompt`, `sequence`, `accordion`, `diagrams`, `flow-strip`, `sidebar-toc`, `flow-terminus`, `tweakable-plan`, `callstack-walkthrough`, `annotation-drawer`, `term-rung`, `teach-me-explainer`, `sticky-reply`, `source-ref-chip`, `faq-block`, `glossary-sync`, `live-sim`, `accordion-exclusive`, `anchor-flash` |
| `risk-context-report.html`   | `badges`, `callout`, `finding`, `columns`, `decision-box`, `expect-reality`, `blindspot-report`, `risk-matrix`, `owner-routing`, `tldr-block`                                                                                                                                                                                                       |
| `ranked-options.html`        | `cards`, `table`, `choice-toggle`, `approach-comparison`, `design-variant-gallery`, `variant-matrix`, `reviewable-option-frame`, `verdict-table`, `variant-rationale`, `scope-cuts`                                                                                                                                                                 |
| `brainstorm-spectrum.html`   | `assembly`, `segmented`, `brainstorm-spectrum`, `spectrum-minimap`, `reaction-chips`                                                                                                                                                                                                                                                                |
| `guided-interview.html`      | `confirm`, `stepper`, `avatars`, `guided-question-card`, `quiz-gate`, `wizard-steps`, `nl-reply`                                                                                                                                                                                                                                                    |
| `semantics-map.html`         | `annotated`, `schema-box`, `inline-chip`, `unified-diff`, `data-model-card`, `pr-file-review`, `light-code-card`, `semantics-map`, `syntax-tokens`, `rich-diff`, `code-pair-highlight`, `code-tabs`                                                                                                                                                 |
| `interactive-prototype.html` | `artifact`, `codeblock`, `annotated`, `scrubber`, `split-reveal`, `tool-palette`, `toggle-switch`, `preset-live-preview`, `prototype-mock`, `live-editor-panel`, `drag-probe`, `motion-specimen`, `demo-loop`, `specimen-code-map`                                                                                                                  |
| `readiness-check.html`       | `stats`, `timeline-rail`, `pitch-doc`, `signoff-block`, `status-checklist`, `activity-filter-bar`, `entity-card`, `milestone-timeline`, `inline-chart`, `filter-chips`                                                                                                                                                                              |
| `specimen-board.html`        | `provenance-pill`, `provenance-row`, `tradeoffs-honestly`, `invented-data-flag`, `annotation-pins`, `browser-frame`, `specimen-scope`, `global-rig`, `artboard-frame`, `theme-direction-gallery`, `mock-frame`                                                                                                                                      |
| `board-hub.html`             | `board-hub`, `board-index`                                                                                                                                                                                                                                                                                                                          |
| `architecture-board.html`    | `node-edge-diagram`, `diagram-detail`, `prompt-echo`, `source-manifest`                                                                                                                                                                                                                                                                             |

Some patterns intentionally overlap. For example, annotated code appears in
both the semantics map and interactive prototype because each demonstrates a
different composition: conformance review versus disposable interaction
testing. The provenance and trade-off patterns are likewise woven into
`ranked-options.html` (its route-health table and option frames) and
`risk-context-report.html` (its findings), so their coverage is robust
independent of the convention boards; the table records each pattern's
primary owner. Shared shell behavior such as annotation, sidebar navigation,
and the single folded prompt appears on every page even though its catalog
marker is recorded once.

Several of the new patterns overlap similarly, and the table records the primary
owner while the reinforcement lives elsewhere. `syntax-tokens` are the owner
demonstration on `semantics-map.html` but recur inside its `rich-diff` rows and
across its lease/replay/adaptation mappings. The `discovery-source-ref` chip
owned by `domain-explainer.html` as `source-ref-chip` reappears as the path in
each `source-manifest` row on `architecture-board.html`. Provenance pills are
reused inside `faq-block` answers, `source-manifest` rows, and `risk-matrix`
mitigations. The `spectrum-minimap` two-way sync mirrors the same
`reaction-chips` state it lives beside, and `glossary-sync` terms thread through
several `domain-explainer.html` sections, not just the glossary itself.

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
