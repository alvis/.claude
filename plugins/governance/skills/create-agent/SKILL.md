---
name: create-agent
description: Create a new specialist agent (base.md + frontmatter/claude.json) from the agent template, proposing a model and effort by role archetype and confirming them with the user before writing. Use when adding a new subagent, defining a new specialist role, scaffolding an agent definition, or when update-agent hands off new-agent creation.
model: opus
context: fork
agent: general-purpose
allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, TodoWrite, AskUserQuestion
argument-hint: <name-or-role> [--model=...] [--effort=...] [--permission=...] [--yes]
---

# Create Agent

Creates a new agent as the two source files `<name>/base.md` + `<name>/frontmatter/claude.json`, stitched into one definition per `template:agent`, choosing the agent's model and effort by role archetype and confirming them with the user before anything is written. **Coherence Mandate.** The authored agent must read as one continuous, deliberate personality from its first line — never as the template with blanks filled in. Persona, expertise, Base Context, Coordination Posture, and Collaboration must dissolve into a single voice; visible template seams, placeholder phrasing, "this agent will…" scaffolding, and addendum sections are the failure mode this rule forbids. A create-agent that emits a fill-in-the-blank file cannot credibly enforce coherence on the agents it makes.

## Purpose & Scope

This skill scaffolds a new agent from `template:agent`: it classifies the requested role, derives the agent's Base Context (`SD-`/`RP-`) from `constitution/references/context-catalog.md`, proposes a model + effort from the role archetype, **confirms model and effort with the user**, then writes `base.md` (the persona/charter body) and `frontmatter/claude.json` (the verified key surface) and builds the required `initialPrompt`.

**What this skill does NOT do**:

- Update or refactor existing agent files (use `/update-agent` instead)
- Delete or remove agent files
- Invent frontmatter keys, Base Context aliases, or standard paths not present in `template:agent` / `constitution/references/context-catalog.md`
- Write model or effort into the file without user confirmation (the confirm gate is mandatory unless `--yes`/explicit flags are passed)

**When to REJECT**:

- The requested role duplicates an existing agent (search the `agents/` directory first)
- The role is too vague to classify into an archetype or to write a trigger-bearing `description`
- Template `template:agent` or the catalog `constitution/references/context-catalog.md` is missing or invalid
- `--model`/`--effort` are passed with values outside the valid surface (`opus|sonnet|haiku|fable` / `low|medium|high|xhigh|max`)

## Workflow

ultrathink: you'd perform the following steps

### Step 1: Authoring Orchestration

Do the planning and classification inline; delegate only heavy reads (scanning the existing `agents/` roster, or digging the target repo for role conventions) to a `Task` subagent so this skill's context stays clean.

#### Planning & Classification

1. **Parse `$ARGUMENTS`** — the agent name-or-role, and any `--model` / `--effort` / `--permission` / `--yes` overrides. Derive a kebab `personalized-name-role` (e.g. `priya-fullstack`) and a one-line `description` carrying explicit `use proactively when…` / `must use if…` triggers.
2. **Reject duplicates** — Glob the `agents/` directory; if a same-role agent already exists, stop and point at `/update-agent`.
3. **Classify the role archetype** — from the role, place it as **producer** (writes/edits — mechanical, routine, or judgment), **critic** (reviews, read-mostly), **orchestrator** (delegates, holds direction), and note **leaf** (never spawns) vs spawn-capable, and background vs interactive. The archetype drives model, effort, `permissionMode`, and `tools`.
4. **Derive Base Context** — select this role's `SD-*` preload subset and lazy `RP-*` aliases **verbatim** from `constitution/references/context-catalog.md` (the catalog is authoritative; never invent an alias or path). There is no shared universal core — list only this role's scoped subset.

#### Model & Effort Selection

Both `model` and `effort` are **fixed at authoring** — one value each for everything this role will ever do, not tuned per task. Pick the cheapest that clears the role's bar; when the role needs more reasoning, prefer raising effort within a tier over jumping to a costlier model.

- **Model — cheapest tier that clears the role's bar:**
  - `haiku` — deterministic/mechanical roles with a known procedure (run tests, lint, collect output, mechanical sweeps).
  - `sonnet` — branching investigation and routine/moderate edits with a few decision points.
  - `opus` — judgment-heavy production (features, non-trivial fixes, refactors) and most critics.
  - `fable` — adversarial scrutiny, deep reasoning, research, design, and orchestration — where correctness hinges on subtle judgment or synthesis across many sources.
- **Effort — reasoning depth the role's work demands** (omit for `haiku`; the live Claude Code docs win on exact semantics):
  - `low` — shallow, near-deterministic; the procedure is known.
  - `medium` — a few genuine decision points.
  - `high` — sustained multi-step judgment; correctness hinges on the reasoning.
  - `xhigh` — deep adversarial scrutiny or synthesis across many sources.
  - `max` — exhaustive reasoning for a pivotal one-shot decision; reserve for gates where cost is no object.
- **Archetype → (model, effort) starting points** (tunable, not law):
  - mechanical / leaf-mechanical → (`haiku`, effort omitted)
  - routine / scaffolding producer → (`sonnet`, `low`–`medium`)
  - judgment producer → (`opus`, `high`)
  - critic → (`opus`, `high`)
  - adversarial / deep-reasoning / research / design → (`fable`, `high`–`xhigh`)
  - orchestrator / tech-lead → (`fable`, `high`)
  - one-shot deep-reasoning gate → (`opus`/`fable`, `max`)

Also propose, from the same archetype: `permissionMode` (main/spawned → `auto` for opus/fable producers, `acceptEdits` for sonnet/haiku producers, `default` for critics; workflow-spawned → always `acceptEdits`; teammate → inherits the lead's — never set), `color`, and `tools` (omit for the full set, or an explicit leaf list).

#### Confirmation Gate (mandatory)

Before writing anything, issue **one `AskUserQuestion` battery** (≤4 questions) confirming the proposal — the inferred value is listed **first and marked "(Recommended)"**, a free-text "override" is the last option, one-tap acceptance is the primary path:

1. **Model** — recommended tier + the other three.
2. **Effort** — recommended level + neighbours (state "omitted — haiku" when the model is haiku).
3. **`permissionMode`** and **leaf-vs-spawn** — include only when they deviate from the archetype default.

`--model=`/`--effort=`/`--permission=`/`--yes` skip the corresponding prompt (accept the recommendation). Record the confirmed values as the frontmatter this run will write.

#### Authoring

Write the two source files under the repository's `agents/` directory (the same location `/update-agent` scans) — `agents/<name>/base.md` and `agents/<name>/frontmatter/claude.json` — stitched at build per `template:agent` (`---\n${yaml.dump(JSON.parse(claude.json))}---\n\n${base.md}`):

- **`frontmatter/claude.json`** — valid JSON over only the `template:agent` key surface (`name`, `description`, `color`, `model`, `effort`, `permissionMode`, `tools`, `disallowedTools`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `isolation`, `maxTurns`, `initialPrompt`); invent no key. Re-check the live Claude Code docs for the current valid key surface before writing — `template:agent` mirrors it at time of writing, but the docs win on conflict; log any conflict found. **Leaf encoding**: a leaf agent gets an explicit `tools` list that **omits `Agent`** — `disallowedTools:["Agent"]` is NOT valid for leafing. `initialPrompt` is REQUIRED.
- **`base.md`** — pure-markdown body (no frontmatter) with the `template:agent` sections woven into one voice: `# Name — Role`, `## Expertise & Style`, `## Communication Style`, `## Base Context` (the catalog subset from Planning), `## Coordination Posture (Axis-2)` (loop, convergence predicate, iteration budget — warm-core register only if this role joins the warm team; leaf/mechanical stay terse), `## Collaboration` (spawn edges; state plainly if it is a leaf).
- **`initialPrompt`** — build the required role-kickoff string per `constitution/templates/role-prompt.md` (load context → confirm loop/stop → loop → convergence predicate + budget → guardrail), in the agent's own voice, compressing the Base Context.

#### Verification

- Frontmatter parses as JSON and every key is on the live-doc-checked valid surface; `permissionMode` matches the agent's launch scenario; leaf agents omit `Agent` from `tools`.
- `initialPrompt` is present and non-empty.
- Every Base Context `SD-`/`RP-` alias resolves against `constitution/references/context-catalog.md`.
- `base.md` reads as one continuous personality (Coherence Mandate) — no template seams or placeholder phrasing.

### Step 2: Reporting

**Output Format**:

```
[✅/❌] Command: create-agent $ARGUMENTS

## Summary
- Agent created: [name]
- Archetype: [producer/critic/orchestrator · leaf?/background?]
- Model / Effort: [model] / [effort or "omitted (haiku)"]  ([confirmed by user | --yes | flag])
- permissionMode: [default/acceptEdits/auto]

## Files Written
- agents/[name]/base.md
- agents/[name]/frontmatter/claude.json

## Base Context
- Preloaded: [SD-* list]
- Lazy: [RP-* list]

## Verification
- Frontmatter key surface: [PASS/FAIL]
- initialPrompt present: [PASS/FAIL]
- Base Context aliases resolve: [PASS/FAIL]
- Coherence (single voice): [PASS/FAIL]

## Issues Found (if any)
- **Issue**: [description]
  **Resolution**: [applied fix or manual intervention needed]
```

## Examples

### Create from a role description

```bash
/create-agent "priya-fullstack — full-stack feature implementer"
# Classifies as a judgment producer → proposes (opus, high), permissionMode auto
# AskUserQuestion confirms model + effort, then writes agents/priya-fullstack/{base.md,frontmatter/claude.json}
```

### Create a leaf/mechanical runner

```bash
/create-agent "test-runner" --yes
# Classifies as mechanical leaf → (haiku, effort omitted), acceptEdits, tools omit Agent
# --yes accepts the recommendation; no confirm prompt
```

### Create a critic with explicit overrides

```bash
/create-agent "security-champion — adversarial security reviewer" --model=fable --effort=xhigh
# Flags pin model + effort (skip those prompts); permissionMode default (critic, read-mostly)
```

### Reject a duplicate

```bash
/create-agent "james-mitchell"
# Error: an agent for this role already exists
# Suggestion: use '/update-agent "james-mitchell"' to change it
```
