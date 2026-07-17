# Shared HTML components

The component system is a small declarative contract implemented by
`assets/html/discovery.css` and `assets/html/discovery.js`. It makes temporary
discovery pages consistent enough to learn quickly without turning the examples
into rigid templates.

The styling strategy is Tailwind CSS plus shared CSS variables. Load the
temporary browser runtime, map `--ui-*` values through `@theme inline`, and use
the resulting utilities for composition. Keep palette, type, shadow, and surface
values centralized in `discovery.css`; action examples must not create competing
theme tokens.

Use `backdrop-blur-lg` through `backdrop-blur-2xl` only on elevated controls,
decision surfaces, annotation UI, and the generated-prompt host. Pair the blur
with translucent `--ui-glass*` surfaces and inset highlights. Do not add opaque
card borders around glass, and do not turn every prose section into a glass
panel.

## Mandatory page shell

Use one root with a stable ID, action, and goal:

```html
<main
  data-discovery-page
  data-page-id="release-mechanics-v1"
  data-discovery-action="domain-explainer"
  data-discovery-goal="Choose a safe migration approach"
>
  <!-- adaptable page content -->
</main>
```

The runtime uses `essential.discover.v1:<page-id>` for local state. Generated
temporary previews should include a run-specific page ID so separate previews
cannot recover one another's answers accidentally.

Start from `templates/html/page.html`, then inspect the approved
`examples/html/domain-explainer.html`. The top bar contains no search control:
each artifact is one static page. On wide viewports, place navigation on the
right while keeping the reading column optically centered; move navigation
below the content on narrow viewports. The navigation owns live decision and
note groups: each label and count share a header row, and every current item is
listed beneath it. Untouched recommendations appear immediately as suggested
items; touched answers replace their suggested state. Do not hard-code empty
messages or collapse multiple items into a single summary.

## Annotatable section

Wrap every user-facing content region in a section with a unique identifier:

```html
<section data-discovery-section data-section-id="migration-sequence">
  <p class="discovery-eyebrow">Mechanism</p>
  <h2>Four changes, one reversible sequence</h2>
  <p>Section content remains readable before JavaScript adds annotation UI.</p>
</section>
```

The shared runtime inserts one **Add note** control and an annotation summary in
each section. It reuses one dialog/editor for the whole page. Do not hand-code
separate editors, and never insert annotation text with `innerHTML`.

## Decision question

Questions need stable IDs and human-readable labels. Recommended defaults may
be checked initially, but are unresolved until touched:

```html
<fieldset
  data-discovery-question
  data-question-id="rollout-speed"
  data-question-label="Preferred rollout speed"
>
  <legend>How quickly should traffic move?</legend>
  <label>
    <input
      type="radio"
      name="rollout-speed"
      value="Measured stages"
      data-recommended="true"
      checked
    />
    Measured stages <span>Recommended</span>
  </label>
  <label>
    <input type="radio" name="rollout-speed" value="One coordinated cutover" />
    One coordinated cutover
  </label>
</fieldset>
```

Use radios for one choice, checkboxes for independent choices, selects for
compact known sets, and text inputs only when recognition-based choices are not
enough. The runtime records `touched` independently from the current value.

Not every response is a decision. An explainer may instead offer optional
follow-up actions such as “show another example” or “go deeper on the failure
path.” Mark those question containers explicitly:

```html
<fieldset
  data-discovery-question
  data-question-id="explainer-follow-ups"
  data-question-label="Explain next"
  data-response-kind="follow-up"
>
  <legend>What should the coder explain next?</legend>
  <label
    ><input type="checkbox" value="Show a worked rollback" />Rollback</label
  >
</fieldset>
```

Omit decision questions entirely when the action does not require a choice.
The sidebar label and generated prompt adapt to decision-only, follow-up-only,
and mixed pages. An untouched optional follow-up is never treated as a request.

## Direction frame and trait reactions

When the user must choose a product, technical, visual, or interaction
direction, compare complete alternatives under one shared scenario. The hooks
below describe the decision semantics; they do not prescribe card styling or a
single composition:

```html
<main
  data-discovery-page
  data-page-id="review-queue-directions-v1"
  data-discovery-action="ranked-options"
  data-discovery-goal="Choose a direction for the review queue"
  data-scenario-id="review-queue-at-peak-load-v1"
>
  <section
    data-discovery-section
    data-section-id="dense-console"
    data-option-frame
    data-scenario-id="review-queue-at-peak-load-v1"
    data-direction-id="dense-console"
    data-direction-composition="operations-console"
  >
    <div data-direction-artifact>
      <!-- Render the representative interface, flow, model, or mechanism. -->
      <div data-direction-trait="metric-strip">Queue health at a glance</div>
      <div data-direction-trait="inline-triage">Resolve work in place</div>
    </div>
    <fieldset
      data-discovery-question
      data-question-id="dense-console-reaction"
      data-question-label="Dense console reaction"
      data-option-reaction
    >
      <legend>What should survive from this direction?</legend>
      <label>
        <input
          type="radio"
          name="dense-console-reaction"
          value="Keep the whole direction"
          data-reaction-kind="keep"
        />
        Keep the whole direction
      </label>
      <label>
        <input
          type="radio"
          name="dense-console-reaction"
          value="Steal the metric strip"
          data-reaction-kind="steal"
        />
        Steal the metric strip
      </label>
      <label>
        <input
          type="radio"
          name="dense-console-reaction"
          value="Reject this direction"
          data-reaction-kind="reject"
        />
        Reject this direction
      </label>
    </fieldset>
  </section>

  <!-- Render two to four more materially different direction frames. -->

  <fieldset
    data-discovery-question
    data-question-id="final-direction"
    data-question-label="Final direction"
    data-final-selection
  >
    <legend>Which direction should anchor the next iteration?</legend>
    <label>
      <input
        type="radio"
        name="final-direction"
        value="Dense console"
        data-direction-choice="dense-console"
      />
      Dense console
    </label>
  </fieldset>
</main>
```

Use three to five frames. Repeat the root `data-scenario-id` on every frame so
the content, inputs, operating state, and viewport remain controlled. Give each
frame a unique `data-direction-id` and `data-direction-composition`, one
substantive `data-direction-artifact`, and at least two visible named
`data-direction-trait` elements. Every frame needs local keep, steal, and reject
reactions; every stable direction ID needs exactly one matching
`data-direction-choice` in the final selection.

`data-direction-artifact` is also the shared responsive container. Compose its
interior with `discovery-direction-stats`, `discovery-direction-flow`, or
`discovery-direction-columns` plus one of
`discovery-direction-columns-two`, `discovery-direction-columns-three`,
`discovery-direction-columns-main-aside`, or
`discovery-direction-columns-aside-main`. These components respond to the artifact's available
width rather than the browser viewport, so a wide browser with a title rail and
sidebar cannot force a five-column layout into a narrow frame. Keep every grid
child at `min-width: 0`; long code, metrics, and labels must wrap inside the
artifact border.

For visual or interaction directions, render the same representative content
and state while changing hierarchy, density, controls, navigation, or
interaction model. For technical directions, hold inputs and constraints steady
while changing mechanism, ownership, or failure behavior. A renamed clone, a
moodboard swatch, or prose-only card is not a direction frame. The executor
should add or remove tables, flows, prototypes, diagrams, and controls to make
each direction honestly inspectable.

## Prompt host

Every page contains exactly one host and one prompt copy control:

```html
<section data-discovery-section data-section-id="generated-brief">
  <h2>Your reply to the coder</h2>
  <textarea data-discovery-prompt-host readonly></textarea>
  <button type="button" data-copy-generated-prompt>
    Copy prompt for LLM coder
  </button>
</section>
```

The runtime regenerates one Markdown prompt from the discovery goal, touched
answers, accepted recommendations, overrides, unresolved suggestions, and all
section annotations. It updates on every relevant `input` or `change` event.
There is no prompt per card, section, answer, or note.

The runtime moves this section into the navigation's folded prompt target when
JavaScript runs. Keep it in the main document in source so the page remains
readable without JavaScript. The fold is collapsed initially, and its textarea
grows to its content rather than creating a nested scrollbar.

## Optional presentation components

Use only what improves the page:

- context rail for a short mental model or glossary;
- sequence or flow for ordering and causality;
- comparison table for repeated fields;
- recommendation marker that remains visibly provisional;
- evidence or caveat strip for provenance and limits;
- status or readiness indicator for a single verdict;
- code/sample block with a separately labelled **Copy code** action;
- sticky table of contents for long pages;
- clear-state action near the generated prompt.

The executor may replace any optional component, including every component in
an example. Preserve semantic elements, keyboard reachability, visible focus,
44px touch targets, reduced-motion behavior, light/dark readability, and the
mandatory annotation/single-prompt contract.

## Catalog coverage markers

The checked-in examples also serve as an exhaustive demonstration suite. Mark
the element that visibly implements a catalog pattern with
`data-presentation-pattern="pattern-id"`; use a space-separated value when one
composition legitimately demonstrates several patterns. The allowed IDs and
their action owners are listed in [coverage](coverage.md).

Markers are test evidence, not styling hooks. Never mark an absent component or
force every component into a generated user artifact. The complete validator
checks suite coverage while each executor remains free to choose the smallest
useful task-specific composition.

## Action-structure hooks

Examples also expose semantic `data-*` hooks for the structural validator.
These hooks name the job performed by an element—such as
`data-option-frame`, `data-idea-card`, `data-interview-step`, or
`data-readiness-gate`—and are never styling hooks. Their required counts live
in `scripts/test_html_templates.py` beside the executable check.

A structural hook is valid only on a substantive visible element. For example,
an option frame contains a credible artifact and its local reaction control; an
idea card contains a grounded intervention rather than a title placeholder; a
semantics mapping includes source evidence, target behavior, and a consequence.
Meeting a count with empty wrappers is a failed review even when the mechanical
validator passes.
