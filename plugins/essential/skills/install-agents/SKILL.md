---
name: install-agents
description: "Discover, validate, stitch, and install specialist agent templates contributed by Essential and other enabled plugins in the same marketplace. Use when asked to install agents, set up subagents, refresh the agent team, or configure Claude Code or Codex on a new machine."
allowed-tools: Bash, Read
---

# Install Agents

Installs agent templates contributed by Essential and the other enabled plugins in this marketplace. The same authoritative template becomes a Claude Code Markdown definition under `~/.claude/agents/` or a Codex TOML definition under `~/.codex/agents/`.

## What the installer does

`scripts/install-agents.sh` is idempotent and safe to re-run:

1. In a source checkout, discovers `plugins/*/templates/agents/*`; from an installed Essential plugin, reads the current harness's plugin list and discovers templates only from enabled plugins in Essential's marketplace.
2. Validates every `base.md` + `frontmatter/claude.json` pair, including its role-only definition name, three distinct preferred short teammate names, runtime tool inheritance, intelligence level, centralized-policy boundary, and required project-memory path and maintenance contract, and rejects malformed or duplicate names before touching the destination.
3. Stitches all definitions into Claude Code Markdown or native Codex TOML. Each template's `intelligenceLevel` is projected through the authoritative [intelligence-level matrix](references/intelligence-levels.json), which owns both harnesses' model and effort fields. Codex receives `name`, `description`, `developer_instructions`, and the mapped `model` and `model_reasoning_effort`; an inherited level omits both Codex fields.
4. Copies staged files into the selected harness's agent directory, overwriting discovered same-named agents while leaving unrelated and formerly managed files untouched.
5. Prints each installed path and a final count.

Codex has no safe equivalent for Claude's color, permission mode, project-memory mode, turn limit, startup prompt, or per-agent hooks, so the projection omits them. It also removes the Claude-managed `Memory` section and only the Dynamic Workflow portion of `Delegation Modes`, retaining direct persistent delegation; model tools, sandboxing, approvals, and local memories remain Codex-owned.

## Workflow

### Step 1: Run the installer

Run the command for the active harness:

```bash
# Claude Code
bash "${CLAUDE_PLUGIN_ROOT}/skills/install-agents/scripts/install-agents.sh" \
  --harness claude

# Codex
bash "${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/install-agents/scripts/install-agents.sh" \
  --harness codex
```

Codex does not currently ingest custom agents directly from a plugin. This install step uses its supported personal-agent directory; start a fresh session afterward so Codex loads the new TOML definitions.

### Step 2: Verify

Smoke-check one representative definition after confirming the installer's reported count:

```bash
# Claude Code
head -3 ~/.claude/agents/tech-lead.md

# Codex
head -3 ~/.codex/agents/tech-lead.toml
```

In a fresh session, the roster appears in the selected harness's agent list. For Codex, confirm a lead such as `tech-lead` uses `gpt-5.6-sol` and the lightweight `test-runner` uses `gpt-5.6-luna`.

For maintainer verification, run the deterministic contract suite:

```bash
uvx pytest plugins/essential/skills/install-agents/scripts/test_install_agents.py
```

### Step 3: Report

Tell the user:

- How many agents were installed and the selected destination
- That they take effect in the next session (the current session's agent list is fixed at startup)
- That re-running overwrites currently discovered agents and does not prune any other files
