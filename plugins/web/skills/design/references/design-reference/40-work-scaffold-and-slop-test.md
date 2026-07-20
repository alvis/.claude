# Work scaffold and slop test

## Work design scaffold

For multi-page or production UIs, create the active work's
`design/<design-slug>.md` before the first component. The 13-section structure,
two-tier token tables, component specifications, decision log, evidence map,
and “Motion, Transitions & Separators” specification live in
`../design.template.md`. Sections 10–13 are the domain handoff contract; whole-work
context and planning stay in `state.md`.

For a single component or quick prototype, use a lightweight design child with
the shared metadata, three-line visual thesis, decisions, evidence paths,
implementation mapping, and next action. Evidence still belongs under
`evidence/design/<design-slug>/`.

## AI Slop Test

Would a stranger glancing at the first viewport immediately say "an AI made this"? If yes, the design direction was not committed enough. The usual culprits:

1. Reflex font (Inter, Roboto, Poppins, or system-ui at display sizes)
2. Default purple/blue accent with no brand connection
3. Centered hero with generic card grid beneath
4. Uniform card sizing with identical shadows and padding

Fix the typography, the color system, or the layout until the answer flips. If more than one culprit applies, fix all of them.

---

*Adapted from [Waza](https://github.com/tw93/Waza) design skill references. Font, color, motion, and AI slop rules draw on [pbakaus/impeccable](https://github.com/pbakaus/impeccable) (Apache 2.0). Design scaffold concept credited to [getdesign.md](https://getdesign.md) (MIT).*
