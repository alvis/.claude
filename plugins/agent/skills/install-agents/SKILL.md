---
name: install-agents
description: >
  Install the bundled specialist agent roster into ~/.claude/agents. Use when
  asked to "install the agents", "set up my subagents", "refresh the agent
  team", or after setting up Claude Code on a new machine.
allowed-tools: Bash, Read
---

# Install Agents

Installs the version-controlled specialist agent roster bundled with this skill onto the current machine. The roster is the 20-agent team (tech lead, principal engineer, data architect, security champion, testing evangelist, frontend designer/implementer, and more) that the delegation map (this plugin's `CLAUDE.md`) routes work to. Once installed under `~/.claude/agents/`, Claude Code auto-discovers them — no `settings.json` wiring needed.

## What the installer does

`scripts/install-agents.sh` is idempotent and safe to re-run:

1. Resolves the bundled roster at `references/agents/*.md` and asserts it is non-empty
2. Creates `~/.claude/agents/` if missing
3. Copies each `*.md` into `~/.claude/agents/` (copy, not symlink, so it survives plugin relocation)
4. Overwrites managed same-named files; leaves unrelated user agents untouched (no destructive sync)
5. Prints each installed path and a final count

## Workflow

### Step 1: Run the installer

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/install-agents/scripts/install-agents.sh"
```

### Step 2: Verify

Confirm the roster landed and each file is a valid agent definition (starts with `---` frontmatter containing `name:`):

```bash
ls ~/.claude/agents/*.md | wc -l
head -3 ~/.claude/agents/raj-patel-techlead.md
```

In a fresh Claude Code session, the roster appears in the agent list.

### Step 3: Report

Tell the user:

- How many agents were installed and the destination (`~/.claude/agents/`)
- That they take effect in the next session (the current session's agent list is fixed at startup)
- That re-running is a clean overwrite of the managed files and leaves other user agents alone
