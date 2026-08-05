# Governance authoring invariants

These are the repository-wide rules for authoring skills, agents, and
standards. `plugins/governance/skills/write-skill/references/authoring.md` owns
the portable Agent Skills directory, frontmatter, resource, and validation
contract.

## Content

- Before adding content, check it changes what someone does, and that what is
  missing isn't something else. Drop anything whose removal changes nothing —
  naming an example set of negations is unbounded and says nothing.
- Write one coherent document. Integrate changes where readers expect them;
  remove superseded prose instead of appending corrections or addenda.
- Concision must preserve operational sufficiency. An artifact is not complete
  when it names an outcome but omits the decisions, failure behavior, or
  verification needed to produce it.
  Trim repetition and ceremony; never trim the executable contract.
- Use headings that fit the capability. Boundaries, inputs, workflow,
  verification, and completion are useful defaults, not mandatory names.
- Delegate when direct execution would consume more session context than a
  bounded assignment and report. Follow [delegation.md](delegation.md) whenever
  an artifact dispatches subagents.

## Content Boundary Convention

Enclose each block of important or long content in a semantically-named XML
tag so the block has an unambiguous, machine- and eye-visible boundary and
cannot bleed into surrounding prose. The tag names the content's role — it is
not a copy of the section heading and does not replace the `##`/`###`
headings that give the document its outline.

Tags in use: `<report>` encloses a machine-readable report or output
contract; `<IMPORTANT>` encloses a hard guardrail or critical instruction
that must not be missed.

- Name tags for the content, never for the section; do not wrap a short
  structural section in a tag that merely echoes its heading.
- Tags never replace headings — where both apply, keep both.
- Keep a language hint on a fenced block inside the tags (the tags are the
  boundary, the fence is the syntax hint).
- Every opening tag has a matching close.
