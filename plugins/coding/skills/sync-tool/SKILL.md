---
name: sync-tool
description: 'Install or update coding CLI tools (brew, jj, gh) across macOS, Linux, and Windows. Triggers when: "install jj", "install gh", "install brew", "update my coding tools", "missing gh command", "missing jj command", "set up CLI dependencies". Also use when: a sibling skill needs to ensure a tool is on PATH before running. Examples: "install gh and jj", "make sure jj is up to date", "sync coding tools".'
model: sonnet
argument-hint: '[--only <name1,name2>] [--check] [--dry-run] [--force]'
eval_type: process
---

# Sync Tool

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Idempotently install or update a registered set of coding CLI tools (`brew`, `jj`, `gh`) across macOS, Linux, and Windows so any sibling skill can guarantee its dependencies are on `PATH`. Each tool is installed from its official upstream source with a per-OS branch.
**When to use**:

- A user requests installation/update of `brew`, `jj`, or `gh` (e.g., "install jj", "update my coding tools", "missing gh command").
- A sibling skill (e.g., `coding:stack-code`) needs to ensure `jj`/`gh` are present before running.
- Bootstrapping a fresh machine for coding work where the registered CLIs must be present at minimum versions.
**Prerequisites**:

- A POSIX-compatible shell (`bash`) on macOS/Linux, or Git-Bash/MSYS/Cygwin on Windows.
- Network access to upstream package sources (Homebrew, GitHub releases, apt/dnf, winget, crates.io).
- `python3` (3.8+) on `PATH` to run `scripts/sync.py`.

### Your Role

You are a **Tool Sync Director** who orchestrates dependency installation like a release engineer running a bootstrap pipeline. You never install tools directly yourself; you parse arguments, dispatch a single execution subagent to run `scripts/sync.py`, then verify the resulting per-tool report. Your management style emphasizes:

- **Strategic Delegation**: Hand the full registry run to one execution subagent rather than fanning out per tool — the script already serializes correctly.
- **Idempotent Coordination**: Always allow re-runs; trust `--check` and `--dry-run` to make state visible before taking action.
- **Quality Oversight**: Read the per-tool status lines and decide whether the run was clean, partial, or failed.
- **Decision Authority**: On failure, decide whether to retry a single tool with `--only` or escalate the error to the caller.

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

This skill has no required inputs. Invoking it with no arguments runs the full registry in order.

#### Optional Inputs

- **`--only <csv>`**: Comma-separated subset of registered tool names to sync (e.g., `--only=jj,gh`). Registry order is preserved regardless of CSV order.
- **`--check`**: Status-only mode. Reports what is missing/outdated and exits non-zero if any registered tool is not at minimum version. No installation is performed.
- **`--dry-run`**: Print the planned installer command for each selected tool without executing it. Sets `DRY_RUN=1` for each `installers/<tool>.sh`.
- **`--force`**: Reinstall/upgrade even when the tool is present and at minimum version. Sets `FORCE=1` for each installer.
- **`SYNC_TOOL_NO_WAIT=1` (env var)**: For `gh.sh` post-install — print the auth banner once and exit non-zero instead of polling. Lets CI/non-interactive callers fail fast.

#### Expected Outputs

- **Per-tool status line** on stdout, one per selected tool, in the form `{tool}: {status} ({action})` where `status ∈ {installed, updated, already_current, skipped, failed}` and `action` is the underlying command run (or "noop" for `already_current`).
- **Summary report**: A trailing line `summary: N tools — X installed, Y updated, Z already_current, W skipped, V failed`.
- **Process exit code**: `0` if every selected tool ended in `installed | updated | already_current | skipped`; non-zero if any ended in `failed`. In `--check` mode, non-zero if any registered tool is missing or below its minimum version.

#### Data Flow Summary

The skill reads CLI flags, resolves a tool list (default = full registry, in order), then for each tool: detects the OS via `uname -s`, executes `scripts/installers/<tool>.sh` (passing `DRY_RUN`/`FORCE` env vars), verifies the resulting `<tool> --version` against the per-tool minimum, and (for `gh` only) polls `gh auth status` until authenticated or the user aborts. Each tool's outcome is emitted as a status line, then a summary line and a final exit code reflecting overall success.

### Visual Overview

#### Main Skill Flow

```plaintext
   YOU                              SUBAGENTS
(Orchestrates Only)             (Perform Tasks)
   |                                   |
   v                                   v
[START]
   |
   v
[Step 1: Parse args & resolve tool list]
   |
   v
[Step 2: Dispatch sync.py run] ─────→ (Subagent: run scripts/sync.py with flags)
   |                                       │
   |                                       ├─ for each tool in registry order:
   |                                       │    detect OS → run installers/<tool>.sh
   |                                       │    → verify version
   |                                       │    → (gh only) poll gh auth status
   |                                       └─ emit per-tool status + summary
   v
[Step 3: Review report]
   |
   v
[Step 4: Decision] ── proceed | retry --only=<failed> | abort
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You parse, dispatch, review, decide
• RIGHT SIDE: One execution subagent runs the registry
• ARROWS (───→): You assign work to the subagent
═══════════════════════════════════════════════════════════════════

Note:
• You: Parse args, dispatch one run, read report, decide
• Subagent: Runs sync.py end-to-end, reports per-tool status
• Skill is LINEAR: Step 1 → 2 → 3 → 4
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. Parse Arguments & Resolve Tool List
2. Dispatch `sync.py` Run
3. Review Per-Tool Report
4. Decision

### Step 1: Parse Arguments & Resolve Tool List

**Step Configuration**:

- **Purpose**: Translate caller arguments into a concrete list of tools to process and the mode flags to pass through.
- **Input**: Raw CLI args (`--only`, `--check`, `--dry-run`, `--force`) plus environment (`SYNC_TOOL_NO_WAIT`).
- **Output**: Resolved tool list (preserving registry order) and mode flags ready to pass to `scripts/sync.py`.
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Read arguments** from the invocation. Default behavior = run full registry (`brew`, `jj`, `gh`) in order.
2. **Validate `--only` values** against registered names listed in `references/tool-registry.md`. Reject unknown names with a clear error.
3. **Detect platform** via `uname -s` to anticipate which installer branch will run (informational; the installers themselves re-detect).
4. **Use TodoWrite** to seed a single task: "Run sync.py with resolved flags" (status `pending`).
5. **Prepare the dispatch**: Build the `python3 scripts/sync.py …` command line with the resolved flags.

**OUTPUT from Planning**: A ready-to-run `sync.py` command line and a single pending todo.

### Step 2: Dispatch `sync.py` Run

**Step Configuration**:

- **Purpose**: Execute the install/update pipeline end-to-end.
- **Input**: The `sync.py` command line from Step 1.
- **Output**: Per-tool status lines and a final summary line on stdout, plus an exit code.
- **Sub-skill**: None
- **Parallel Execution**: No (the registry is intentionally serialized; `brew` must precede `jj`/`gh` on macOS).

#### Phase 2: Execution (Subagent)

**What You Send to Subagent**:

In a single message, you assign the run to one execution subagent.

- **[IMPORTANT]** You MUST ask the subagent to ultrathink hard about each tool's branch and the post-install auth behavior for `gh`.
- **[IMPORTANT]** Use TodoWrite to update the task status from `pending` to `in_progress` when dispatched.

Request the subagent to perform the following:

    >>>
    **ultrathink: adopt the Release Engineer mindset**

    - You're a **Release Engineer** with deep expertise in cross-platform CLI installation who follows these technical principles:
      - **Idempotence First**: Re-running with the same flags must produce the same final state without errors.
      - **Official Sources Only**: Use upstream-recommended install methods per OS (Homebrew on mac, official apt repo / dnf / cargo / tarball on Linux, winget on Windows).
      - **Loud on Failure, Quiet on Success**: Per-tool one-liner on success; clear stderr message + non-zero exit on failure.
      - **Never Run Interactive Auth**: For `gh`, poll `gh auth status` and instruct the user via banner — never invoke `gh auth login` automatically.

    **Read the following references** and follow them:

    - plugins/coding/skills/sync-tool/references/tool-registry.md
    - plugins/coding/skills/sync-tool/references/platforms.md

    **Assignment**
    Run the `sync.py` command line provided by the caller end-to-end:

    - Command: `python3 plugins/coding/skills/sync-tool/scripts/sync.py [flags]`
    - Tools (registry order): brew, jj, gh
    - Mode flags pass through to each installer as env vars: `DRY_RUN=1` for `--dry-run`, `FORCE=1` for `--force`.
    - For `gh` only: after install, `gh auth status` is polled per the spec in `installers/gh.sh`. If `SYNC_TOOL_NO_WAIT=1` is set, banner-once-and-fail.

    **Steps**

    1. Run the provided `sync.py` command line.
    2. Capture stdout per-tool status lines as they are emitted.
    3. Capture the final summary line and the process exit code.
    4. Do not retry on failure — report and let the caller decide.

    **Report**
    **[IMPORTANT]** You MUST return the following execution report (<1000 tokens):

    ```yaml
    status: success|failure|partial
    summary: 'Ran sync.py for N tools'
    modifications: ['<tool> -> <status>', ...]
    outputs:
      per_tool: ['brew: <status> (<action>)', 'jj: <status> (<action>)', 'gh: <status> (<action>)']
      summary_line: '<verbatim summary line from sync.py>'
      exit_code: <int>
    issues: ['issue1', ...]  # only if any tool ended in failed
    ```
    <<<

### Step 3: Review Per-Tool Report

**Step Configuration**:

- **Purpose**: Confirm each selected tool reached an acceptable end state.
- **Input**: Execution report from Step 2.
- **Output**: A pass/fail decision per tool and overall.
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 3: Review (You)

**What You Do**:

1. Parse the `per_tool` list from the execution report.
2. Mark each tool: `pass` if status ∈ `{installed, updated, already_current, skipped}`; `fail` otherwise.
3. If `--check` was passed and any tool is missing or below minimum version, mark overall as `fail` (this is the documented contract).
4. Note any `gh` post-install auth wait that timed out or was aborted (status `failed` with a `gh-auth-aborted` or `gh-auth-no-wait` action).

### Step 4: Decision

#### Phase 4: Decision (You)

**What You Do**:

1. **Apply decision criteria**:
   - All tools pass → **PROCEED**: emit final summary, mark todo `completed`, return exit code 0.
   - One tool failed with a transient/auth issue (e.g., `gh-auth-aborted`) → **DEFER TO CALLER**: surface the banner instructions; do not auto-retry interactive auth.
   - One tool failed with an installation error → **RETRY ONCE** with `--only=<that-tool>` and the same mode flags. If the retry also fails → **ABORT** with the underlying error.
   - In `--check` or `--dry-run` mode → never retry; always just report.
2. **Use TodoWrite** to update the task list:
   - PROCEED: mark `completed`.
   - RETRY: add a new todo for the retry; on second failure, mark both `failed`.
   - ABORT: mark `failed` with the error captured.
3. **Prepare final output**: Echo the verbatim per-tool lines and summary line from the subagent report; surface the exit code as the skill's exit code.

### Skill Completion

**Report the skill output as specified**:

```yaml
skill: sync-tool
status: completed|partial|failed
outputs:
  per_tool:
    - 'brew: <status> (<action>)'
    - 'jj: <status> (<action>)'
    - 'gh: <status> (<action>)'
  summary_line: '<verbatim summary line from sync.py>'
  exit_code: <int>
  mode:
    check: <bool>
    dry_run: <bool>
    force: <bool>
    only: ['<tool>', ...] | null
summary: |
  Ran sync-tool against [registry|--only subset]; [N] tools reached an acceptable
  end state. See per_tool for details. For gh, auth state is reported separately
  and may require the user to run `gh auth login` in another terminal.
```

## 4. EXAMPLES

```bash
# Install/update everything in registry order (brew → jj → gh)
python3 plugins/coding/skills/sync-tool/scripts/sync.py

# Only sync jj and gh (e.g., from coding:stack-code)
python3 plugins/coding/skills/sync-tool/scripts/sync.py --only=jj,gh

# Status-only check; non-zero exit if anything is missing/outdated
python3 plugins/coding/skills/sync-tool/scripts/sync.py --check

# Show what would run without executing
python3 plugins/coding/skills/sync-tool/scripts/sync.py --only=jj --dry-run

# Force reinstall/upgrade even if at minimum version
python3 plugins/coding/skills/sync-tool/scripts/sync.py --force

# Non-interactive: skip the gh auth poll, fail fast
SYNC_TOOL_NO_WAIT=1 python3 plugins/coding/skills/sync-tool/scripts/sync.py --only=gh
```
