# Design Task Workspace

Every design task owns one durable workspace at the project root:

```text
./.design-<area-noun-phrase>/
├── CONTEXT.md
├── DECISIONS.md
├── boards/        # each board HTML file and its rendered image
├── previews/            # each preview gets its own directory and screenshot
│   └── tokens/          # preview.html + screenshot.webp (+ light/dark variants)
├── captures/            # temporary browser captures and computed-style data
└── inventories/         # facelift/content inventories and comparison data
```

Create only the subdirectories needed by the task, but every temporary design
artifact must remain below `./.design-<area-noun-phrase>/`. This includes HTML, CSS,
JSON, PNG, WebP, screenshots, browser captures, preview exports, and facelift
inventories. Board images stay beside their board HTML in `boards/`. Preview
screenshots stay beside their preview HTML under `previews/<preview-slug>/`.
Do not use a session scratchpad or `$TMPDIR` fallback. Production implementation
files remain in their normal source locations.

## Bootstrap and resume gate

1. Derive a short, stable, filesystem-safe noun phrase from the target (for
   example, `marketing-homepage` or `checkout-dialog`). Use it consistently for
   the workspace name during the run.
2. Before creating anything, inspect the project root for `./.design` and every
   `./.design-*` directory.
3. If an existing design directory is found, ask the user whether to resume one
   of the existing tasks or start a new `./.design-<area-noun-phrase>/` task. For a
   legacy `./.design` directory, explicitly offer to resume/migrate it or start
   a new named workspace. Never silently reuse, overwrite, or merge workspaces.
4. On resume, read `CONTEXT.md` and `DECISIONS.md` before generating a board and
   continue from the recorded current phase and next action.
5. On a new task, create `CONTEXT.md` and `DECISIONS.md` before asking design
   questions or writing a board. Keep them current throughout the run.

The workspace is a resume record, not disposable system temp space. Do not
delete it automatically after sign-off; ask the user before archiving or
removing it.

## `CONTEXT.md`

Write the current design context and general direction here. It must include:

- task target and requested outcome;
- audience, primary user task, and usage context;
- supplied inputs and evidence (URL, screenshot, code, Figma, or description);
- detected framework and existing design-system constraints;
- accessibility, responsiveness, performance, brand, and content constraints;
- the three-line Direction Summary once confirmed;
- the active workspace path and root `DESIGN.md` path; and
- current phase, last completed action, and exact next action for a resume.

Update context when the target, constraints, direction, or phase changes. Keep
candidate-by-candidate decisions in `DECISIONS.md`, not as an unstructured
appendix here.

## `DECISIONS.md`

Append one decision record immediately after every visual choice. This includes
the direction pick, every area/component pick, mix-and-match revisions,
connective-tissue choices, and any visual library or architecture decision.

Each record must identify:

- decision ID, date, phase, and area/component;
- the user question and the board HTML and screenshot paths;
- every presented candidate, with its number, name, rank, why-this-rank, and
  concrete design details: composition, hierarchy, content treatment,
  typography, palette/surfaces, spacing, imagery, responsive behavior,
  interaction/motion, states, and separator treatment where applicable;
- the chosen candidate or merged variant;
- every rejected candidate and a one-line reason for rejection;
- the user's confirmation or the `--quick` auto-pick rationale; and
- the resulting follow-up or next action.

Never record only `#2 chosen`. The record must preserve enough detail for a
fresh agent to reproduce the selected design without reopening the screenshot.
The root `DESIGN.md` may summarize these decisions, but this file is the
authoritative detailed visual decision history.

## Root `DESIGN.md` and the goal handoff

`<root>/DESIGN.md` is the general direction and implementation handoff for the
overall design: visual thesis, content plan, interaction thesis, design tokens,
layout principles, and the final assembled system. Create or update it from
`references/design.template.md` during the task; do not wait until the end to
establish the general direction.

Put this exact one-line goal statement near the top of the root `DESIGN.md`,
replacing the placeholder with the active noun phrase:

```text
/goal Follow the decisions in ./.design-<area-noun-phrase>/DECISIONS.md for this design task.
```

`DESIGN.md` §10 must link to both `CONTEXT.md` and `DECISIONS.md` and summarize
the chosen direction, area picks, rejected candidates, and sign-off state. Do
not use it as a replacement for the detailed decision records.
