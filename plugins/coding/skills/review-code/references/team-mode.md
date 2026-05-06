# Team Mode Workflow

Use this workflow when the session context contains `**Agent Teams**: enabled` under the "Agent Capabilities" section. This is the Team Mode branch of Step 2.

## Phase 1: Planning & Scope Selection (Lead)

**Context Detection & Scope Selection**:

**Detect execution environment**:

- Check if CI/non-interactive mode (no user interaction available)
- Check if interactive mode (user can respond to prompts)

**Resolve specifier** (if provided): see `references/specifier-resolution.md` for the per-type resolution logic and file-discovery rules.

**Determine default scope based on context**: see `references/specifier-resolution.md` (Default Scope Determination ladder).

**File Discovery**: see `references/specifier-resolution.md` (File Discovery section).

**Pre-pass mechanical scan**: Run `python3 plugins/coding/scripts/scan_potential_violations.py <discovered-files> --category all --before 5 --after 10` and capture the stdout. Slice the report by category and route each slice to the relevant reviewer when spawning their task:

| Reviewer | Categories from report |
|---|---|
| `docs-reviewer` | `jsdoc-uppercase`, `jsdoc-fullstop` |
| `test-reviewer` | `test-hooks` |
| `quality-reviewer` | `let` |
| `style-reviewer` | all four (style polish) |
| `security-reviewer` | (none — no relevant categories) |

Pass the slice as a "Candidate violations (advisory; verify against scan.md before flagging)" section in the dispatch prompt. Reviewers MUST re-check every candidate against the loaded rule files (`DOC-FORM-03`, `DOC-FORM-04`, `TST-MOCK-04`, `TST-MOCK-10`, `TST-DATA-01`, `TST-DATA-05`, `TST-STRU-04`, `TYP-CORE-05`) and discard candidates that fall under sanctioned exceptions. If `python3` is unavailable, log a warning and proceed without the pre-pass.

## Phase 2: Team Setup & Execution

1. **Create team**: `TeamCreate` with name `review-team`

2. **Initialize agent pool registry** tracking:
   - Name (agent identifier)
   - Role (reviewer type: test, security, code-quality, documentation, style)
   - Model (opus for specialized, haiku for general)
   - Context Level (%)
   - Status (working, idle, retired)

3. **Spawn specialized reviewer teammates** (one per selected scope):

   For each selected scope, spawn appropriate agent:

   - **test scope**: `Task` with `team_name="review-team"`, `name="test-reviewer"`, `subagent_type="coding:ava-thompson-testing-evangelist"`, `model="opus"`
   - **security scope**: `Task` with `team_name="review-team"`, `name="security-reviewer"`, `subagent_type="coding:nina-petrov-security-champion"`, `model="opus"`
   - **code-quality scope**: `Task` with `team_name="review-team"`, `name="quality-reviewer"`, `subagent_type="coding:marcus-williams-code-quality"`, `model="opus"`
   - **documentation scope**: `Task` with `team_name="review-team"`, `name="docs-reviewer"`, `subagent_type="general-purpose"`, `model="opus"`
   - **style scope**: `Task` with `team_name="review-team"`, `name="style-reviewer"`, `subagent_type="general-purpose"`, `model="opus"`

4. **Create review tasks**: `TaskCreate` for each scope with:
   - Subject: "Review [scope] (e.g., test, security)"
   - Description: Full instructions including:
     - **Neutral preamble** (verbatim): "You are an independent reviewer. Treat the artifact as unfamiliar code. Apply the rubric without assuming the author's intent was correct."
     - **Core Review Mandates** (plan adherence, non-mechanical redundancy, sibling consistency across adapters/mappers/etc., zero-tolerance semantics, delegate mechanical checks to lint/tsc/knip) — see top of skill
     - Path to the approved plan document (PLAN.md/DRAFT.md/DESIGN.md/PR description) for drift checking — pass the file path only; do NOT summarize or paraphrase the plan
     - Scope/file-set name and the file paths to analyze (NOT file contents)
     - Rubric / standard file paths to consult (e.g., `plugins/coding/constitution/standards/code-review.md`, plus the area-specific scan standard such as `/absolute/path/to/standards/testing.md`)
     - **Output target**: the absolute path to the area file under `<out>/` (e.g., `<project-root>/reviews/SECURITY.md`) — the subagent writes this file directly
     - **Template**: `references/review.template.md` — the canonical structure to follow (frontmatter, verdict, General Status, Issues grouped P0→P3, Pending Decisions)
     - **Re-run instruction**: if the target file already exists, read it first; cross-reference new findings against any unchecked (`- [ ]`) issues by `Source` location + `Issue` text; reuse the original `<PREFIX>-P<n>-<seq>` ID for matched issues; preserve any Pending Decisions context on matched issues; for prior unchecked issues with no current match, confirm the issue no longer applies before dropping it; new unmatched findings get the next available sequence per priority
     - Instruction to calculate and report `context_level` from token usage in the completion message back to the lead

   **Do NOT include in the task description**: parent-conversation framing, the implementer's reasoning narrative, "what we built and why" prose, sibling reviewers' findings during this initial pass, or any "the user wants X" / "we decided Y" sentences. The reviewer must form judgments solely from the artifact + rubric + template.

5. **Assign ownership**: `TaskUpdate` to set owner for each task to corresponding reviewer

## Phase 3: Review Cycle

1. **Wait for completion messages** from all reviewers via `SendMessage`

2. **Track context levels**: Each reviewer reports their `context_level` calculated as:
   - `context_level = (input_tokens / context_window_size) × 100`
   - Based on real token usage from conversation metadata

3. **Update agent pool registry** with reported context levels

4. **Collect review reports** via `TaskGet` for each completed task

5. **Optional: Cross-scope review round** (if multiple critical issues found):
   - Check agent pool for idle reviewers with `context_level < 50%`
   - If eligible reviewers exist → Reuse via `SendMessage` with cross-scope review task
   - If not → Spawn fresh reviewers with appropriate specialization
   - Task: Check for conflicts or interactions between scope findings
   - Wait for cross-review completion messages

## Phase 4: Index & Cleanup

1. **Verify per-area files**:
   - For every scope spawned, confirm the corresponding `<out>/<AREA>.md` file exists and conforms to `references/review.template.md` (frontmatter + verdict line + General Status + Issues + Pending Decisions).
   - If a file is missing, surface the failure rather than silently aggregating.

2. **Generate or refresh `<out>/README.md` index**:
   - One row per area file, with the verdict pulled verbatim from the file's first verdict line (`✅ PASS` or `❌ FAIL — N issues (P0:a, P1:b, P2:c, P3:d)`).
   - Link each area name to its file (e.g., `[Security](./SECURITY.md)`).
   - Include reviewed timestamp and aggregate counts (P0/P1/P2/P3 totals across files).
   - On re-runs, **rewrite** this index entirely from the current area files.

3. **Print console summary**:
   - Counts per priority across all areas.
   - List of FAIL areas with their open-issue counts.
   - Path to `<out>/README.md`.
   - Agent lifecycle statistics (agents spawned, reused, retired).

4. **Shutdown teammates**:
   - Send `SendMessage` with type `shutdown_request` to all active teammates
   - Wait for shutdown confirmations

5. **Cleanup**: `TeamDelete` to remove team

6. **Report**:
   - Display per-area file listing with each verdict.
   - Path to `<out>/README.md` index.
   - Note execution mode: team.
   - Include agent lifecycle stats (spawned, reused, retired by context level).

## Agent Summary

| Role | Agent Type | Model | Lifecycle |
|------|------------|-------|-----------|
| Test Reviewer | `coding:ava-thompson-testing-evangelist` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |
| Security Reviewer | `coding:nina-petrov-security-champion` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |
| Quality Reviewer | `coding:marcus-williams-code-quality` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |
| Docs Reviewer | `general-purpose` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |
| Style Reviewer | `general-purpose` | opus | Spawned per scope; reuse if context < 50% for cross-scope review |

**Context-aware reuse policy**: Reviewers with reported `context_level < 50%` are eligible for reuse in optional cross-scope review rounds. Reviewers with `context_level >= 50%` are retired and replaced with fresh agents if additional review rounds are needed.
