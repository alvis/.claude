# Presenting discovery results

Use an interactive HTML review surface when visual relationships, comparison,
or in-context feedback will reduce ambiguity more than prose alone. HTML is not
the default and is never evidence by itself. The evidence ledger remains the
source of truth after answers and annotations are transferred back.

## Choose a directional action

| Discovery mode | Directional action    | Best fit                                                                |
| -------------- | --------------------- | ----------------------------------------------------------------------- |
| `blindspots`   | risk/context report   | Interacting risks, constraints, actors, or failure surfaces             |
| `blindspots`   | domain explainer      | An unfamiliar mechanism must become understandable before deciding      |
| `options`      | ranked options        | Viable approaches or experiential directions need in-context comparison |
| `options`      | brainstorm spectrum   | The user should react to a deliberately broad solution space            |
| `interview`    | guided interview      | Several coupled questions need visible supporting context               |
| `reference`    | semantics map         | Terms, relationships, or observable behavior must map into the target   |
| `prototype`    | interactive prototype | A disposable interaction is the cheapest useful probe                   |
| `readiness`    | readiness check       | Evidence, assumptions, blockers, and the next owner need one view       |

These actions are directions, not page schemas. Add, remove, reorder, combine,
or redesign components to deliver the clearest experience for the actual
information. Never preserve a component merely because an example contains it.
The shared annotation and single-prompt behavior is mandatory; visual recipes
and component counts are not.

Each action must nevertheless feel complete for its own job. Build from one
credible scenario and enough realistic data to expose the relevant trade-offs.
An action page is not complete when it merely places the catalog markers on a
few generic cards. Its core composition must let the user perform the action:
compare full directions, manipulate a prototype, traverse a mechanism, react
across a spectrum, answer an ordered interview, inspect source-to-target
semantics, evaluate risks, or reach a readiness verdict.

The approved [domain explainer](presentation/actions/domain-explainer.md) and
its [golden HTML example](../examples/html/domain-explainer.html) define the
shared visual hierarchy, responsive shell, annotation flow, and folded
single-prompt experience. Every action example follows that contract while
changing its content density and optional components to fit the action.

Together, the eight examples must cover the complete reusable pattern catalog.
Use the [presentation coverage map](presentation/coverage.md) to see which
action owns each demonstration. This is suite-level coverage: generated pages
still select only the components that improve their task-specific UX.
The complete validator checks both catalog coverage and minimum semantic
structure for every action; neither check substitutes for rendered review.

## Shared interaction contract

Follow [components](presentation/components.md) for the declarative HTML hooks.
Every user-facing section must be annotatable. Answers, decisions, optional
follow-up requests, overrides, and annotations regenerate one Markdown prompt
immediately. The page displays that prompt in one host and provides exactly one
control labelled **Copy prompt for LLM coder**. Do not add per-section prompt
copy actions. A separately labelled copy control for non-prompt material, such
as code, is allowed only when it cannot be mistaken for the generated reply.

Untouched defaults are suggestions, not user decisions. Record whether a
control was touched. Show suggested responses in the sidebar immediately; do
not fill empty lists with static explanatory strings. In the generated prompt,
distinguish confirmed recommendations, explicit overrides, optional or selected
follow-ups, unresolved suggestions, and free-form notes. User input always
outranks a recommendation. Do not manufacture a decision for an explanatory
page; it may contain only follow-up actions.

Use safe text APIs for user content. The page must remain legible when
JavaScript fails, storage is unavailable, or the clipboard API is blocked.
Persist only page answers and annotations in browser-local storage; fall back
to in-memory state without preventing review.

## Shared theme contract

Use Tailwind CSS utilities together with the shared `--ui-*` CSS variables.
The variables in `assets/html/discovery.css` are the only theme-value source;
the page's `@theme inline` block maps them into Tailwind names such as
`bg-canvas`, `text-ink`, and `bg-accent-soft`. Do not redefine color values in
an action page. Compose page-specific layout and states with utilities, then use
the shared component classes for behavior-heavy patterns that would be noisy or
fragile to repeat.

The specimen exception. House `--ui-*` stays the default for page chrome, but
an embedded specimen or mockup should read as the subject product, not the tool.
Show its real palette in a scoped `[data-specimen]` container that re-points the
`--ui-*` tokens locally — the one place a hex literal may appear in an action
page — or expose parallel `--spec-*` tokens when the specimen must show house
and brand side by side. Re-point only the tokens the specimen needs; its
interior reuses the house component classes and renders brand-tinted. A
page-level re-tint outside `[data-specimen]` is allowed only through token
indirection (`--ui-accent: var(--ui-insight)`), never a hex literal. The tool's
annotation pin layer and browser-frame chrome stay on house tokens, outside the
specimen re-point, because they are the tool's layer rather than the product's.

These pages are temporary development artifacts, so the no-build Tailwind
browser runtime is appropriate. The shared stylesheet must still provide a
readable base when that runtime cannot load. Default to the light, daylight
theme; use an explicit `data-theme="dark"` for dark review rather than following
the host system automatically.

The shared visual direction is an empowering developer workspace with liquid
glass depth and the warm editorial grammar of the approved source reference:
a natural canvas, translucent layered surfaces, crisp code typography,
terracotta interaction energy, and restrained olive for insight. Glass supports
hierarchy rather than decorating every region; prose sections can remain open
on the canvas. Preserve readable fallback colors whenever `backdrop-filter` is
unavailable.

## Guided conventions and extensibility

Four optional conventions raise the honesty and depth of a review surface when
the content warrants them. Reach for [components](presentation/components.md)
for the exact hooks:

- provenance pills wire each claim's status from the evidence ledger, so the
  reader sees what is observed, inferred, assumed, decided, approved, or open;
- a "Trade-offs, honestly" block states the wins, costs, and failure modes of a
  direction, with an invented-data flag for illustrative filler;
- author annotation pins over a browser-frame specimen teach a mockup in place,
  distinct from the user's own Add-note mechanism;
- a multi-board hub links sibling boards by session-relative href.

The foundation is fixed: the page shell, annotatable sections, the single-prompt
contract, the `--ui-*`/`@theme inline` theme, and these provenance, trade-off,
pin, and board conventions. On top of that fixed floor an executor may propose
new structural cards, provided each honors the theme, interaction (annotatable
plus one live prompt), provenance, and accessibility conventions. Guided, not
rigid.

## Temporary artifact lifecycle

Always save generated, user-specific HTML before presenting it. Use the
platform temp root through Python's `tempfile.mkdtemp` to open one session
workspace, with sanitized slugs and a unique suffix:

```python
workspace_dir = tempfile.mkdtemp(
    prefix=f"essential-discover-{repo_slug}-session-"
)
```

One workspace holds every board HTML file produced during the session, so
boards can cross-link with session-relative hrefs (`./sibling.html`). This
resolves through the operating system (`$TMPDIR` on macOS, the configured temp
root such as `/tmp` on Linux, and `%TEMP%` on Windows) without a shared
filename collision. Write each board's HTML and optional captures inside that
workspace directory, and link boards to one another with relative hrefs. Link
every page to the canonical plugin CSS and JavaScript; temporary pages are
intentionally nonportable and may break after the plugin moves. Artifacts stay
ephemeral — durable, bookmarkable, and cross-linked only within the session,
never a permanent deliverable.

Present in this order:

1. the LLM coder's built-in local browser or HTML viewer;
2. a cloud artifact viewer/store only when a suitable tool exists, the content
   is safe to externalize, and the service can render the linked dependencies;
3. a local browser such as Chrome.

If the cloud viewer cannot load the common assets, skip it. Never externalize
sensitive discovery content merely to satisfy the preference order. After the
user's decisions and annotations are captured in the one generated prompt and
transferred to the ledger, discard the whole session workspace.

## Golden-example confirmation

The domain-explainer example was explicitly approved after desktop and narrow
review. Treat it as the golden baseline for new action pages. Preserve its
right-side desktop navigation, bottom narrow navigation, shared button
language, section annotation dialog, live decision/note lists, and one folded
generated prompt. The action recipe remains directional: change, remove, or
add content components whenever that improves the task-specific UX.
