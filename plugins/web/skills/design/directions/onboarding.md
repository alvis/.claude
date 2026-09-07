# Onboarding

Use for first-use setup, guided configuration, and reaching an initial useful outcome. A marketing signup CTA uses landing-page guidance until the request includes the setup flow.

## Establish the first useful outcome
Identify the user's intended result, genuinely required inputs, optional preferences, dependencies, existing validation rules, persistence, and the point at which setup can safely be considered complete. Read existing product behavior before adding steps. Ask when a missing rule changes eligibility, saved data, or completion; never invent account creation or service success.

## Design the shortest sufficient path
- Organize steps around meaningful decisions, not one input per screen. Explain why required information is needed; postpone nonessential work until after value is available.
- Use honest progress with named stages. If branching changes the remaining path, avoid a misleading fixed percentage.
- Provide back navigation and retain entered values. Make optional steps visibly skippable; skipping clears or bypasses their validation without secretly submitting partially entered data.
- Use persistent labels and specific inline errors tied to fields. On failed continuation, focus the first invalid input or an appropriate error summary; preserve valid entries.
- Explain consequences before irreversible actions under the existing product contract. Show loading, retry, and duplicate-submission prevention only where an asynchronous operation actually exists.
- Keep controls predictable across steps; distinguish back, skip, continue, and final completion. On each transition, move focus to the new heading or relevant error.
- Completion states what actually happened and offers the next useful action. A local demonstration explicitly states no account or workspace was created and supports restarting.
- Mobile retains progress, input context, and primary controls without hiding content behind fixed bars. Avoid celebratory motion that delays the next task.

## Handoff and acceptance
Return the outcome, step/dependency map, required/optional distinction, validation and retention rules, navigation, and truthful completion behavior through the parent contract.

Exercise invalid and valid continuation, back with retained values, skipping incomplete optional input, keyboard-only completion, restart, and narrow-screen behavior. For real persistence, use the product's existing failure/resume contract rather than assuming refresh retains data.

## Example
Optionally open `examples/onboarding/index.html` and `examples/onboarding/preview.png` from this skill root for a fictional setup flow. Its in-memory state and completion message are demonstration boundaries, not production persistence guidance.

