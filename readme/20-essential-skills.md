# essential skills

[Back to marketplace overview](../README.md#plugins-and-skills)

Documentation creation, code design, product strategy, and Notion integration for knowledge management

This catalog is generated from the plugin manifest and each skill's `SKILL.md` frontmatter. Run `python3 scripts/generate_readme.py` after changing either source.

- `essential:autoresearch` — Run a metric-driven research loop: define a metric, evaluator, baseline, and target; evolve candidate solutions; score and adversarially verify them; then mutate survivors until the target, budget, or plateau ends the run. Use for measurable optimization of prompts, code, experiments, or creative variants; use deep-research for fact-finding.
- `essential:decide` — Decides between researched approaches before implementation. Use when asked to choose an approach, challenge a recommendation, make an architecture decision, compare options, define rollback and falsification signals, or obtain approval; routes blindspot passes, brainstorms, interviews, references, and prototypes to essential:discover.
- `essential:deep-research` — Conduct comprehensive multi-source research with AI-assisted analysis and explicit source synthesis. Use when investigating complex topics, comparing evidence, gathering current information, or producing a fact-finding report with citations and uncertainty notes. Do not use for metric-driven candidate optimization.
- `essential:discover` — Discovers material unknowns before planning. Use for a blindspot pass or unknown unknowns, to brainstorm approaches from cheapest to ambitious, interview about architecture, extract reference implementation semantics, make a disposable prototype before touching the real app, or check whether discovery is ready for a decision; researched option selection belongs to essential:decide.
- `essential:handoff` — Create or execute a context-complete cross-domain plan as an orchestrator. Use when another agent must continue without prior context, or when a multi-domain plan needs coordinated execution while this skill retains decision ownership. For coding-session persistence, use coding:handover.
- `essential:install-agents` — Discover, validate, stitch, and install specialist agent templates contributed by Essential and other enabled plugins in the same marketplace. Use when asked to install agents, set up subagents, refresh the agent team, or configure Claude Code on a new machine.
- `essential:install-statusline` — Install the bundled Bullet Train statusline into ~/.claude and wire settings.json statusLine. Use when setting up Claude Code on a new machine, installing or restoring the statusline, or repairing its configuration; preserve the bundled executable and report permission or platform limitations.
