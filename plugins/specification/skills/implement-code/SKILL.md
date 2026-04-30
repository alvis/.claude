---
name: implement-code
description: Execute approved specification-notion tickets end-to-end by resolving ticket intent, committing or iterating on plans, and dispatching coding:* child skills to write, verify, and commit code in an isolated git worktree. Use when asked to implement a Notion ticket, take a spec to code, kick off work on a specification URL/ID, turn an approved plan into shipped commits, or audit and finish a partial implementation tracked in Notion.
model: opus
context: fork
agent: general-purpose
allowed-tools: Read, Grep, Glob, Bash, Task, Skill, TodoWrite, AskUserQuestion, ExitPlanMode
argument-hint: <notion-url-or-id> [--repo=<path>] [--branch=<name>] [--dry-run] [--skip-approval] [--use-cache]
---

# Implement Code

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Turn an approved Notion specification ticket into landed code by resolving ticket status, selecting the right execution mode (commit-plan, iterate, draft-then-ask, audit-and-complete, verify-only, flag-mismatch, or refuse), and orchestrating coding:* child skills inside an isolated git worktree. Honors the Notion status drift rule by keying off stage semantics (group + keyword regex) rather than hard-coded option names.

**When to use**:

- When the user supplies a Notion URL/ID and asks to implement, build, ship, or execute the spec
- When an approved plan-code output (DRAFT.md + PLAN.md) is ready to be translated into commits
- When a previously-started implementation needs to be audited and finished against its spec
- When a Notion ticket status signals readiness for coding (group=to_do/in_progress with ready/approved/implementing keywords) and the user wants work to begin
- Stack-aware: detects when landed changes exceed `coding:stack-code` size thresholds (or semantically modify code an open lower PR depends on) and delegates slicing/restacking to `coding:stack-code` rather than committing flat

**Prerequisites**:

- Notion MCP access for the target workspace and page
- Local git repository (current directory or `--repo=<path>`) with the target spec's codebase
- `superpowers:using-git-worktrees` skill available for worktree creation
- `specification:sync-spec` available for the Step 2 spec bundle download (hard-gated)
- `coding:*` child skills available (draft-code, write-code, complete-code, fix, review, commit, handover)
- `coding:stack-code` available for size-triggered slicing and upstream-restack delegation (thresholds and modes are read from that skill, never hardcoded here)
- `governance:verify-skill` accessible for the final skill-quality gate

### Your Role

You are an **Implementation Director** who orchestrates spec-to-code delivery like an engineering manager coordinating planning leads, worktree operators, and coding specialists. You never write or edit production code directly — every `Write`/`Edit` call happens inside dispatched `coding:*` children. Your management style emphasizes:

- **Strategic Delegation**: Route ticket resolution, plan work, worktree setup, and coding passes to the right specialist subagents
- **Mode-Driven Coordination**: Pick exactly one execution mode per invocation and keep the downstream dispatch aligned to it
- **Quality Oversight**: Gate code landing on `coding:review` passing and `governance:verify-skill` reporting clean
- **Decision Authority**: Make single-gate go/no-go calls (one approval gate after mode resolution) and enforce refusal when the ticket isn't ready
- **Zero Direct Writes**: You never hold the pen on source files — your outputs are decisions, dispatches, and reports

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **Notion URL or ID**: The Notion page identifier for the specification ticket (full URL or bare 32-char ID). Resolves to a page in the specification database (e.g. `292b2572f78880fe95b9fdc8daeb862f`).

#### Optional Inputs

- **--repo=<path>**: Absolute path to the target repository. Defaults to the current working directory.
- **--branch=<name>**: Override the default branch name. Defaults to `feat/impl-<spec-slug>` derived from the ticket title.
- **--dry-run**: Plan and report only. Do not create a worktree, do not dispatch write/edit children, do not commit.
- **--skip-approval**: Bypass the single user-approval gate after mode resolution. Intended for trusted automation contexts.
- **--use-cache**: Reuse an existing `.code-spec/<ticket.slug>/` bundle if `INDEX.md` and `SPEC.md` are both present locally. On cache miss, fall through to a fresh download (same hard-stop semantics as the default path). Default behavior wipes and re-downloads on every invocation.

#### Expected Outputs

- **Mode Decision**: The selected execution mode (`COMMIT_PLAN` | `PI_ITERATE` | `DRAFT_THEN_ASK` | `AUDIT_AND_COMPLETE` | `VERIFY_ONLY` | `FLAG_MISMATCH` | `REFUSE`) with the group + regex rule that fired
- **Worktree Info**: Absolute path to the created worktree and branch name (skipped in `--dry-run` and `VERIFY_ONLY`/`REFUSE`)
- **Consistency Report**: Summary of Spec vs DRAFT vs PLAN vs Code cross-check, including drift/mismatch markers
- **Features Cross-Check**: Mapping of spec Features → implemented symbols with coverage status
- **Child Dispatch Log**: Ordered list of `coding:*` skills dispatched with input summary and exit status for each
- **Commits Landed**: Array of commit SHAs and messages produced by `coding:commit` dispatches
- **Verification Report**: `governance:verify-skill` result for this skill in full mode
- **Final Status**: `completed` | `partial` | `refused` | `flagged` | `dry_run`

#### Data Flow Summary

The skill fetches the Notion ticket, classifies its status by Notion `status` group (`to_do` | `in_progress` | `complete`) combined with keyword regex on the option name, resolves one of seven modes from the Mode Resolution matrix, optionally asks for a single approval, creates an isolated git worktree, dispatches the appropriate chain of `coding:*` children to draft, write, complete, fix, review, and commit code, runs a Consistency Check and Features cross-check before and after code changes, and finally runs `governance:verify-skill implement-code --mode=full` to gate the skill itself.

### Visual Overview

#### Main Skill Flow

```plaintext
   YOU                                  SUBAGENTS / SUB-SKILLS
(Orchestrates Only)                     (Perform Tasks)
   |                                         |
   v                                         v
[START]
   |
   v
[Step 1: Resolve Ticket] ───────────→ (Notion MCP fetch + status classify)
   |                                    group + keyword regex → stage
   v
[Step 2: Download Spec Bundle] ─────→ (sub-skill specification:sync-spec → .code-spec/<slug>/)
   |                                    HARD GATE: stop if root SPEC.md cannot be saved
   |                                    --use-cache short-circuits sub-skill if INDEX.md + SPEC.md exist
   v
[Step 3: Mode Resolution] ──────────→ (Apply Mode Matrix → 1 of 7 modes)
   |
   v
[Step 4: Consistency Check] ────────→ (Spec ↔ DRAFT ↔ PLAN ↔ Code diff)
   |
   v
[Step 5: Features Cross-Check] ─────→ (Spec Features → code symbols coverage)
   |
   v
[Step 6: Approval Gate] ────────────→ (AskUserQuestion — skipped if --skip-approval)
   |
   v ─── approved or skipped ───
[Step 7: Worktree Setup] ───────────→ (superpowers:using-git-worktrees)
   |                                    feat/impl-<spec-slug>
   v
[Step 8: Execute Mode] ─────────────→ (Dispatch coding:* children)
   |                                    draft-code → write-code → complete-code
   |                                    → fix → review → commit → handover
   v
[Step 9: Post-Change Re-Check] ─────→ (Repeat Consistency + Features + DEVIATIONS cross-ref)
   |
   ├──→ [Step 9a: Stack-aware sizing] ──→ coding:stack-code (split|create|restack)
   |        • large change (>~5 files OR >300 LOC OR multi-domain — thresholds read from stack-code)
   |        • OR open stack detected AND landed code semantically alters a lower PR's contract
   |        • orchestrator NEVER calls `jj split` / `gh pr create` directly — always delegates
   v
[Step 10: Thought-Experiment Gate] ──→ (opus + max effort, mandatory, paper-only)
   |
   v
[Step 11: Skill Self-Verify] ───────→ (governance:verify-skill full mode)
   |
   v
[Step 12: Completion Report]
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You orchestrate (no direct writes)
• RIGHT SIDE: Subagents / sub-skills execute tasks
• ARROWS (───→): You dispatch work
• DECISIONS: You select mode + approve/abort based on reports
• Skill is LINEAR: Step 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → (9a) → 10 → 11 → 12
• Step 9a is a conditional sub-branch: only fires on size-trigger or semantic upstream-stack impact
═══════════════════════════════════════════════════════════════════

Note:
• You: Resolve ticket, pick mode, gate approval, dispatch children, decide
• Notion subagent: Fetch page + status (1 call, <1k tokens)
• coding:* children: Perform all Write/Edit/Bash commits (<1k tokens each)
• governance:verify-skill: Final skill quality gate (<500 tokens)
• --dry-run short-circuits Steps 7–10 and still runs Step 11
• REFUSE / FLAG_MISMATCH short-circuit after Step 6
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. Resolve Ticket (Notion fetch + status classification)
2. Download Spec Bundle (sub-skill `specification:sync-spec`; --use-cache short-circuits to reuse local `.code-spec/<slug>/`)
3. Mode Resolution (apply Mode Matrix)
4. Consistency Check (Spec ↔ DRAFT ↔ PLAN ↔ Code)
5. Features Cross-Check (Spec Features → Code symbols)
6. Approval Gate (single, skippable)
7. Worktree Setup (`superpowers:using-git-worktrees`)
8. Execute Mode (dispatch `coding:*` children)
9. Post-Change Re-Check (repeat 4 + 5 + DEVIATIONS cross-ref)
9a. Stack-Aware Sizing & Restack Trigger (delegate to `coding:stack-code` when oversized or upstream-impacting)
10. Thought-Experiment Gate (opus + max effort, mandatory)
11. Skill Self-Verify (`governance:verify-skill`)
12. Skill Completion Report

### Step 1: Resolve Ticket

**Step Configuration**:

- **Purpose**: Fetch the Notion ticket and classify its status by stage semantics (never by exact option name)
- **Input**: `notion_url_or_id`, optional `repo`, `branch`, `dry_run`, `skip_approval`
- **Output**: `ticket` object with `{id, title, slug, status_group, status_option, status_stage, spec_url, has_plan, has_draft, linked_pr}`
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. **Receive inputs** from invocation; parse notion id from URL or accept bare id
2. **Normalize the ticket id** (strip dashes, extract 32-char hex) and build fetch arguments
3. **Use TodoWrite** to create a todo `resolve-ticket` with status `pending`
4. **Prepare a single Notion-fetch task assignment** for one subagent

**OUTPUT from Planning**: One queued subagent task to fetch + classify the ticket

#### Phase 2: Execution (Subagent)

**What You Send to Subagent**:

In a single message, you spin up one Notion specialist subagent.

- **[IMPORTANT]** You MUST ask the subagent to ultrathink hard about the task and requirements
- **[IMPORTANT]** Use TodoWrite to update the todo from `pending` to `in_progress` when dispatched
- **[IMPORTANT]** Do NOT hard-code status option strings. Match stage by `group` + keyword regex.

Request the subagent to perform the following fetch and classification:

    >>>
    **ultrathink: adopt the Notion Ticket Specialist mindset**

    - You're a **Notion Ticket Specialist** with deep expertise in Notion's data model who follows these principles:
      - **Stage-Not-Label**: Key off the `status` property's `group` (`to_do` | `in_progress` | `complete`) and a keyword regex on the option name. Never hard-code literal option strings — workspace labels drift.
      - **Minimal Fetch**: Retrieve only what is needed (title, status, slug source, linked DRAFT/PLAN/PR properties)
      - **Clear Reporting**: Emit a single YAML block describing the resolved ticket

    **Assignment**
    Fetch the Notion page and classify its status stage:

    - **Notion ID**: [normalized 32-char id]
    - **Database**: specification DB (e.g. 292b2572f78880fe95b9fdc8daeb862f)

    **Steps**

    1. Fetch the page via Notion MCP (`notion-fetch` or equivalent)
    2. Extract:
       - `id`, `title`, derived `slug` (kebab-case of title)
       - `status.group` (one of `to_do` | `in_progress` | `complete`)
       - `status.option_name` (raw label, for logging + fallback)
       - any `spec_url`, `draft_url`, `plan_url`, `linked_pr` properties
    3. **Classify stage** using group + regex on option name:
       - `group=to_do` AND option matches `/idea|draft|skel+ton|review/i` → `stage=not-ready`
       - `group=to_do` AND option matches `/pending|ready|approved|queued/i` → `stage=ready-to-code`
       - `group=in_progress` AND option matches `/implementing|in[- ]?progress|wip|coding/i` → `stage=implementing`
       - `group=in_progress` AND option matches `/audit|verify|qa/i` → `stage=auditing`
       - `group=complete` AND option matches `/implemented|done|shipped|merged/i` → `stage=done`
       - option matches `/external|archive|wontfix|won'?t[- ]?do/i` → `stage=out-of-scope`
       - **On regex miss**: return `stage=unknown` with raw option for caller's AskUserQuestion fallback
    4. **Log the rule that fired**: include `matched_by: group=<g>, regex=<pattern>` in the report

    **Report**
    **[IMPORTANT]** Return the following YAML (<1000 tokens):

    ```yaml
    status: success|failure
    summary: 'Resolved Notion ticket <title> (<stage>)'
    outputs:
      ticket:
        id: '...'
        title: '...'
        slug: '...'
        status_group: 'to_do|in_progress|complete'
        status_option: '<raw option>'
        status_stage: 'not-ready|ready-to-code|implementing|auditing|done|out-of-scope|unknown'
        matched_by: 'group=<g>, regex=<pattern>'
        spec_url: '...'
        draft_url: '...|null'
        plan_url: '...|null'
        linked_pr: '...|null'
    issues: []
    ```
    <<<

#### Phase 3: Review (Subagents)

**SKIPPED** — Classification is deterministic given the rules, and the report itself logs which rule fired for drift-surfacing.

#### Phase 4: Decision (You)

**What You Do**:

1. Parse the `ticket` block from the subagent report
2. **Error handling** — handle Notion/MCP failures explicitly:
   - **Notion 404 / page not found**: report `status=refused` with reason `notion_not_found`; jump to Step 12, do not create a worktree
   - **Notion auth / MCP unavailable**: report `status=refused` with reason `notion_unavailable`; jump to Step 12
   - **Malformed id** (not 32-hex after normalization): report `status=refused` with reason `invalid_id`; jump to Step 12
   - **Fetch transient error**: retry once; if second failure, treat as `notion_unavailable`
3. If `status_stage=unknown`: use `AskUserQuestion` to surface the raw option and let the user map it to a stage, or abort (→ `status=flagged`)
4. Cache the ticket for downstream steps
5. Mark the `resolve-ticket` todo as `completed`

### Step 2: Download Spec Bundle

**Step Configuration**:

- **Purpose**: Materialize a hard local copy of the Notion spec into `<repo>/.code-spec/<ticket.slug>/` BEFORE any coding can begin. This is a hard gate — if the root spec cannot be persisted locally, the skill MUST stop and refuse to dispatch any `coding:*` child. The only bypass is `--use-cache` with a pre-existing valid local bundle.
- **Input**: `ticket` (from Step 1), `--use-cache`, `--repo`
- **Output**: `spec_bundle` = `{ root_path, index_path, files[], cache_hit }`
- **Sub-skill**: `specification:sync-spec` (download); cache check is performed inline before delegation
- **Parallel Execution**: Delegated to sub-skill

#### Phase 1: Cache Check (You)

1. Compute `bundle_root = <repo>/.code-spec/<ticket.slug>/`
2. **Cache decision**:
   - **Cache-hit path**: If `--use-cache` AND `bundle_root/INDEX.md` exists AND `bundle_root/SPEC.md` exists (both files non-empty) → load `spec_bundle` from disk (`Read` INDEX.md, list files via `Glob`), set `cache_hit=true`, **skip Phase 2**. This is the only branch that may continue without a fresh Notion fetch.
   - **Cache-miss under --use-cache**: If `--use-cache` is set but the cache is incomplete (missing INDEX.md OR missing SPEC.md OR either is empty) → log a `cache_miss_fallthrough` notice and proceed to Phase 2 (sub-skill will wipe + re-download).
   - **Default path**: Otherwise → proceed to Phase 2. The sub-skill always wipes `<spec-path>` before downloading; no extra wipe is required here.
3. **Auto-write `<repo>/.code-spec/.gitignore`** containing a single line `*` if the file does not already exist, so bundles never accidentally get committed. Idempotent — never overwrite an existing user-managed gitignore. (Note: the sub-skill writes its own `.gitignore` at `<bundle_root>/.gitignore`; this parent-level one covers the whole `.code-spec/` directory across all slugs.)
4. Add TodoWrite `download-spec-bundle` → `in_progress`

#### Phase 2: Sub-Skill Invocation (You)

Skip this phase entirely if Phase 1 took the cache-hit path.

1. Use `Read` to load `/Users/alvis/Repositories/.claude/plugins/specification/skills/sync-spec/SKILL.md`
2. Invoke `specification:sync-spec` via the `Skill` tool with:
   - `notion_url_or_id`: `ticket.id`
   - `--spec-path`: `<bundle_root>` (i.e. `<repo>/.code-spec/<ticket.slug>`) — sync-spec is slug-agnostic; namespacing is implement-code's responsibility
3. Capture the sub-skill's report. Map `outputs.spec_bundle.spec_path` → `spec_bundle.root_path`. Set `spec_bundle.index_path = outputs.spec_bundle.index_path`, `spec_bundle.files = outputs.spec_bundle.files`, `spec_bundle.cache_hit = false`.

#### Phase 4: Decision (You)

This is the **hard gate** that guarantees a local spec hard copy exists before coding. No `coding:*` child may be dispatched unless this gate passes.

- **On sub-skill `status=refused` with reason `spec_bundle_unavailable` / `notion_not_found` / `notion_unavailable` / `invalid_id`**: report this skill's `status=refused` with the same reason (or `spec_bundle_unavailable` if the sub-skill returned a different upstream reason but the root SPEC.md is missing), jump to Step 12. Do NOT proceed to Step 3. Do NOT create a worktree. Do NOT dispatch any `coding:*` child.
- **On sub-skill `status=completed` with `issues[]` warnings** (some children/linked pages failed): the hard-copy guarantee is satisfied — warn, continue with what was fetched, surface the missing-children list in the final report.
- **On sub-skill `status=completed` with no warnings, OR cache hit**: cache `spec_bundle` for downstream steps; mark todo `completed`.
- **Verification before exit**: Before marking this step complete, `Read` (or `Bash test -s`) `<bundle_root>/SPEC.md` to confirm the hard copy actually exists on disk. If the file is missing despite a `completed` report, treat as refusal (`spec_bundle_unavailable`) and apply the rule above.

### Step 3: Mode Resolution

**Step Configuration**:

- **Purpose**: Select exactly one of seven modes based on the ticket stage and artifact presence
- **Input**: `ticket` from Step 1, plus filesystem presence of `DRAFT.md` / `PLAN.md` / code in repo
- **Output**: `mode` with one of `COMMIT_PLAN` | `PI_ITERATE` | `DRAFT_THEN_ASK` | `AUDIT_AND_COMPLETE` | `VERIFY_ONLY` | `FLAG_MISMATCH` | `REFUSE`
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

**What You Do**:

1. Read the ticket + detect local artifacts (`DRAFT.md`, `PLAN.md`, code presence) via `Glob`/`Bash` (read-only)
2. Apply the **Mode Resolution Matrix** below in order; the first match wins

**Mode Resolution Matrix** (apply top-down):

| # | Condition                                                                                                                                               | Mode                  |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| 1 | `status_stage=out-of-scope`                                                                                                                             | `REFUSE`              |
| 2 | `status_stage=not-ready` (e.g. group=to_do + Idea/Draft/Skeleton/Review)                                                                                | `REFUSE`              |
| 3 | `status_stage=done`                                                                                                                                     | `VERIFY_ONLY`         |
| 4 | `status_stage=ready-to-code` AND `PLAN.md` present AND `DRAFT.md` present                                                                               | `COMMIT_PLAN`         |
| 5 | `status_stage=ready-to-code` AND (`PLAN.md` missing OR `DRAFT.md` missing)                                                                              | `DRAFT_THEN_ASK`      |
| 6 | `status_stage=implementing` AND there is partial code + pending TODOs or failing tests                                                                  | `PI_ITERATE`          |
| 7 | `status_stage=auditing`                                                                                                                                 | `AUDIT_AND_COMPLETE`  |
| 8 | Ticket stage and local artifacts disagree (e.g. stage=done but code missing, or stage=not-ready but code landed)                                        | `FLAG_MISMATCH`       |
| 9 | `status_stage=unknown` after Step 1 fallback                                                                                                            | `FLAG_MISMATCH`       |

**Mode Semantics**:

- **COMMIT_PLAN**: Execute PLAN.md phases via `coding:draft-code` → `coding:write-code` → `coding:review` → `coding:commit`, one commit per PLAN phase
- **PI_ITERATE**: Partial implementation exists; dispatch `coding:complete-code` then `coding:fix` then `coding:review` then `coding:commit`
- **DRAFT_THEN_ASK**: No plan yet; refuse to code, print pointer to run `specification:plan-code` first, ask user whether to proceed with a lightweight draft
- **AUDIT_AND_COMPLETE**: Dispatch `coding:review` first, then `coding:complete-code` + `coding:fix` for gaps, then `coding:commit`
- **VERIFY_ONLY**: Ticket marked done; dispatch `coding:review` only, report any drift, no commits
- **FLAG_MISMATCH**: Emit a structured report to the user describing the mismatch and ask for resolution via `AskUserQuestion`; do not code
- **REFUSE**: Decline with a clear message citing stage + matched rule; no worktree, no dispatch

#### Phase 4: Decision (You)

1. Record selected `mode` and the exact matrix row that fired
2. If `REFUSE` or (`FLAG_MISMATCH` and user declines to override): jump to Step 12 with `status=refused|flagged`
3. Otherwise proceed to Step 4

### Step 4: Consistency Check

**Step Configuration**:

- **Purpose**: Cross-check Spec (Notion) ↔ DRAFT.md ↔ PLAN.md ↔ existing code to surface drift before any writes
- **Input**: `ticket`, local `DRAFT.md`/`PLAN.md`, repo code
- **Output**: `consistency_report` with `{spec_vs_draft, draft_vs_plan, plan_vs_code, drift_items[]}`
- **Sub-skill**: None
- **Parallel Execution**: No (single pass, read-only)

#### Phase 1: Planning (You)

1. Confirm Step 3 produced a non-terminal mode (not `REFUSE` / `FLAG_MISMATCH`); otherwise short-circuit
2. Locate `DRAFT.md` and `PLAN.md` in the repo (read-only `Glob`)
3. Use TodoWrite to add `consistency-check` todo as `pending` → `in_progress` on dispatch
4. Queue one read-only analyst subagent with the artifacts inline

#### Phase 2: Execution (Subagent)

Dispatch one read-only analyst subagent.

    >>>
    **ultrathink: adopt the Spec Consistency Analyst mindset**

    - You're a **Spec Consistency Analyst**:
      - **Read-Only**: Never edit files
      - **Diff-Centric**: Focus on items present in one artifact but not in the others
      - **Terse**: Report each drift item as a single line

    **[IMPORTANT]** Read `INDEX.md` first, then open only the files referenced in the pointer block. Do NOT re-fetch from Notion.

    **Assignment**
    Compare these artifacts:
    - Spec bundle root: `<spec_bundle.root_path>` — read `INDEX.md` first, then open only the pointer-list files; do NOT re-fetch from Notion
    - Spec pointer block (pre-computed by orchestrator from INDEX.md + SPEC.md headings):
        - `<bundle_root>/SPEC.md#Features`
        - `<bundle_root>/SPEC.md#Acceptance`
        - matching `<bundle_root>/children/*.md` headings (Features/Acceptance sections in child pages)
    - DRAFT.md — [path if present, else N/A]
    - PLAN.md — [path if present, else N/A]
    - Code under [repo path] matching Features slugs

    **Steps**

    1. Extract Features / Acceptance criteria from Spec
    2. Extract commit blueprints from DRAFT.md
    3. Extract phase → commit mapping from PLAN.md
    4. Grep/Glob code for symbols matching Features slugs
    5. Build a drift table: each row = one Feature with columns `spec | draft | plan | code` and a `status`:
       - `aligned`: present in all relevant artifacts
       - `missing_plan` / `missing_draft` / `missing_code` / `missing_spec`
       - `signature_drift`: signatures differ across artifacts

    **Report**

    ```yaml
    status: pass|warn|fail
    summary: 'N drift items across M features'
    outputs:
      consistency_report:
        spec_vs_draft: 'aligned|partial|missing'
        draft_vs_plan: 'aligned|partial|missing'
        plan_vs_code: 'aligned|partial|missing'
        drift_items:
          - feature: '<name>'
            status: 'aligned|missing_plan|missing_draft|missing_code|missing_spec|signature_drift'
            detail: '<one-liner>'
    issues: []
    ```
    <<<

#### Phase 4: Decision (You)

- If `consistency_report.status=fail` and mode is `COMMIT_PLAN` or `PI_ITERATE`: downgrade to `FLAG_MISMATCH` and re-enter Step 3
- Otherwise: proceed to Step 5 with the report attached

### Step 5: Features Cross-Check

**Step Configuration**:

- **Purpose**: Map each Spec Feature to a concrete code symbol (existing or planned) and record coverage
- **Input**: `consistency_report` + `ticket`
- **Output**: `features_coverage[]` with `{feature, target_symbol, target_file, status: covered|planned|missing}`
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

1. Receive `consistency_report` + `ticket` from Step 4
2. Extract the Features list from the spec body for the mapping subagent
3. Use TodoWrite to add `features-cross-check` todo as `pending` → `in_progress` on dispatch
4. Queue one read-only mapping subagent

#### Phase 2: Execution (Subagent)

Dispatch one read-only mapping subagent.

    >>>
    **ultrathink: adopt the Feature Mapping Specialist mindset**

    - Map each Spec Feature to one code symbol. If multiple candidates exist, prefer the closest-named exported symbol.

    **[IMPORTANT]** Read `INDEX.md` first, then open only the files referenced in the pointer block. Do NOT re-fetch from Notion.

    **Assignment**
    Spec bundle root: `<spec_bundle.root_path>`
    Features pointer list (pre-computed by orchestrator):
      - `<bundle_root>/SPEC.md#Features`
      - matching child page Features headings under `<bundle_root>/children/*.md`
    Repo root: [repo path]

    **Steps**

    1. For each Feature, `grep`/`glob` the repo for matching symbols
    2. Classify each feature:
       - `covered`: symbol exists and its shape matches Feature
       - `planned`: symbol referenced by DRAFT.md/PLAN.md only
       - `missing`: no match in any artifact

    **Report**

    ```yaml
    status: pass|partial|fail
    outputs:
      features_coverage:
        - feature: '<name>'
          target_symbol: '<name or null>'
          target_file: '<path or null>'
          status: 'covered|planned|missing'
    issues: []
    ```
    <<<

#### Phase 4: Decision (You)

- If any Feature is `missing` and mode is `COMMIT_PLAN`: warn and consider downgrade to `DRAFT_THEN_ASK`
- Attach `features_coverage` to the running context

### Step 6: Approval Gate

**Step Configuration**:

- **Purpose**: Single skippable user-approval gate after mode resolution and consistency reporting
- **Input**: `mode`, `consistency_report`, `features_coverage`, `ticket`, `skip_approval` flag
- **Output**: `approval` = `approved` | `declined` | `skipped`
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

1. If `--skip-approval` is set: record `approval=skipped` and proceed to Step 7
2. Otherwise compose a concise approval payload:
   - Ticket title + stage + matched rule
   - Selected mode + matrix row
   - Top 3 drift items (if any)
   - Planned child-skill chain for the mode
   - "Working Draft is treated as non-authoritative. Material deviations are logged to DEVIATIONS.md in the worktree. Trivial departures (JSDoc, inferred types, lint) are silent."
3. Call `AskUserQuestion` with a single question and options:
   - `Approve`: proceed with the chain
   - `Switch Mode`: let the user override to another mode (re-enters Step 3 Decision)
   - `Abort`: mark `status=refused`, jump to Step 12
4. `ExitPlanMode` is used for this single gate — no other gates downstream

#### Phase 4: Decision (You)

- `Approve` → proceed to Step 7
- `Switch Mode` → apply user's chosen mode, re-run Steps 4 + 5 if needed, re-enter this gate once
- `Abort` → jump to Step 12 with `status=refused`

### Step 7: Worktree Setup

**Step Configuration**:

- **Purpose**: Create an isolated git worktree so all child edits happen on a dedicated branch
- **Input**: `ticket.slug`, `--repo`, `--branch`, `--dry-run`, `mode`
- **Output**: `worktree_path`, `branch_name`
- **Sub-skill**: `superpowers:using-git-worktrees`
- **Parallel Execution**: No

#### Execute Sub-Skill (You)

When you reach this step:

1. If `--dry-run=true` OR `mode` ∈ {`VERIFY_ONLY`, `REFUSE`, `FLAG_MISMATCH`}: **skip** worktree creation — no worktree is created, no worktree path is returned, and execution proceeds to Step 8 using the existing repo path in read-only dispatch configuration
2. Otherwise, resolve sub-skill path and invoke `superpowers:using-git-worktrees` with:
   - `repo`: `--repo` or current working directory
   - `branch`: `--branch` or `feat/impl-<ticket.slug>`
   - `base`: the repo's default branch (detected via `git rev-parse --abbrev-ref origin/HEAD`)
3. Record the returned `worktree_path` + `branch_name` for all downstream child dispatches
4. **Scaffold `<worktree_path>/DEVIATIONS.md`** with the header template below. Skip this write when the worktree step itself is skipped (`--dry-run`, `VERIFY_ONLY`, `REFUSE`, `FLAG_MISMATCH`):

    ```markdown
    # Deviations from Notion Draft

    **Spec**: <ticket.title> (<ticket.id>)
    **Worktree**: <worktree_path>
    **Branch**: <branch_name>
    **Draft source**: <notion spec URL>

    Entries below are material departures from the draft discovered during implementation. Trivial differences (JSDoc, inferred types, lint/format) are not recorded.

    ---
    ```

5. Update TodoWrite: add todos for the planned `coding:*` chain for the selected mode

### Step 8: Execute Mode

**Step Configuration**:

- **Purpose**: Dispatch the mode-specific chain of `coding:*` children inside the worktree
- **Input**: `mode`, `worktree_path`, `branch_name`, `ticket`, `consistency_report`, `features_coverage`
- **Output**: `child_dispatch_log[]`, `commits_landed[]`
- **Sub-skill**: One or more of `coding:draft-code`, `coding:write-code`, `coding:complete-code`, `coding:fix`, `coding:review`, `coding:commit`, `coding:handover`
- **Parallel Execution**: No (children run sequentially; they may internally parallelize)

#### Phase 1: Planning (You)

0. **Pre-coding hard-copy gate**: Before selecting any child chain, verify `<spec_bundle.root_path>/SPEC.md` still exists and is non-empty (`Bash test -s`). This is a defence-in-depth check against any path that could have skipped Step 2's gate (e.g. injected mode override, race with manual cleanup). If missing, set `status=refused` with reason `spec_bundle_missing_at_dispatch`, do NOT dispatch any child, jump to Step 12.

Select the child chain from the mode:

- **COMMIT_PLAN** (per PLAN phase):
  1. `coding:draft-code` — scaffold skeletons for the phase
  2. `coding:write-code` — TDD-complete the phase
  3. `coding:review` — MUST pass before commit
  4. `coding:commit` — atomic commit for the phase
- **PI_ITERATE**:
  1. `coding:complete-code` — finish TODOs
  2. `coding:fix` — fix broken tests/lint
  3. `coding:review`
  4. `coding:commit`
- **DRAFT_THEN_ASK**:
  1. Print pointer to `specification:plan-code`
  2. If user opts into lightweight draft: `coding:draft-code` only, then `coding:handover`
- **AUDIT_AND_COMPLETE**:
  1. `coding:review` (baseline)
  2. `coding:complete-code` for gaps
  3. `coding:fix`
  4. `coding:review` (final)
  5. `coding:commit`
- **VERIFY_ONLY**:
  1. `coding:review` — no commits
- **FLAG_MISMATCH** / **REFUSE**: no children dispatched; skip to Step 11

Update TodoWrite with one todo per dispatched child.

#### Phase 2: Execution (Sub-Skills)

For each child in the chain, in order:

1. Load the child SKILL.md via `Read`
2. Invoke via `Skill` tool with a minimal payload:
   - `worktree_path`
   - `branch_name`
   - `ticket_summary` (title + slug)
   - `deviation_policy` (the block below, verbatim, embedded in every `coding:*` dispatch payload)
   - Child-specific inputs (e.g. plan phase, drift items, features to complete)

   **Deviation policy block** (include verbatim in every dispatch):

    ```markdown
    ## Deviation Policy

    The Working Draft / AI Coder Prompt / PLAN phase you are implementing is a DRAFT and may contain errors. If you encounter any of the following while implementing, DEVIATE and proceed, appending an entry to `<worktree>/DEVIATIONS.md`:

    - Missing or wrong dependency (package not installed, wrong version, replaced)
    - Wrong integration assumption (API signature, event name, schema field, import path, module layout differs from what the draft assumes)
    - Standard violation (draft conflicts with `plugins/<plugin>/constitution/standards/`)
    - Architectural conflict (draft's structure doesn't fit the repo's existing pattern)
    - Symbol the draft references no longer exists

    SKIP logging for trivial differences:

    - Auto-added JSDoc the draft omitted
    - Inferred type annotations the draft left implicit
    - Lint / formatter-driven whitespace or import ordering
    - Casing adjustments to match local conventions
    - Obvious prose typos in the draft

    **DEVIATIONS.md entry format** (append, never rewrite existing entries):

        ### D-<N>: <short title>
        - **When**: <step name / commit label>
        - **Draft said**: <one-line summary>
        - **What I did instead**: <one-line summary>
        - **Reason**: missing-dep | wrong-integration | standard-violation | arch-conflict | stale-symbol
        - **Impact on spec**: none | surface-change | behavior-change
        - **Severity**: minor | major | blocking

    DO NOT refuse the task over a deviation. DO NOT ask the user mid-implementation for trivial choices. Record and proceed.
    ```

3. **[IMPORTANT]** You do NOT call `Write`/`Edit` yourself — you rely on the child's tool grants
4. Capture each child's status + summary into `child_dispatch_log`
5. On `coding:review` failure: run `coding:fix` then re-run `coding:review`, max 3 iterations
6. On `coding:commit` success: append SHA to `commits_landed`
7. **After the last code commit**, dispatch one extra `coding:commit` scoped to `DEVIATIONS.md` with message `chore(deviations): log draft departures for <ticket.slug>`. **Skip** this trailing commit when any of the following hold:
   - The file ended header-only (no `D-N` entries appended)
   - Mode is `VERIFY_ONLY` or `DRAFT_THEN_ASK` (no commits land)
   - `--dry-run` is set

#### Phase 4: Decision (You)

- All children succeed → Step 9
- Any child fails twice in a row → dispatch `coding:handover` to capture state, mark `status=partial`, jump to Step 11

### Step 9: Post-Change Re-Check

**Step Configuration**:

- **Purpose**: Re-run Consistency + Features cross-check against the newly-committed code
- **Input**: `worktree_path`, `ticket`, `commits_landed`
- **Output**: `post_consistency_report`, `post_features_coverage`
- **Sub-skill**: None
- **Parallel Execution**: No

#### Phase 1: Planning (You)

1. Confirm `commits_landed` is non-empty and mode is not `VERIFY_ONLY` / `DRAFT_THEN_ASK`; otherwise skip
2. Use TodoWrite to add `post-change-recheck` todo as `pending` → `in_progress` on dispatch
3. Queue one analyst subagent re-running the Step 4/5 pattern against the post-commit worktree

#### Phase 2: Execution (Subagent)

Dispatch the same analyst pattern as Step 4 and Step 5, but against the post-commit worktree state. Skip entirely when mode is `VERIFY_ONLY` (Step 4/5 already covered it) or `DRAFT_THEN_ASK` (no commits).

After the analyst runs, **additionally read `<worktree_path>/DEVIATIONS.md`** and reconcile it against the post-commit reports:

- For each `D-N` with `Impact on spec: surface-change` or `behavior-change` → confirm the matching spec Feature is still present in `post_features_coverage` with status `covered`. Flag any mismatch by appending a row to `post_consistency_report.drift_items` (status `signature_drift` or `missing_code` as appropriate, detail citing `D-N`).
- For each `D-N` with `Severity: blocking` → immediately set `status=partial` and surface the entry in the final report.

#### Phase 4: Decision (You)

- Any remaining `missing_code` on a spec Feature → warn in final report and set `status=partial`
- Any blocking deviation surfaced above → set `status=partial`
- Otherwise set `status=completed`
- Always run **Step 9a (Stack-Aware Sizing & Restack Trigger)** before advancing to Step 10, regardless of `status`. Stack delegation is independent of consistency outcome — a clean partial still warrants slicing if oversized, and a completed run still warrants restack if it semantically alters a lower PR's contract.

### Step 9a: Stack-Aware Sizing & Restack Trigger

**Step Configuration**:

- **Purpose**: After `commits_landed` are produced, decide whether to delegate to `coding:stack-code` (split/create mode for oversized changes, restack mode for semantic upstream impact). The orchestrator NEVER runs `jj split` / `jj bookmark set` / `gh pr create` directly — every stack mutation is dispatched through `coding:stack-code` so its standards (`GIT-PR-STACK-01..06`, `GIT-PR-SIZE-01..04`) and detect-mode thresholds remain the single source of truth.
- **Input**: `worktree_path`, `branch_name`, `commits_landed`, post-commit diff stats, `ticket.slug`
- **Output**: `stack_dispatch` = `{ dispatched: true|false, mode: split|create|restack|null, slug: <slug>|null, prs: [...] }`
- **Sub-skill**: `coding:stack-code` (only when triggered)
- **Parallel Execution**: No

**⚠️ SKIP LIST**: Skip this step entirely when any of the following hold (record `stack_dispatch.dispatched=false` with one-line reason):

- `mode ∈ {VERIFY_ONLY, DRAFT_THEN_ASK, REFUSE, FLAG_MISMATCH}`
- `--dry-run` is set
- `commits_landed` is empty

#### Phase 1: Planning (You)

1. **Compute aggregate change size** against the worktree base branch (read-only, via `Bash` `jj diff --stat` or `git diff --stat <base>...HEAD`):
   - `changed_files`: total files touched across `commits_landed`
   - `loc_delta`: total added + removed lines
   - `domains_touched`: distinct top-level path prefixes / package roots
2. **Read thresholds from `coding:stack-code`** (do not hardcode here): the detect-mode heuristic table in `plugins/coding/skills/stack-code/SKILL.md` Step 2 is authoritative — currently >5 changed files OR >300 LOC diff OR multiple loosely-coupled domains. If that file's thresholds drift, this skill picks up the new values automatically.
3. **Detect open stack**: presence of `<repo>/.jj/stack-code/<slug>.json` state file OR existing bookmarks matching `<slug>/NN-<scope>` per `GIT-PR-STACK-01`.
4. **Classify the trigger**:
   - **Size-trigger** → dispatch `coding:stack-code` in `split` mode (existing chunky branch) or `create` mode (planned outline) per stack-code's own auto-detect; orchestrator does not pre-pick.
   - **Restack-trigger** → an open stack exists AND the landed code **semantically modifies a symbol/contract that a lower (earlier-in-order) PR in the stack establishes or relies on**. Apply this judgement per symbol, not per file:
     - Trigger: signature change of an exported symbol the lower PR consumes; behavior change in a shared helper a lower PR's tests assume; schema/contract change a lower PR's migration depends on.
     - Do NOT trigger: incidental file overlap (formatting, lint, unrelated co-edit in same file), purely additive code that lower PRs do not reference.
   - **Both triggers fire** → `split` (or `create`) takes precedence; restack is implicit in the new stack layout.
   - **Neither fires** → small, single-domain change; continue with the existing single-commit / single-PR path. Record `stack_dispatch.dispatched=false`.
5. Update TodoWrite: add `stack-aware-sizing` todo set to `in_progress` when a trigger fires.

#### Phase 2: Execution (Sub-Skill)

When a trigger fires, dispatch `coding:stack-code` exactly once via the `Skill` tool:

1. Load `/Users/alvis/Repositories/.claude/plugins/coding/skills/stack-code/SKILL.md` via `Read`
2. Invoke with a minimal payload:
   - `--slug <ticket.slug>`
   - For size-trigger: let `coding:stack-code`'s `detect-mode.py` pick `create` vs `split`; do not force `--mode` unless the user has already approved a specific path
   - For restack-trigger: invoke `scripts/restack.py --slug <ticket.slug>` per stack-code Step 8 (Ongoing Operations)
   - Pass `worktree_path` and `branch_name` so stack-code operates inside the same worktree
3. Capture stack-code's `outputs.mode`, `outputs.slug`, and `outputs.prs[]` from its YAML report into `stack_dispatch`
4. Append the dispatch entry to `child_dispatch_log` so Step 12 surfaces it alongside the `coding:*` chain

#### Phase 4: Decision (You)

- `stack-code` reports `status=completed` → record `stack_dispatch` and proceed to Step 10
- `stack-code` reports `status=failed|partial` → mark this skill's final `status=partial`, attach the stack-code report to the running context, still proceed to Step 10 (paper-only review remains valuable)
- Mark `stack-aware-sizing` todo as `completed`

### Step 10: Thought-Experiment Gate

**Step Configuration**:

- **Purpose**: Paper-only integration validation against the landed code; catches silent integration breakage that tests missed by tracing every intended usage through the real file graph.
- **Input**: `worktree_path`, `spec_bundle.root_path` plus a pre-computed pointer list of all Usage/Example/Scenario/Verification sections discovered across `SPEC.md` + `children/*.md`, `commits_landed`, `<worktree_path>/DEVIATIONS.md`
- **Output**: `thought_experiment_report` with per-usage verdicts
- **Sub-skill**: None — single `Task` dispatch. The subagent **MUST** use `subagent_type=general-purpose`, `model=opus` (never Sonnet, never Haiku, no fallback), and **maximum reasoning effort / thinking budget**. These settings are mandatory whenever this step runs; do not downgrade for cost, latency, or quota reasons. If opus is unavailable, fail the step with `status=partial` and an advisory rather than substituting a weaker model.
- **Parallel Execution**: No — one sequential deep pass

**⚠️ IMPORTANT SKIP LIST**: Skip this step entirely when any of the following hold:

- `mode ∈ {VERIFY_ONLY, DRAFT_THEN_ASK, REFUSE, FLAG_MISMATCH, AUDIT_AND_COMPLETE}`
- `--dry-run` is set
- `commits_landed` is empty

`AUDIT_AND_COMPLETE` is in the skip list because the mode's premise is that the draft is no longer authoritative — tracing spec→code loses meaning once the audit itself has overridden the draft.

#### Phase 1: Planning (You)

1. Evaluate the skip list. If any condition holds, record `thought_experiment_report.status=skipped` with a one-line reason and proceed to Step 11.
2. Otherwise assemble the inputs bundle: `spec_bundle.root_path` + pre-computed pointer list of Usage/Example/Scenario/Verification sections, absolute `worktree_path`, `DEVIATIONS.md` path, and the list of `commits_landed` shas for context.
3. Update TodoWrite: add a `thought-experiment` todo set to `in_progress`.

#### Phase 2: Execution (Subagent)

Dispatch a single `Task` with `subagent_type=general-purpose`, `model=opus`, maximum reasoning budget. Embed the prompt below verbatim.

    >>>
    (Dispatched on model=opus with maximum reasoning effort. This is the only place in the skill that guarantees deep paper-only integration review; no other step compensates if you under-think here.)

    You are the Thought-Experiment Reviewer. Apply maximum reasoning effort. Do NOT run code, run tests, or edit files — read only.

    **[IMPORTANT]** Read `INDEX.md` first, then open only the files referenced in the pointer block. Do NOT re-fetch from Notion.

    **Inputs**
    - Spec bundle root: `<spec_bundle.root_path>` (read `INDEX.md` first, then open only pointer-list files)
    - Spec pointer list (pre-computed by orchestrator): every Usage / Example / Scenario / PI Verification section discovered across `<bundle_root>/SPEC.md` + `<bundle_root>/children/*.md`
    - Worktree: <worktree_path> (use Read / Grep / Glob)
    - Deviations log: <worktree_path>/DEVIATIONS.md

    **Task**
    Identify every INTENDED USAGE in the spec (one usage = one externally-observable way the implementation is meant to be called or composed). For each:
    1. Trace it step-by-step through the actual landed code — imports, call graph, return shapes, error paths, async boundaries
    2. Verify the public surface the usage touches exists, has the right signature, and composes correctly with its dependencies
    3. Check every deviation in DEVIATIONS.md has been absorbed — the usage must still work despite the departure from draft
    4. Cross-check against adjacent usages to catch conflicting assumptions

    **Per-usage verdict**: `works` | `broken` | `unclear` — with 2-3 sentences of trace reasoning. If `broken`, cite `file:line`.

    **Overall verdict**: `pass` (all `works`) | `partial` (any `unclear`, no `broken`) | `fail` (any `broken`).

    **Report (YAML, <3000 tokens)**:

        status: pass|partial|fail
        outputs:
          thought_experiment_report:
            usages:
              - id: U-1
                description: '<one-liner>'
                verdict: works|broken|unclear
                trace: '<2-3 sentences>'
                cite: '<file:line or null>'
            deviations_absorbed: true|false
            summary: '<paragraph>'
        issues: []
    <<<

#### Phase 3: Review (Subagents)

**SKIPPED** — This step is itself the review layer; its output feeds Step 11 and Step 12 directly.

#### Phase 4: Decision (You)

- `status=pass` → proceed to Step 11 with `status=completed`
- `status=partial` → final `status=partial`, list unclear usages in the final report, do not block
- `status=fail` → append `D-<N>: thought-experiment-blocking / severity=blocking` to `DEVIATIONS.md`, final `status=partial`, recommend rerun after fix, proceed to Step 11
- Always attach the full `thought_experiment_report` to running context so Step 12 can emit it

### Step 11: Skill Self-Verify

**Step Configuration**:

- **Purpose**: Run `governance:verify-skill` against `implement-code` itself in full mode to keep the skill healthy
- **Input**: Path to this SKILL.md
- **Output**: `verification_report` from verify-skill
- **Sub-skill**: `governance:verify-skill`
- **Parallel Execution**: No

#### Execute Sub-Skill (You)

1. Load `/Users/alvis/Repositories/.claude/plugins/governance/skills/verify-skill/SKILL.md` via `Read`
2. Invoke with:
   - `skill_path`: `/Users/alvis/Repositories/.claude/plugins/specification/skills/implement-code/SKILL.md`
   - `mode`: `full`
   - `fix`: `false`
3. Capture the structural + functional + trigger results
4. If verification fails structurally: attach the report to the final completion yaml so the user can dispatch `governance:update-skill`

### Step 12: Skill Completion

**Report the skill output as specified**:

```yaml
skill: implement-code
status: completed | partial | refused | flagged | dry_run
# Refusal reasons (when status=refused):
#   - notion_not_found
#   - notion_unavailable
#   - invalid_id
#   - spec_bundle_unavailable          # Step 2 failed to persist root SPEC.md locally
#   - spec_bundle_missing_at_dispatch  # Step 8 pre-dispatch gate found SPEC.md missing
#   - approval_aborted
outputs:
  ticket:
    id: '<id>'
    title: '<title>'
    slug: '<slug>'
    status_group: 'to_do|in_progress|complete'
    status_option: '<raw>'
    status_stage: 'not-ready|ready-to-code|implementing|auditing|done|out-of-scope|unknown'
    matched_by: 'group=<g>, regex=<pattern>'
  spec_bundle:
    root_path: '<abs path>'
    cache_hit: true|false
    files_count: <N>
  mode:
    selected: 'COMMIT_PLAN|PI_ITERATE|DRAFT_THEN_ASK|AUDIT_AND_COMPLETE|VERIFY_ONLY|FLAG_MISMATCH|REFUSE'
    matrix_row: <#>
  worktree:
    path: '<abs path or null>'
    branch: '<name or null>'
  consistency_report: { ... }
  features_coverage: [ ... ]
  child_dispatch_log:
    - skill: 'coding:<name>'
      status: 'pass|fail|partial'
      summary: '<one-liner>'
  commits_landed:
    - sha: '<sha>'
      message: '<conventional message>'
  stack:
    dispatched: true|false
    mode: 'split|create|restack|null'
    slug: '<slug>|null'
    prs:
      - number: NN
        bookmark: '<slug>/NN-<scope>'
        title: '<conventional-commit title>'
        url: '<gh pr url>'
        base: '<prev_bookmark_or_main>'
  post_consistency_report: { ... }
  post_features_coverage: [ ... ]
  deviations:
    - id: D-1
      title: '<short>'
      reason: 'missing-dep|wrong-integration|standard-violation|arch-conflict|stale-symbol'
      severity: 'minor|major|blocking'
  thought_experiment_report:
    status: 'pass|partial|fail'
    usages_works: <N>
    usages_broken: <N>
    usages_unclear: <N>
    summary: '<paragraph>'
  verification_report:
    status: 'pass|fail|partial'
    structural: 'pass|fail'
    functional: { pass_rate: 0.XX, test_cases: N }
    trigger: { trigger_rate: 0.XX, false_positive_rate: 0.XX }
summary: |
  Implementation of ticket <slug> resolved to mode <mode> and landed <N> commits
  on branch <branch_name>. Spec Features coverage: <X>/<Y>. Skill self-verify: <pass|fail>.
  Thought experiment: <pass|partial|fail> (<W>/<B>/<U> works/broken/unclear).
  Stack: <dispatched=true|false> [mode=<split|create|restack> slug=<slug> prs=<N>].
```

> **Summary guidance**: When `thought_experiment_report.status != skipped`, the `summary:` string MUST mention that the thought experiment ran on **opus with maximum reasoning effort** — this is how the reader confirms the mandatory opus/max-effort dispatch was honoured, not downgraded. Omit the opus note only when `status=skipped` (AUDIT_AND_COMPLETE, VERIFY_ONLY, DRAFT_THEN_ASK, REFUSE, FLAG_MISMATCH, `--dry-run`, or empty `commits_landed`).

## 4. EXAMPLES

### Example 1: Approved spec with DRAFT + PLAN → COMMIT_PLAN

Invocation:

```
/specification:implement-code https://www.notion.so/<workspace>/296b2572f788804094e4fa180444c26d
```

Fetched ticket:

- `status_group=to_do`, `status_option=Pending Implementation`, regex `/pending|ready|approved/i` fires → `stage=ready-to-code`
- DRAFT.md + PLAN.md both exist in repo

Mode matrix row 4 fires → `COMMIT_PLAN`. After approval, dispatches `coding:draft-code` → `coding:write-code` → `coding:review` → `coding:commit` per PLAN phase.

### Example 2: Notion ticket at `Status=Review`

Invocation:

```
/specification:implement-code cf2d93f918b3435f8618956c4c0988e9
```

- `status_group=to_do`, `status_option=Review`, regex `/idea|draft|skel+ton|review/i` fires → `stage=not-ready`
- Mode matrix row 2 → `REFUSE` with message: "Ticket at stage `not-ready` (group=to_do, matched `/idea|draft|skel+ton|review/i`). Re-run after approval or use `specification:plan-code` first."

### Example 3: Dry run for an implementing ticket

```
/specification:implement-code <id> --dry-run
```

- `stage=implementing` → matrix row 6 → `PI_ITERATE`
- `--dry-run` skips Steps 7–10
- Still runs Step 11 (`governance:verify-skill`)
- Final `status=dry_run` with `child_dispatch_log=[]` and `commits_landed=[]`

### Example 4: Cache hit with --use-cache

```
/specification:implement-code <id> --use-cache
```

- Cache decision: `<repo>/.code-spec/<slug>/INDEX.md` exists → load bundle from disk, set `cache_hit=true`, skip Phase 2
- Subsequent steps proceed against the existing bundle without any Notion fetch
- Final report shows `spec_bundle.cache_hit=true`
