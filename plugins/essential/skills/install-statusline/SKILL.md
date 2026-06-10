---
name: install-statusline
description: >
  Install the bundled Bullet Train statusline (bin/statusline) into ~/.claude
  and wire settings.json statusLine. Use when asked to "install the
  statusline", "set up my statusline", "fix/restore statusline", or after
  setting up Claude Code on a new machine.
allowed-tools: Bash, Read
---

# Install Statusline

Installs the version-controlled statusline bundled with this skill onto the current machine. The statusline renders: time · ⎇ branch with jj/git state markers (✎±N undescribed work, ±N dirty files, ∅ empty jj @, ××N conflicts, ↑N/↓N sync arrows) · repo|relative-path · ❯❯❯ · model · ⬩ context % (tokens) · 5h/7d rate-limit braille bars · output style. In jj-colocated repos it reads `@` metadata with `--ignore-working-copy` (no snapshot churn) and resolves the branch label from the nearest bookmark.

## What the installer does

`scripts/install-statusline.sh` is idempotent and safe to re-run:

1. Verifies `jq` is available (aborts with install hint if not)
2. Copies `bin/statusline` → `~/.claude/bin/statusline` and marks it executable (copy, not symlink, so it survives plugin relocation)
3. Sets `statusLine` in `~/.claude/settings.json` to `{"type": "command", "command": "~/.claude/bin/statusline"}` — atomic write, with a timestamped backup taken only when the value actually changes
4. Smoke-tests the installed binary with a fixture JSON
5. Retires legacy `~/.claude/statusline-command.sh` / `statusline-command-backup.sh` by moving them to `/tmp/` (restorable until next reboot/cleanup)

## Workflow

### Step 1: Run the installer

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/install-statusline/scripts/install-statusline.sh"
```

If it aborts because `jq` is missing, install it (`brew install jq` on macOS) and re-run.

### Step 2: Verify

Pipe a sample status JSON into the installed binary and confirm a rendered line appears:

```bash
printf '%s' '{"model":{"display_name":"Claude"},"workspace":{"current_dir":"'"$PWD"'","project_dir":""},"output_style":{"name":"default"},"context_window":{"total_input_tokens":120000,"used_percentage":60}}' | ~/.claude/bin/statusline
```

### Step 3: Report

Tell the user:

- Installed path (`~/.claude/bin/statusline`) and the rendered sample line
- Settings backup path, if one was created
- `/tmp/` location of any retired legacy scripts (restore with `mv` if ever needed)
- The statusline takes effect on the next render — no restart required
