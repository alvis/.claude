---
name: install-agents
description: "Discover, validate, stitch, and install specialist agent templates contributed by Essential and other enabled plugins in the same marketplace. Use when asked to install agents, set up subagents, refresh the agent team, or configure Claude Code on a new machine."
allowed-tools: Bash, Read
---

# Install Agents

Installs agent templates contributed by Essential and the other enabled plugins in this marketplace. Once stitched under `~/.claude/agents/`, Claude Code auto-discovers them without `settings.json` wiring.

## What the installer does

`scripts/install-agents.sh` is idempotent and safe to re-run:

1. In a source checkout, discovers `plugins/*/templates/agents/*`; from an installed Essential plugin, reads `claude plugin list --json` and discovers templates only from enabled plugins in Essential's marketplace.
2. Validates every `base.md` + `frontmatter/claude.json` pair, including its role-based spawn posture, model/effort, `SendMessage` capability, and centralized-policy boundary, and rejects malformed or duplicate names before touching the destination.
3. Stitches all definitions into a temporary staging directory.
4. Copies staged files into `~/.claude/agents/`, overwriting discovered same-named agents while leaving unrelated and formerly managed files untouched.
5. Prints each installed path and a final count.

## Workflow

### Step 1: Run the installer

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/install-agents/scripts/install-agents.sh"
```

### Step 2: Verify

Smoke-check one representative definition after confirming the installer's reported count:

```bash
head -3 ~/.claude/agents/raj-patel-techlead.md
```

In a fresh Claude Code session, the roster appears in the agent list.

For maintainer verification, run the deterministic contract suite:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest plugins/essential/skills/install-agents/scripts/test_install_agents.py
```

### Step 3: Report

Tell the user:

- How many agents were installed and the destination (`~/.claude/agents/`)
- That they take effect in the next session (the current session's agent list is fixed at startup)
- That re-running overwrites currently discovered agents and does not prune any other files
