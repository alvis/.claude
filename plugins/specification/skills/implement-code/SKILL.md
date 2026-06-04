---
name: implement-code
description: Execute approved specification-notion tickets end-to-end by resolving ticket intent, committing or iterating on plans, and dispatching coding:* child skills to write, verify, and commit code in place against the current working copy. When the dynamic Workflow tool is available it runs implementation as a fanout + adversarial advisor-verification + loop-until-done workflow, falling back to sequential dispatch otherwise. Use when asked to implement a Notion ticket, take a spec to code, kick off work on a specification URL/ID, turn an approved plan into shipped commits, audit and finish a partial implementation tracked in Notion, or run a spec implementation as an ultracode/dynamic workflow.
model: opus
context: fork
agent: general-purpose
allowed-tools: Read, Write, Grep, Glob, Bash, Task, Skill, Workflow, TodoWrite, AskUserQuestion, ExitPlanMode
argument-hint: <notion-url-or-id> [--repo=<path>] [--dry-run] [--skip-approval] [--use-cache]
---

# Implement Code

## 1. INTRODUCTION

### Purpose & Context

**Purpose**: Turn an approved Notion specification ticket into landed code by resolving ticket status, selecting the right execution mode (commit-plan, iterate, draft-then-ask, audit-and-complete, verify-only, flag-mismatch, or refuse), and orchestrating coding:* child skills in place against the current working copy, delegating all jj organization to `coding:commit` (with `--create-pr` when stacked PRs are required). Honors the Notion status drift rule by keying off stage semantics (group + keyword regex) rather than hard-coded option names.

**When to use**:

- When the user supplies a Notion URL/ID and asks to implement, build, ship, or execute the spec
- When an approved plan-code output (DRAFT.md + PLAN.md) is ready to be translated into commits
- When a previously-started implementation needs to be audited and finished against its spec
- When a Notion ticket status signals readiness for coding (group=to_do/in_progress with ready/approved/implementing keywords) and the user wants work to begin
- Stack-aware: detects when landed changes exceed the stacked-PR size thresholds (or semantically modify code an open lower PR depends on) and delegates slicing/restacking to `coding:commit --create-pr` rather than committing flat

**Prerequisites**:

- `notion-sync` CLI on PATH with `NOTION_TOKEN` exported (used by `specification:sync-spec` and any direct ticket-status reads)
- Local git repository (current directory or `--repo=<path>`) with the target spec's codebase
- `specification:sync-spec` available for the Step 2 spec bundle download (hard-gated)
- `coding:*` child skills available (draft-code, write-code, complete-code, fix, review, commit, handover)
- `coding:commit` (with `--create-pr`) available for size-triggered slicing and upstream-restack delegation (thresholds documented in `references/stack-aware-sizing.md`)

### Your Role

You are an **Implementation Director** who orchestrates spec-to-code delivery like an engineering manager coordinating planning leads and coding specialists, never writing or editing production code directly — every production `Write`/`Edit` call happens inside dispatched `coding:*` children. **Coherence Mandate.** Every edit must produce one continuous, deliberate work. Rewrite over restructure, restructure over integrate, never append. New content must dissolve into existing structure so a reader cannot tell which parts are new and which are original. Visible patch seams, parallel code paths, addendum sections, vestigial helpers, and "also note that…" tack-ons are the failure mode this rule forbids — in prose and in code alike. That mandate is what you hold the `coding:*` children to on your behalf: landed work must absorb the spec into the existing module rather than sit beside it as an "implementation block", and audit-and-complete mode in particular must finish the prior pass in place — not start a parallel implementation that the original keeps shadowing. Your management style emphasizes:

- **Strategic Delegation**: Route ticket resolution, plan work, in-place workspace prep, and coding passes to the right specialist subagents
- **Mode-Driven Coordination**: Pick exactly one execution mode per invocation and keep the downstream dispatch aligned to it
- **Quality Oversight**: Gate code landing on `coding:review` passing and the spec-alignment review reporting clean
- **Decision Authority**: Make single-gate go/no-go calls (one approval gate after mode resolution) and enforce refusal when the ticket isn't ready
- **Zero Direct Writes (one carve-out)**: You never hold the pen on source files — your outputs are decisions, dispatches, and reports. The **sole** file you may `Write` directly is `<repo_path>/DEVIATIONS.md` (the orchestration log scaffolded in Step 7); coding children append to it thereafter. `.code-spec/*.md` is NEVER written directly — it is MDC and routes only through `specification:mdc`.

## 2. SKILL OVERVIEW

### Skill Input/Output Specification

#### Required Inputs

- **Notion URL or ID**: The Notion page identifier for the specification ticket (full URL or bare 32-char ID). Resolves to a page in the specification database (e.g. `292b2572f78880fe95b9fdc8daeb862f`).

#### Optional Inputs

- **--repo=<path>**: Absolute path to the target repository. Defaults to the current working directory.
- **--dry-run**: Plan and report only. Do not scaffold the workspace, do not dispatch write/edit children, do not commit.
- **--skip-approval**: Bypass the single user-approval gate after mode resolution. Intended for trusted automation contexts.
- **--use-cache**: Reuse an existing `.code-spec/<ticket.slug>/` bundle if it contains any `*.md` files (i.e. a prior `notion-sync pull` left flat `{kebab-title}-{32hex-id}.md` files behind). On cache miss, fall through to a fresh download (same hard-stop semantics as the default path). Default behavior wipes and re-downloads on every invocation.

#### Expected Outputs

- **Mode Decision**: The selected execution mode (`COMMIT_PLAN` | `PI_ITERATE` | `DRAFT_THEN_ASK` | `AUDIT_AND_COMPLETE` | `VERIFY_ONLY` | `FLAG_MISMATCH` | `REFUSE`) with the group + regex rule that fired
- **Workspace Info**: confirmed in-place `repo_path` (current working copy) + captured `base_rev`
- **Consistency & Coverage Report**: Spec ↔ DRAFT ↔ PLAN ↔ Code drift table plus the Spec Feature → code-symbol coverage map (single combined cross-check)
- **Child Dispatch Log**: Ordered list of `coding:*` skills dispatched with input summary and exit status for each
- **Commits Landed**: Array of commit SHAs and messages produced by `coding:commit` dispatches
- **Git-Worktree Relocation**: `{ detected, action }` — whether landed work was found inside a linked `git worktree` and the user's relocation decision
- **Final Status**: `completed` | `partial` | `refused` | `flagged` | `dry_run`

#### Data Flow Summary

The skill fetches the Notion ticket, classifies its status by Notion `status` group (`to_do` | `in_progress` | `complete`) combined with keyword regex on the option name, resolves one of seven modes from the Mode Resolution matrix, runs a single combined Consistency + Features cross-check (Step 4), then critically reviews the spec + current code for flaws and major architectural deviations (Step 5) — resolving each with the user and recording the decision back into the local spec via `specification:mdc`. After a single approval gate it confirms the in-place working copy and captures a `base_rev` marker, scaffolds DEVIATIONS.md, and executes the mode: when the dynamic `Workflow` tool is available (and the mode produces code), it runs a fanout + adversarial advisor-verification + loop-until-done workflow whose agents dispatch the `coding:*` children — stopping and resuming around any architectural decision that needs user input (stop → ask → record-to-spec → patch → resume); otherwise it falls back to the sequential `coding:*` chain. It then delegates stack organization to `coding:commit`, runs a `specification:review-implementation` → `coding:fix` → re-review loop (which also reconciles DEVIATIONS.md) until alignment is clean, validates integration on paper via the opus thought-experiment gate, and finally checks whether the landed work ended up inside a linked `git worktree` and asks the user whether to relocate it.

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
[Step 1: Resolve Ticket] ───────────→ (notion-sync pull <id> --follow-children --follow-links + status classify)
   |                                    group + keyword regex → stage
   v
[Step 2: Download Spec Bundle] ─────→ (sub-skill specification:sync-spec → .code-spec/<slug>/)
   |                                    HARD GATE: stop if root spec file (filename suffix = ticket.id) cannot be saved
   |                                    --use-cache short-circuits sub-skill when bundle dir already has any *.md files
   v
[Step 3: Mode Resolution] ──────────→ (Apply Mode Matrix → 1 of 7 modes + Applicability Matrix)
   |
   v
[Step 4: Consistency + Features] ───→ (one analyst: Spec ↔ DRAFT ↔ PLAN ↔ Code drift + Feature → symbol coverage)
   |
   v
[Step 5: Soundness Review] ─────────→ (Critique spec + current code for flaws / arch deviations)
   |                                    capability-gated fanout + adversarial verify (else 1 subagent)
   |                                    per blocking issue → AskUserQuestion → record to local spec
   |                                    via specification:mdc (MDC bundle edited ONLY through mdc)
   |                                    skipped per Applicability Matrix
   v
[Step 6: Approval Gate] ────────────→ (AskUserQuestion — skipped if --skip-approval)
   |
   v ─── approved or skipped ───
[Step 7: Workspace Setup] ──────────→ (in place; capture base_rev; Write-scaffold DEVIATIONS.md)
   |
   v
[Step 8: Execute Mode] ─────────────→ (Mechanism gate — see references/execute-workflow.md)
   |   • Mechanism A (Workflow available + COMMIT_PLAN/PI_ITERATE/AUDIT_AND_COMPLETE + not --dry-run):
   |       ultracode it → fanout impl agents (dispatch coding:write/complete/fix)
   |       → adversarial advisor verify → loop-until-done
   |       → on a needed decision the run STOPS; main thread asks, records to spec
   |         via specification:mdc, then RESUMES (resumeFromRunId) — stop→ask→patch→resume
   |   • Mechanism B (fallback): sequential coding:* chain (references/modes.md), asks inline
   v
[Step 9: Stack-Aware Sizing] ───────→ coding:commit --create-pr (stacked-PR or restack)
   |        • large change (>5 files OR >300 LOC OR multi-domain) — diffed against base_rev
   |        • OR open stack detected AND landed code semantically alters a lower PR's contract
   |        • orchestrator NEVER calls `jj split` / `gh pr create` directly — always delegates
   |
   v
[Step 10: Spec-Alignment Review Loop] ──→ specification:review-implementation
   |        • on P0/P1 alignment findings → coding:fix → re-review (max 3 iterations)
   |        • reconciles DEVIATIONS.md (behavior-change/blocking → P0/partial)
   v
[Step 11: Thought-Experiment Gate] ──→ (opus + max effort, mandatory, paper-only)
   |
   v
[Step 12: Git-Worktree Relocation Check] ──→ (AskUserQuestion if linked git worktree detected)
   |
   v
[Step 13: Completion Report]
   |
   v
[END]

Legend:
═══════════════════════════════════════════════════════════════════
• LEFT COLUMN: You orchestrate (no direct writes, save the DEVIATIONS.md scaffold)
• RIGHT SIDE: Subagents / sub-skills execute tasks
• ARROWS (───→): You dispatch work
• DECISIONS: You select mode + approve/abort based on reports
• Skill is LINEAR: Step 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13
• Step 5 is a pre-implementation verification gate: critiques the spec + code and locks in user decisions BEFORE coding
• Step 8 is capability-gated: Mechanism A (dynamic Workflow) when available + code-producing mode, else Mechanism B (sequential)
• Step 9 is conditional: only fires on size-trigger or semantic upstream-stack impact
• Step 10 is the alignment-review loop: runs review-implementation → fix → re-review until clean, and owns the DEVIATIONS reconciliation
• Run/skip per the single Applicability Matrix in Step 3 — no per-step skip lists to drift
═══════════════════════════════════════════════════════════════════

Note:
• You: Resolve ticket, pick mode, run soundness review, gate approval, dispatch children/workflow, decide
• Notion subagent: Fetch page + status (1 call, <1k tokens)
• coding:* children: Perform all production Write/Edit/Bash commits (<1k tokens each) — in Mechanism A they are dispatched by workflow agents
• specification:mdc: the ONLY writer for .code-spec/*.md (MDC) decision blocks — orchestrator never edits the bundle directly
• Step 12 guard: fires AskUserQuestion only when a linked git worktree is detected
• --dry-run is plan-only (Applicability Matrix "dry-run" column): no soundness review, no scaffold, no children dispatched, no commits; Step 13 emits the report with status=dry_run
• REFUSE / FLAG_MISMATCH short-circuit after Step 3 / Step 6 — they never reach Steps 4+ (so they need no per-step skip entry)
```

## 3. SKILL IMPLEMENTATION

### Skill Steps

1. Resolve Ticket (Notion fetch + status classification)
2. Download Spec Bundle (sub-skill `specification:sync-spec`; --use-cache short-circuits to reuse local `.code-spec/<slug>/`)
3. Mode Resolution (apply Mode Matrix + Applicability Matrix)
4. Consistency + Features Cross-Check (one analyst: Spec ↔ DRAFT ↔ PLAN ↔ Code drift + Feature → symbol coverage)
5. Pre-Implementation Soundness Review (critique spec + code for flaws / arch deviations; record user decisions to local spec via `specification:mdc`)
6. Approval Gate (single, skippable)
7. Workspace Setup (in place; capture `base_rev`; Write-scaffold DEVIATIONS.md)
8. Execute Mode (capability-gated: Mechanism A dynamic `Workflow` fanout + advisor-verify + loop-until-done, else Mechanism B sequential `coding:*` chain)
9. Stack-Aware Sizing & Restack Trigger (delegate to `coding:commit --create-pr` when oversized or upstream-impacting)
10. Spec-Alignment Review Loop (dispatch `specification:review-implementation` → `coding:fix` on P0/P1 → re-review until clean, max 3 iterations; reconcile DEVIATIONS.md)
11. Thought-Experiment Gate (opus + max effort, mandatory)
12. Git-Worktree Relocation Check (AskUserQuestion if work landed in a linked git worktree)
13. Skill Completion Report

### Step 1: Resolve Ticket

**Step Configuration**:

- **Purpose**: Fetch the Notion ticket and classify its status by stage semantics (never by exact option name)
- **Input**: `notion_url_or_id`, optional `repo`, `dry_run`, `skip_approval`
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

    1. Fetch the page via the `notion-sync` CLI as a one-shot recursive pull:
       - `Bash: notion-sync pull <normalized 32-char id> --follow-children --follow-links --out <tmp-dir>` (single call — never iterate per-page across turns)
       - Then `Glob: <tmp-dir>/*.md` and `Read` the file whose filename ends in `-<normalized id>.md` to extract status + linked URLs
       - Requires `NOTION_TOKEN` exported in the shell
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
2. **Error handling** — handle Notion failures explicitly:
   - **Notion 404 / page not found**: report `status=refused` with reason `notion_not_found`; jump to Step 13, do not scaffold the workspace
   - **Notion auth**: report `status=refused` with reason `notion_unavailable`; jump to Step 13
   - **Malformed id** (not 32-hex after normalization): report `status=refused` with reason `invalid_id`; jump to Step 13
   - **Fetch transient error**: retry once; if second failure, treat as `notion_unavailable`
3. If `status_stage=unknown`: use `AskUserQuestion` to surface the raw option and let the user map it to a stage, or abort (→ `status=flagged`)
4. Cache the ticket for downstream steps
5. Mark the `resolve-ticket` todo as `completed`

### Step 2: Download Spec Bundle

**Step Configuration**:

- **Purpose**: Materialize a hard local copy of the Notion spec into `<repo>/.code-spec/<ticket.slug>/` BEFORE any coding can begin. This is a hard gate — if the root spec file cannot be persisted locally, the skill MUST stop and refuse to dispatch any `coding:*` child. The only bypass is `--use-cache` with a pre-existing valid local bundle.
- **Input**: `ticket` (from Step 1), `--use-cache`, `--repo`
- **Output**: `spec_bundle` = `{ root_path, files[], cache_hit }` where `files[]` entries are `{ path, notion_id }`; plus the **shared spec pointer block** (computed once, reused by Steps 4, 5, 11)
- **Sub-skill**: `specification:sync-spec` (download); cache check is performed inline before delegation
- **Parallel Execution**: Delegated to sub-skill

#### Phase 1: Cache Check (You)

1. Compute `bundle_root = <repo>/.code-spec/<ticket.slug>/`
2. **Cache decision**:
   - **Cache-hit path**: If `--use-cache` AND `bundle_root/` contains at least one `*.md` file (`Glob: <bundle_root>/*.md` returns non-empty) AND the file whose `{32hex-id}` filename suffix matches `ticket.id` exists and is non-empty → load `spec_bundle` from disk (enumerate via `Glob`, parse the 32-hex suffix from each filename to populate `files[]`), set `cache_hit=true`, **skip Phase 2**. This is the only branch that may continue without a fresh Notion fetch.
   - **Cache-miss under --use-cache**: If `--use-cache` is set but the cache is incomplete (no `*.md` files OR the root id-suffix file is missing/empty) → log a `cache_miss_fallthrough` notice and proceed to Phase 2 (sub-skill will wipe + re-download).
   - **Default path**: Otherwise → proceed to Phase 2. The sub-skill always wipes `<spec-path>` before downloading; no extra wipe is required here.
3. **Auto-write `<repo>/.code-spec/.gitignore`** containing a single line `*` if the file does not already exist, so bundles never accidentally get committed. Idempotent — never overwrite an existing user-managed gitignore. (Note: `notion-sync pull` also writes its own `.gitignore` at `<bundle_root>/.gitignore`; this parent-level one covers the whole `.code-spec/` directory across all slugs.)
4. Add TodoWrite `download-spec-bundle` → `in_progress`

#### Phase 2: Sub-Skill Invocation (You)

Skip this phase entirely if Phase 1 took the cache-hit path.

1. Use `Read` to load `/Users/alvis/Repositories/.claude/plugins/specification/skills/sync-spec/SKILL.md`
2. Invoke `specification:sync-spec` via the `Skill` tool with:
   - `notion_url_or_id`: `ticket.id`
   - `--spec-path`: `<bundle_root>` (i.e. `<repo>/.code-spec/<ticket.slug>`) — sync-spec is slug-agnostic; namespacing is implement-code's responsibility
3. Capture the sub-skill's report. Map `outputs.spec_bundle.spec_path` → `spec_bundle.root_path`. Set `spec_bundle.files = outputs.spec_bundle.files` (each entry `{ path, notion_id }`). Set `spec_bundle.cache_hit = false`.

#### Phase 3: Decision (You)

This is the **hard gate** that guarantees a local spec hard copy exists before coding. No `coding:*` child may be dispatched unless this gate passes.

- **On sub-skill `status=refused` with reason `spec_bundle_unavailable` / `notion_not_found` / `notion_unavailable` / `invalid_id`**: report this skill's `status=refused` with the same reason (or `spec_bundle_unavailable` if the sub-skill returned a different upstream reason but the root file is missing), jump to Step 13. Do NOT proceed to Step 3. Do NOT scaffold the workspace. Do NOT dispatch any `coding:*` child.
- **On sub-skill `status=completed` with `issues[]` warnings** (some children/linked pages failed): the hard-copy guarantee is satisfied — warn, continue with what was fetched, surface the missing-children list in the final report.
- **On sub-skill `status=completed` with no warnings, OR cache hit**: cache `spec_bundle` for downstream steps; mark todo `completed`.
- **Verification before exit**: Before marking this step complete, locate the entry in `spec_bundle.files[]` whose `notion_id` equals `ticket.id` and confirm via `Bash test -s <root file>` that it exists non-empty. If the file is missing despite a `completed` report, treat as refusal (`spec_bundle_unavailable`) and apply the rule above.

#### Phase 4: Compute the shared spec pointer block (You)

Compute the pointer block **once here** and reuse it verbatim in Steps 4, 5, and 11 — never recompute per-step. `Glob: <bundle_root>/*.md`, identify the root file by filename suffix matching `ticket.id`, and read its (plus adjacent reachable bundle files') `Features` / `Acceptance` / `Usage` / `Example` / `Scenario` / `Verification` headings. Cache the resulting `spec_pointer_block = { root_filename, features[], acceptance[], usages[] }` for the downstream read-only agents.

### Step 3: Mode Resolution

**Step Configuration**:

- **Purpose**: Select exactly one of seven modes based on the ticket stage and artifact presence, and read off which downstream steps run from the Applicability Matrix
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

**Mode Semantics**: See `references/modes.md` for one-line semantics + per-mode child chains. Load only the section for the resolved mode after selection.

#### Applicability Matrix (single source of truth for run/skip)

Every gated step reads its run/skip decision from this one table instead of restating its own list (which is how skip conditions drift). `✓` = runs, `–` = skipped. Columns assume the global gates below have not already short-circuited.

| Mode | S5 Soundness | S8 Mechanism | S9 Stack | S10 Alignment | S11 Thought-Exp | S12 Worktree |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| `COMMIT_PLAN`        | ✓ | A | ✓ | ✓ | ✓ | ✓ |
| `PI_ITERATE`         | ✓ | A | ✓ | ✓ | ✓ | ✓ |
| `AUDIT_AND_COMPLETE` | ✓ | A | ✓ | ✓ | ✓ | ✓ |
| `DRAFT_THEN_ASK`     | – | B | – | – | – | ✓ⁱ |
| `VERIFY_ONLY`        | – | B | – | –ᵛ | – | –ⁿ |
| `FLAG_MISMATCH`      | exits at Step 3 (or Step 6 on user decline) — never reaches S4+ |
| `REFUSE`             | exits at Step 3 — never reaches S4+ |

- **S8 Mechanism**: `A` = dynamic `Workflow` when the tool is available, else falls back to `B`; `B` = sequential `coding:*` chain. `VERIFY_ONLY`/`DRAFT_THEN_ASK` are always `B` (review-only / code-light).
- **Global gates (apply on top of the table)**:
  - `--dry-run` → skip S5 and all of S7-scaffold + S8-dispatch + S9–S12 (plan-only; S8 sets `execution.mechanism=none`).
  - `commits_landed` empty → skip S9, S10, S11, S12 (nothing landed to organize, align, trace, or relocate).
- **ⁱ** S12 runs for `DRAFT_THEN_ASK` only if a draft commit actually landed (else caught by the empty-`commits_landed` gate).
- **ᵛ** `VERIFY_ONLY` is itself a review; S10 is moot since it lands no commits (caught by the empty-`commits_landed` gate).
- **ⁿ** `VERIFY_ONLY` lands no commits → S12 skipped by the empty-`commits_landed` gate.
- **Thought-Experiment runs for `AUDIT_AND_COMPLETE`**: requirement-coverage (S10) and intended-usage tracing (S11) both remain valid for audit work — the mode finishes a real implementation, so tracing every usage through landed code is exactly the confidence the audit needs.

#### Phase 2: Decision (You)

1. Record selected `mode` and the exact matrix row that fired
2. If `REFUSE` or (`FLAG_MISMATCH` and user declines to override): jump to Step 13 with `status=refused|flagged`
3. Otherwise proceed to Step 4

### Step 4: Consistency + Features Cross-Check

**Step Configuration**:

- **Purpose**: In a single read-only analyst pass, cross-check Spec (Notion bundle) ↔ DRAFT.md ↔ PLAN.md ↔ existing code to surface drift, AND map each Spec Feature to a concrete code symbol with a coverage status. (Merged: one bundle-walk + one code-grep produces both the drift table and the coverage map — they share the same inputs, so they share one agent.)
- **Input**: `ticket`, `spec_pointer_block` (from Step 2 Phase 4), local `DRAFT.md`/`PLAN.md`, repo code
- **Output**: `consistency_report` with `{spec_vs_draft, draft_vs_plan, plan_vs_code, drift_items[]}` **and** `features_coverage[]` with `{feature, target_symbol, target_file, status: covered|planned|missing}`
- **Sub-skill**: None
- **Parallel Execution**: No (single pass, read-only)

#### Phase 1: Planning (You)

1. Confirm Step 3 produced a non-terminal mode (not `REFUSE` / `FLAG_MISMATCH`); otherwise short-circuit
2. Locate `DRAFT.md` and `PLAN.md` in the repo (read-only `Glob`)
3. Use TodoWrite to add `consistency-features` todo as `pending` → `in_progress` on dispatch
4. Queue one read-only analyst subagent with the artifacts + shared pointer block inline

#### Phase 2: Execution (Subagent)

Dispatch one read-only analyst subagent that produces **both** the drift table and the coverage map.

    >>>
    **ultrathink: adopt the Spec Consistency & Coverage Analyst mindset**

    - You're a **Spec Consistency & Coverage Analyst**:
      - **Read-Only**: Never edit files
      - **Diff-Centric**: For drift, focus on items present in one artifact but not the others
      - **Map-Centric**: For coverage, bind each Feature to its closest-named exported code symbol
      - **Terse**: Report each drift item and each coverage row as a single line

    **[IMPORTANT]** Enumerate the bundle via `Glob: <bundle_root>/*.md`. The root spec file is the one whose filename ends `-<ticket.id>.md` (32-hex suffix). Open only the files referenced in the pointer block. Do NOT re-fetch from Notion.

    **Assignment**
    Compare and map these artifacts in ONE pass:
    - Spec bundle root: `<spec_bundle.root_path>` — flat directory of `{kebab-title}-{32hex-id}.md` files; identify the root by filename suffix matching `<ticket.id>`; open only the pointer-list files; do NOT re-fetch from Notion
    - Spec pointer block (pre-computed by orchestrator in Step 2 — Features / Acceptance headings across the root + adjacent bundle files)
    - DRAFT.md — [path if present, else N/A]
    - PLAN.md — [path if present, else N/A]
    - Code under [repo path] matching Features slugs

    **Steps**

    1. Extract Features / Acceptance criteria from Spec
    2. Extract commit blueprints from DRAFT.md
    3. Extract phase → commit mapping from PLAN.md
    4. Grep/Glob code for symbols matching Features slugs
    5. **Drift table** — each row = one Feature with columns `spec | draft | plan | code` and a `status`:
       - `aligned`: present in all relevant artifacts
       - `missing_plan` / `missing_draft` / `missing_code` / `missing_spec`
       - `signature_drift`: signatures differ across artifacts
    6. **Coverage map** — for each Feature, bind one code symbol (prefer the closest-named exported symbol) and classify:
       - `covered`: symbol exists and its shape matches Feature
       - `planned`: symbol referenced by DRAFT.md/PLAN.md only
       - `missing`: no match in any artifact

    **Report**

    ```yaml
    status: pass|warn|fail
    summary: 'N drift items / M features mapped'
    outputs:
      consistency_report:
        spec_vs_draft: 'aligned|partial|missing'
        draft_vs_plan: 'aligned|partial|missing'
        plan_vs_code: 'aligned|partial|missing'
        drift_items:
          - feature: '<name>'
            status: 'aligned|missing_plan|missing_draft|missing_code|missing_spec|signature_drift'
            detail: '<one-liner>'
      features_coverage:
        - feature: '<name>'
          target_symbol: '<name or null>'
          target_file: '<path or null>'
          status: 'covered|planned|missing'
    issues: []
    ```
    <<<

#### Phase 3: Decision (You)

- If `consistency_report.status=fail` and mode is `COMMIT_PLAN` or `PI_ITERATE`: downgrade to `FLAG_MISMATCH` and re-enter Step 3
- If any Feature is `missing` and mode is `COMMIT_PLAN`: warn and consider downgrade to `DRAFT_THEN_ASK`
- Otherwise: attach `consistency_report` + `features_coverage` to the running context and proceed to Step 5

### Step 5: Pre-Implementation Soundness Review

**Step Configuration**:

- **Purpose**: Before any code is written, critically review the spec bundle AND the current code implementation (if any) for genuine flaws or major architectural deviations that must be addressed *first*. This is distinct from Step 4, which only checks artifact drift + coverage — Step 5 asks "is the spec itself sound, internally consistent, feasible, and architecturally compatible with the existing code?" Any blocking issue is resolved **with the user** and the decision is recorded back into the local spec so the spec is fully prepared and correct before implementation begins.
- **Input**: `mode`, `ticket`, `spec_bundle`, `spec_pointer_block`, `consistency_report`, `features_coverage`, repo code, `dry_run`
- **Output**: `soundness_review` = `{ issues_found, decisions_recorded[], spec_files_updated[] }`
- **Sub-skill**: `specification:mdc` (to record decisions into the local spec bundle)
- **Parallel Execution**: Capability-gated (see Phase 2)

**Run/skip**: Per the **Applicability Matrix** (Step 3) — runs for `COMMIT_PLAN` / `PI_ITERATE` / `AUDIT_AND_COMPLETE`, skipped (record `soundness_review = { issues_found: 0, decisions_recorded: [], spec_files_updated: [], skipped: true }`) otherwise and under `--dry-run`. (`AUDIT_AND_COMPLETE` runs it — finishing a partial pass still needs the spec verified and sound first.)

#### Phase 1: Planning (You)

1. Use TodoWrite to add `soundness-review` todo as `pending` → `in_progress` on dispatch
2. Reuse the `spec_pointer_block` computed in Step 2 Phase 4 (do not recompute)
3. Decide the detection mechanism via the capability gate in Phase 2

#### Phase 2: Execution (Capability-gated)

- **Mechanism A — fanout (when the `Workflow` tool is available AND scope is non-trivial)**: initiate a small dynamic `Workflow` with a *Find* phase of independent reviewers — each on a distinct lens (spec internal consistency, spec↔code architecture fit, feasibility / invariants / acceptance-criteria soundness) emitting candidate issues — followed by a *Verify* phase where an adversarial verifier tries to refute each candidate (issue is spurious, already handled, or within tolerance). Only un-refuted candidates survive. The workflow returns structured `soundness_issues[]`; it writes no files.
- **Mechanism B — single subagent (fallback when `Workflow` is unavailable/disabled or scope is small)**: dispatch exactly one `opus` Soundness Reviewer subagent (agent type `general-purpose`) that ultrathinks hard about spec soundness and spec↔code architectural fit and returns the same `soundness_issues[]`.

Either way, each issue has the shape:

```yaml
soundness_issues:
  - kind: 'spec-flaw|arch-deviation'
    severity: 'minor|major|blocking'
    spec_loc: '<bundle-file>:<heading or line>'
    code_loc: '<file:line or null>'
    summary: '<one-liner>'
    question: '<the decision the user must make>'
    options: ['<option A>', '<option B>', '...']
```

#### Phase 3: Decision (You) — resolve & record

1. **Resolve loop**: for each issue with `severity ∈ {major, blocking}`, call `AskUserQuestion` using the issue's `question` + `options`. (Minor issues are surfaced in the report but do not gate.)
2. **Record each decision back into the local spec** — **[IMPORTANT, MANDATORY]** `.code-spec/*.md` files are MDC (Contextual Markdown). You MUST route every spec-bundle mutation through the **`specification:mdc`** skill (load its SKILL.md via `Read`, then invoke via the `Skill` tool). NEVER edit a `.code-spec/` file with `Write`/`Edit` directly. Append/merge a `## Resolved Decisions` block into the spec file that owns the issue (the file at `spec_loc`), each entry: `- <date> · <question> · **Decision**: <chosen> · <rationale>`. For each recorded decision, append an entry `{question, decision, spec_file}` to `soundness_review.decisions_recorded[]`, and add `spec_file` to the deduped `soundness_review.spec_files_updated[]` list.
3. **Loop** Phase 2→3 until no `major`/`blocking` issue remains unresolved (re-run detection only if a recorded decision materially changed the spec; otherwise one pass suffices).
4. **Durability note** — `.code-spec/` is gitignored and is wiped + re-downloaded on the next non-cache run, so recorded decisions are local-only. Surface in the final report that re-running with `--use-cache` preserves them (per the local-spec-only persistence choice; no Notion sync is performed by this skill).
5. Mark the `soundness-review` todo `completed` and proceed to Step 6.

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
   - Soundness decisions recorded in Step 5 (count + the spec files updated), if any
   - Planned execution mechanism (Mechanism A dynamic workflow vs Mechanism B sequential) and the child-skill chain for the mode
   - "Working Draft is treated as non-authoritative. Material deviations are logged to DEVIATIONS.md in the repo. Trivial departures (JSDoc, inferred types, lint) are silent."
3. Call `AskUserQuestion` with a single question and options:
   - `Approve`: proceed with the chain
   - `Switch Mode`: let the user override to another mode (re-enters Step 3 Decision)
   - `Abort`: mark `status=refused`, jump to Step 13
4. `ExitPlanMode` is used for this single gate — no other gates downstream

#### Phase 2: Decision (You)

- `Approve` → proceed to Step 7
- `Switch Mode` → apply user's chosen mode, re-run Step 4 if needed, re-enter this gate once
- `Abort` → jump to Step 13 with `status=refused`

### Step 7: Workspace Setup

**Step Configuration**:

- **Purpose**: Confirm work happens **in place** on the current working copy (`repo_path` = `--repo` or cwd), capture a `base_rev` marker so Step 9 can size the full set of landed commits, and scaffold the DEVIATIONS.md log. No `git worktree`, no jj mutation, no user prompt — `jj` tracks the dirty HEAD safely; all jj organization is deferred to Step 9's `coding:commit`.
- **Input**: `ticket`, `--repo`, `--dry-run`, `mode`
- **Output**: `repo_path`, `base_rev`
- **Sub-skill**: None
- **Parallel Execution**: No

#### Execute (You)

When you reach this step:

1. Set `repo_path` = `--repo` or the current working directory. This is where every child edit happens — there is no worktree to create and no branch to name.
2. **Capture `base_rev`** (read-only `Bash`): record the current working-copy revision BEFORE any child commits, so Step 9 can diff `base_rev`→HEAD across the entire set of `commits_landed` rather than only the last commit. Prefer `jj log -r @ --no-graph -T 'change_id'` (jj-first); fall back to `git rev-parse HEAD` when jj is unavailable. Store as `base_rev`. (Skip the capture under `--dry-run` — no commits will land.)
3. If `--dry-run=true` OR `mode` ∈ {`VERIFY_ONLY`, `REFUSE`, `FLAG_MISMATCH`}: **skip** the DEVIATIONS.md scaffold — no scaffold is written, and execution proceeds to Step 8 with children running in read-only dispatch configuration against `repo_path`.
4. Otherwise, **`Write` `<repo_path>/DEVIATIONS.md`** with the header template below. This is the **one** file the orchestrator writes directly (per the Zero-Direct-Writes carve-out); coding children append `D-N` entries to it during Step 8 and never rewrite the header.

    ```markdown
    # Deviations from Notion Draft

    **Spec**: <ticket.title> (<ticket.id>)
    **Repo**: <repo_path>
    **Draft source**: <notion spec URL>

    Entries below are material departures from the draft discovered during implementation. Trivial differences (JSDoc, inferred types, lint/format) are not recorded.

    ---
    ```

5. Update TodoWrite: add todos for the planned `coding:*` chain for the selected mode

### Step 8: Execute Mode

**Step Configuration**:

- **Purpose**: Land the mode's code against the working copy via the right execution mechanism — a dynamic `Workflow` (fanout + adversarial advisor-verification + loop-until-done) when available, else the sequential `coding:*` chain. Either way, every production `Write`/`Edit`/commit happens inside a dispatched `coding:*` child; the orchestrator never holds the pen and never runs `jj` directly.
- **Input**: `mode`, `repo_path`, `ticket`, `spec_bundle`, `consistency_report`, `features_coverage`, `dry_run`
- **Output**: `child_dispatch_log[]`, `commits_landed[]`, `execution = { mechanism, workflow_runs, pending_decisions_resolved }`
- **Sub-skill**: `Workflow` (Mechanism A) and/or one or more of `coding:draft-code`, `coding:write-code`, `coding:complete-code`, `coding:fix`, `coding:review`, `coding:commit`, `coding:handover`; `specification:mdc` to record any mid-run decision into the local spec
- **Parallel Execution**: Mechanism A fans out agents concurrently inside the workflow; Mechanism B runs children sequentially (they may internally parallelize)

#### Phase 1: Planning (You)

0. **Pre-coding hard-copy gate**: Before selecting any mechanism, verify the bundle's root spec file (the entry in `spec_bundle.files[]` whose `notion_id` matches `ticket.id`) still exists and is non-empty (`Bash test -s <root file>`). This is a defence-in-depth check against any path that could have skipped Step 2's gate (e.g. injected mode override, race with manual cleanup). If missing, set `status=refused` with reason `spec_bundle_missing_at_dispatch`, do NOT dispatch any child, jump to Step 13.

1. **Dry-run short-circuit**: if `--dry-run` is set, this step is plan-only — set `execution.mechanism = none`, dispatch no children, leave `child_dispatch_log` and `commits_landed` empty, and proceed to Step 9 (which itself skips on empty `commits_landed`).
2. **Mechanism gate** (real runs only) — choose exactly one, per the Applicability Matrix S8 column:
   - **Mechanism A (dynamic workflow)** when BOTH hold: the `Workflow` tool is available (not disabled) and `mode ∈ {COMMIT_PLAN, PI_ITERATE, AUDIT_AND_COMPLETE}`. Set `execution.mechanism = workflow`.
   - **Mechanism B (sequential)** otherwise — `Workflow` unavailable/disabled, or `mode ∈ {DRAFT_THEN_ASK, VERIFY_ONLY}` (code-light / review-only modes). Set `execution.mechanism = sequential`. (`FLAG_MISMATCH` / `REFUSE` dispatch nothing — they already exited at Step 3.)
3. Update TodoWrite with the planned work (one todo per workflow phase for A, or one per dispatched child for B).

#### Phase 2: Execution — Mechanism A (dynamic workflow)

Ultracode this step — i.e. organize the work as the dynamic implementation workflow described in **`references/execute-workflow.md`** (Fanout → adversarial Verify → loop-until-done, with the `pending_decision` stop contract). Pass it `repo_path`, the spec pointer block, `mode`, `features_coverage`, and the verbatim `deviation_policy` block from `references/modes.md`. The workflow's implementation agents dispatch the same `coding:*` children (and `coding:commit`) as Mechanism B; the orchestrator still never edits files or runs `jj` directly.

**Stop → ask → patch → resume loop** (workflows cannot take mid-run user input):

1. Run the workflow. It returns `{ verified_slices, pending_decisions[], commits_landed[], unresolved[], child_dispatch_log[] }`. When an agent hits an architectural decision it cannot resolve from the spec, it records a `pending_decision` and the run **stops early** rather than guessing.
2. If `pending_decisions` is non-empty: for each, call `AskUserQuestion`, then **record the answer into the local spec via `specification:mdc`** (MANDATORY — `.code-spec/*.md` is MDC; never `Write`/`Edit` it directly). The recorded spec edits ARE the patch — agents re-read the spec on resume.
3. **Resume** the workflow with `Workflow resumeFromRunId` (the cached prefix replays completed slices instantly; decided slices now implement with the decision baked in). Increment `execution.pending_decisions_resolved` and `execution.workflow_runs`.
4. Repeat 1–3 until the run finishes with empty `pending_decisions` and every slice verified, or a `log()`-ed max-iteration / token guard trips (no silent caps).
5. Merge the workflow's `child_dispatch_log[]` and `commits_landed[]` into this skill's outputs. **After the last code commit**, dispatch one trailing `coding:commit` scoped to `DEVIATIONS.md` per the "Trailing DEVIATIONS Commit" rules in `references/modes.md`.

#### Phase 3: Execution — Mechanism B (sequential, fallback)

Select the child chain from the mode. **See `references/modes.md` "Step 8 — Per-Mode Child Chains"** for the full chain per mode (`COMMIT_PLAN` / `PI_ITERATE` / `DRAFT_THEN_ASK` / `AUDIT_AND_COMPLETE` / `VERIFY_ONLY`).

For each child in the chain, in order:

1. Load the child SKILL.md via `Read`
2. Invoke via `Skill` tool with a minimal payload:
   - `repo_path`
   - `ticket_summary` (title + slug)
   - `deviation_policy`: the verbatim block from `references/modes.md` "Deviation Policy Block" (embed in every `coding:*` dispatch payload)
   - Child-specific inputs (e.g. plan phase, drift items, features to complete)

3. **[IMPORTANT]** You do NOT call `Write`/`Edit` on production files yourself — you rely on the child's tool grants
4. Capture each child's status + summary into `child_dispatch_log`
5. On `coding:review` failure: run `coding:fix` then re-run `coding:review`, max 3 iterations
6. On `coding:commit` success: append SHA to `commits_landed`
7. **Mid-run architectural decisions**: if a child surfaces an architectural decision needing user input, ask inline via `AskUserQuestion` and record the answer into the local spec via `specification:mdc` (MANDATORY — never edit the MDC bundle directly) before continuing the chain.
8. **After the last code commit**, dispatch one trailing `coding:commit` scoped to `DEVIATIONS.md` per the "Trailing DEVIATIONS Commit" rules in `references/modes.md` (skips when header-only, `VERIFY_ONLY`/`DRAFT_THEN_ASK`, or `--dry-run`).

#### Phase 4: Decision (You)

- All work succeeds (workflow finished clean, or all children succeeded) → Step 9
- Mechanism A exhausts its iteration/token guard with `unresolved[]` slices remaining → dispatch `coding:handover` to capture state, mark `status=partial`, jump to Step 12
- Mechanism B child fails twice in a row → dispatch `coding:handover` to capture state, mark `status=partial`, jump to Step 12

### Step 9: Stack-Aware Sizing & Restack Trigger

**Run/skip**: Per the **Applicability Matrix** (Step 3) plus the global `commits_landed`-empty and `--dry-run` gates — skip (record `stack_dispatch.dispatched=false` with reason) for `VERIFY_ONLY` / `DRAFT_THEN_ASK`, under `--dry-run`, or when `commits_landed` is empty.

Otherwise, **see `references/stack-aware-sizing.md`** for the full step (size + restack trigger classification against `base_rev`, `coding:commit` dispatch payload, decision rules). Step 9 is the **sole owner** of all jj organization in this skill — the orchestrator NEVER runs `jj split` / `jj bookmark set` / `jj rebase` / `gh pr create` directly; every jj mutation is dispatched through `coding:commit`.

Output written back to `stack_dispatch` = `{ dispatched, mode: stacked-pr|restack|null, branch_prefix, prs[] }` for Step 13.

### Step 10: Spec-Alignment Review Loop

**Step Configuration**:

- **Purpose**: After the loop-until-done implementation lands, prove the code is faithfully aligned with the agreed spec by running `specification:review-implementation` and closing every P0/P1 alignment finding in a review → fix → re-review loop until clean. This step also **owns the DEVIATIONS.md reconciliation** (formerly a separate post-change re-check): each logged deviation is checked against the landed code, and behavior-changing / blocking deviations are folded into the alignment verdict. This is the "full confidence" requirement-coverage gate.
- **Input**: `repo_path`, `spec_bundle.root_path`, `commits_landed`, `mode`, `dry_run`, `<repo_path>/DEVIATIONS.md`
- **Output**: `alignment_review = { iterations, final_verdict, remaining_p0, remaining_p1, report_path, deviations_reconciled }`
- **Sub-skill**: `specification:review-implementation`, `coding:fix`
- **Parallel Execution**: No (sequential loop)

**Run/skip**: Per the **Applicability Matrix** (Step 3) plus the global gates — skip (record `alignment_review = { iterations: 0, final_verdict: 'skipped', remaining_p0: 0, remaining_p1: 0, report_path: null, deviations_reconciled: false }`) under `--dry-run`, when `commits_landed` is empty, or for `DRAFT_THEN_ASK` (`VERIFY_ONLY` lands no commits, so the empty-`commits_landed` gate already skips it).

#### Phase 1: Planning (You)

1. Use TodoWrite to add `alignment-review` todo as `pending` → `in_progress` on dispatch
2. Resolve the implementation file set from `commits_landed` (the changed files)
3. Read `<repo_path>/DEVIATIONS.md` and extract every `D-N` entry with its `Impact on spec` + `Severity` for reconciliation in Phase 2

#### Phase 2: Execution (Sub-Skill loop)

Iterate, starting at `iteration = 1`:

1. Load `/Users/alvis/Repositories/.claude/plugins/specification/skills/review-implementation/SKILL.md` via `Read`, then invoke `specification:review-implementation` via the `Skill` tool with:
   - the implementation specifier (`repo_path` or the changed-file set)
   - `--spec-path` = `<spec_bundle.root_path>`
   - `--area=alignment`
   - the extracted `DEVIATIONS.md` entries, so the alignment reviewer treats every `behavior-change` / `blocking` deviation as a candidate P0 alignment finding to confirm against the landed code
2. Parse the returned `ALIGNMENT.md` verdict + open `{ p0, p1 }` counts. Set `deviations_reconciled=true` once the reviewer has cross-checked the supplied `D-N` entries.
3. **If `PASS` (no P0/P1)**: set `final_verdict='PASS'`, record `iterations`, exit the loop.
4. **If `FAIL` with P0/P1 and `iteration < 3`**: dispatch `coding:fix` scoped to the cited P0/P1 findings (pass `repo_path`, `ticket_summary`, the verbatim `deviation_policy`, and the finding list), then `iteration += 1` and repeat from step 1.
5. **If `iteration == 3` and P0/P1 remain**: stop; carry the residual counts into `remaining_p0` / `remaining_p1`.

#### Phase 3: Decision (You)

- `final_verdict='PASS'` → keep `status` as set by Step 8 (`completed` unless an earlier partial was recorded).
- Residual P0/P1 after the cap, OR any unresolved `blocking` deviation surfaced in reconciliation → set `status=partial` and surface `alignment_review` in the final report.
- Record `report_path` = the `ALIGNMENT.md` location for Step 13.

### Step 11: Thought-Experiment Gate

**Run/skip**: Per the **Applicability Matrix** (Step 3) plus the global gates — skip (record `thought_experiment_report.status=skipped` with reason) for `VERIFY_ONLY` / `DRAFT_THEN_ASK`, under `--dry-run`, or when `commits_landed` is empty. **It runs for `AUDIT_AND_COMPLETE`** — tracing every intended usage through the finished implementation is exactly the integration confidence an audit needs.

Otherwise, **see `references/thought-experiment.md`** for the full paper-only integration validation step (mandatory `model=opus` + maximum reasoning effort dispatch, verbatim subagent prompt, per-usage verdict rules, and decision flow). It reuses the `spec_pointer_block`'s Usage/Example/Scenario/Verification entries. Output `thought_experiment_report` is attached for Step 13.

### Step 12: Git-Worktree Relocation Check

**Step Configuration**:

- **Purpose**: Post-coding guard — detect whether landed work ended up inside a linked `git worktree` and, if so, ask the user whether to move it back onto HEAD of the main working copy. A `jj workspace` is a sanctioned arrangement and is NEVER flagged.
- **Input**: `repo_path`, `commits_landed`, `--dry-run`
- **Output**: `worktree_relocation` = `{ detected, action }`
- **Sub-skill**: None
- **Parallel Execution**: No

#### Execute (You)

1. **Skip** when `commits_landed` is empty OR `--dry-run` is set — record `worktree_relocation = { detected: false, action: 'skipped' }` and proceed to Step 13.
2. **Detect a linked `git worktree`** at `repo_path` (read-only `Bash`):
   - `git rev-parse --git-common-dir` ≠ `git rev-parse --git-dir`, OR
   - the resolved `git dir` path lies under `.git/worktrees/`.
   - A `jj workspace` is sanctioned — never flag it. (`jj workspace` does not produce a linked `git worktree` git-dir layout.)
3. **If no linked git worktree is detected**: record `worktree_relocation = { detected: false, action: 'none' }` and proceed to Step 13.
4. **If a linked git worktree IS detected**: you MUST call `AskUserQuestion` asking whether to move the landed work back onto HEAD of the main working copy. Surface the worktree path and `commits_landed` in the prompt. Record the user's choice in `worktree_relocation.action` (e.g. `relocate` | `keep`). The actual relocation, if chosen, is performed by dispatching `coding:commit` (the sole owner of jj organization) — never run `jj`/`git worktree` mutations directly here.

### Step 13: Skill Completion

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
  workspace:
    repo_path: '<abs path>'
    base_rev: '<jj change id or git sha>'
  consistency_report: { ... }
  features_coverage: [ ... ]
  soundness_review:
    issues_found: <N>
    decisions_recorded:
      - question: '<the decision asked>'
        decision: '<chosen option>'
        spec_file: '<.code-spec/*.md updated>'
    spec_files_updated: [ '<path>', ... ]
    skipped: true|false
  execution:
    mechanism: 'workflow|sequential|none'   # none = --dry-run plan-only
    workflow_runs: <N>            # number of launch+resume cycles (Mechanism A); 0 for sequential
    pending_decisions_resolved: <N>
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
  alignment_review:
    iterations: <N>
    final_verdict: 'PASS|FAIL|skipped'
    remaining_p0: <N>
    remaining_p1: <N>
    deviations_reconciled: true|false
    report_path: '<abs path to ALIGNMENT.md>|null'
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
  worktree_relocation:
    detected: true|false
    action: 'none|skipped|relocate|keep'
summary: |
  Implementation of ticket <slug> resolved to mode <mode> and landed <N> commits
  in <repo_path> via the <workflow|sequential> mechanism. Spec Features coverage: <X>/<Y>.
  Soundness review: <issues_found> issue(s), <decisions_recorded> decision(s) recorded to the local spec.
  Execution: <workflow_runs> workflow run(s), <pending_decisions_resolved> mid-run decision(s) resolved.
  Alignment review: <PASS|FAIL|skipped> after <iterations> iteration(s) (<remaining_p0> P0 / <remaining_p1> P1 left; deviations_reconciled=<true|false>).
  Thought experiment: <pass|partial|fail> (<W>/<B>/<U> works/broken/unclear).
  Stack: <dispatched=true|false> [mode=<split|create|restack> slug=<slug> prs=<N>].
  Git-worktree relocation: <detected=true|false> [action=<none|relocate|keep>].
```

> **Summary guidance**: When `thought_experiment_report.status != skipped`, the `summary:` string MUST mention that the thought experiment ran on **opus with maximum reasoning effort** — this is how the reader confirms the mandatory opus/max-effort dispatch was honoured, not downgraded. Omit the opus note only when `status=skipped` (VERIFY_ONLY, DRAFT_THEN_ASK, REFUSE, FLAG_MISMATCH, `--dry-run`, or empty `commits_landed`).

## 4. EXAMPLES

### Example 1: Approved spec with DRAFT + PLAN → COMMIT_PLAN

Invocation:

```
/specification:implement-code https://www.notion.so/<workspace>/296b2572f788804094e4fa180444c26d
```

Fetched ticket:

- `status_group=to_do`, `status_option=Pending Implementation`, regex `/pending|ready|approved/i` fires → `stage=ready-to-code`
- DRAFT.md + PLAN.md both exist in repo

Mode matrix row 4 fires → `COMMIT_PLAN`. After approval, dispatches `coding:write-code` → `coding:review` → `coding:commit` per PLAN phase.

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
- `--dry-run` is plan-only: the Applicability Matrix global gate skips Step 5 and all of Steps 7-scaffold + 8-dispatch + 9–12 (Step 8 sets `execution.mechanism=none` and dispatches nothing)
- Step 13 emits the report with `status=dry_run`
- Final `status=dry_run` with `child_dispatch_log=[]` and `commits_landed=[]`

### Example 4: Cache hit with --use-cache

```
/specification:implement-code <id> --use-cache
```

- Cache decision: `Glob: <repo>/.code-spec/<slug>/*.md` returns at least one entry AND the root file (filename suffix matches ticket id) is non-empty → load bundle from disk, set `cache_hit=true`, skip Phase 2
- Subsequent steps proceed against the existing bundle without any Notion fetch
- Final report shows `spec_bundle.cache_hit=true`
