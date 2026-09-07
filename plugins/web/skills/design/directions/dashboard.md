# Dashboard

Use for analytical overviews, operational workspaces, and administrative views where users interpret status or act on records. Backend reporting, metric calculation, and isolated chart analysis do not activate this design workflow on their own.

## Identify the decision
Establish user role, recurring questions, decisions, actions, data sources, metric definitions, units, time range, comparison baseline, freshness, and permissions from supplied contracts. Ask when a missing definition changes interpretation; never silently invent a denominator, aggregation, trend, or permission. Demonstration data must be identified as sample data.

Classify the surface: presentation emphasizes status; exploration supports comparisons and drill-down; operations prioritize queues, exceptions, and record actions. Combine only where one task benefits from the connection.

## Organize information and actions
- Rank information by decision importance. A metric earns space by answering a question; do not fill a fixed number of KPI cards.
- Show units, period, comparison, and update context where needed to interpret values. Missing and stale values are not zero; a positive change is not automatically good.
- Choose positions/lengths for quantitative comparisons, lines for ordered time, and tables for exact values or record operations. Label axes and units; avoid decorative charts or scales that misrepresent differences.
- Keep series colors and comparison semantics consistent. Pair status color with text; provide a readable data equivalent for visual charts.
- Specify whether a filter affects the whole view or one region. Show active filters and reset; keep related metrics, charts, and tables synchronized within that scope.
- Drill-down must preserve context and offer a clear return. Specify sort, selection, pagination, and bulk-action scope only when the product requires them.
- Distinguish loading, no records, no filter matches, partial data, stale data, and errors. Explain recovery and avoid leaving an old value looking freshly verified.
- Keep operational actions discoverable and report their result. Respect the existing permission and confirmation contract; frontend controls are not an authorization boundary.
- Reorder by task priority on mobile. Keep essential comparisons and row identity; use a labeled scrollable region for genuinely wide data rather than shrinking text.

## Handoff and acceptance
Return a question-to-view map, metric/display definitions, filter scope, chart/table rationale, action behavior, and state inventory in the parent contract.

Exercise combined filters and reset, drill-down/return, zero versus missing/stale data, failed or empty views, keyboard operation, chart alternatives, and narrow screens. Verify displayed totals against the supplied sample fixture without expanding into data-pipeline implementation.

## Sources and example
[Carbon's dashboard guidance](https://carbondesignsystem.com/data-visualization/dashboards/) supplies presentation/exploration distinctions and consistent comparisons. [NN/g's quantitative-perception guidance](https://www.nngroup.com/articles/dashboards-preattentive/) supports position and length comparisons; these are established usability sources, not 2026 award claims.

Optionally open `examples/dashboard/index.html` and `examples/dashboard/preview.png` from this skill root for a sample analytical and operational workspace.

