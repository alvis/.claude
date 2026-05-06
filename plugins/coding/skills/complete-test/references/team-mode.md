# Team Mode (Agent Teams enabled)

Load this reference during Step 2 of the workflow when the session context contains `**Agent Teams**: enabled` under "Agent Capabilities". It documents the full Team-Mode orchestration with persistent teammates, agent-pool reuse, and `context_level`-based lifecycle management. If Agent Teams are not enabled, use `references/subagent-mode.md` instead.

## Step 2A: Team Mode (Agent Teams enabled)

You are the **Lead Orchestrator**. Your role is strictly **orchestration** — you coordinate, delegate, and aggregate. You MUST NOT perform any testing, analysis, or standards-reading work yourself.

**Lead Rules**:

- **DO**: Discover files, create batches, spawn teammates, manage lifecycle, aggregate results
- **DO NOT**: Read standard files, write tests, analyze coverage, review compliance, or fix issues
- **NEVER**: Read standards or workflow files yourself — pass full file paths to teammates
- **DO NOT**: Assign new tasks to any agent that reported `context_level` >= 50% — retire them instead
- **ALWAYS**: Pass the full file paths of standard files to teammates
- **LIFECYCLE**: Reuse agents with `context_level` < 50%, retire and replace those >= 50%

### Phase 1: Initial Coverage Analysis (Lead + Analyst Teammate)

**Lead Actions**:

1. **Receive source files list** from workflow inputs
2. **Discover existing test files** using Glob tool: `**/*.spec.{ts,tsx}` or `**/*.test.{ts,tsx}`
3. **Discover standard file paths** (do NOT read them):
   - testing/meta.md + testing/write.md
   - typescript/write.md
4. **Create team**: `TeamCreate` with name `complete-test-team`
5. **Initialize agent pool**: Maintain registry tracking name, role, model, context_level, status
6. **Create analysis task**: `TaskCreate` with full instructions
7. **Spawn or reuse analyst**:
   - Check pool for idle analyst with `context_level` < 50%
   - If found: Reuse via `SendMessage`
   - If not: Spawn fresh `analyst-1` using **opus** model, type `general-purpose`
8. **Assign task**: `TaskUpdate` to set owner to analyst

**Analyst Instructions** (via TaskCreate or SendMessage):

```
Subject: Analyze baseline test coverage

Description:
You are a Coverage Analysis Expert performing baseline coverage analysis.

Read the following standards:
- [full path to testing/meta.md + testing/write.md]
- [full path to typescript.md]

Your task:
1. Discover test configuration (vitest.config.ts)
2. Run existing tests: npm run test
3. Generate coverage report: npm run coverage
4. Extract metrics: line, branch, statement, function coverage
5. Identify uncovered code: files, line ranges, branches, functions

Report format (YAML):
status: success|failure
summary: 'Baseline coverage analysis complete'
outputs:
  baseline_coverage: {...}
  uncovered_files: [...]
  partially_covered_files: [...]
context_level: XX% (input_tokens / 200000 * 100)

You CANNOT delegate work to another subagent.
```

**Lead receives analyst report** with `context_level`. Update agent pool:

- If `context_level` < 50%: Mark as `idle` for potential reuse
- If `context_level` >= 50%: Retire via shutdown request

**Output**: Baseline coverage report ready for Phase 2

### Phase 2: Progressive Test Writing (Lead + Writer Teammates)

**Lead Actions**:

1. **Receive baseline coverage** from Phase 1
2. **List uncovered/partially covered files**
3. **Read source files** using Read tool to determine line counts
4. **Create dynamic batches**:
   - Max 2 source files per batch
   - Max 500 total lines per batch
5. **Discover standard file paths** (do NOT read):
   - testing/meta.md + testing/write.md (REQUIRED)
   - typescript/write.md (REQUIRED)
   - documentation/write.md (REQUIRED)
6. **Create writer tasks**: `TaskCreate` per batch with full instructions
7. **Spawn or reuse writers** (max 10 concurrent):
   - Check pool for idle writers with `context_level` < 50%
   - If found: Reuse via `SendMessage`
   - If not: Spawn fresh `writer-N` using **opus** model
8. **Assign tasks**: `TaskUpdate` per batch

**Writer Instructions** (per batch):

```
Subject: Write tests for batch N (X source files)

Description:
You are a Progressive Test Writing Expert responsible for achieving 100% coverage for ALL source files in this batch.

Read the following standards:
- [full path to testing/meta.md + testing/write.md]
- [full path to typescript.md]
- [full path to documentation.md]

Your batch: [list 2-5 source files with line counts]

Your goal: 100% coverage for ALL files in batch using progressive test writing.

Critical workflow:
FOR EACH source file in batch:
1. Check current coverage
2. Write ONE test targeting uncovered line/branch
3. Run coverage verification
4. KEEP if coverage increased, DELETE if not
5. Repeat until 100% for this file
6. Move to next file in batch

Report coverage per file, tests created/kept/deleted, standards compliance, context_level.

You CANNOT delegate work to another subagent.
```

**Lead receives writer reports** with `context_level`. Update agent pool per writer:

- If `context_level` < 50%: Mark as `idle`, can reuse for next batch
- If `context_level` >= 50%: Retire via shutdown request, spawn fresh replacement if needed

**Output**: Complete test suite with 100% coverage

### Phase 3: Remove Redundant Tests (Lead + Planner + Remover Teammates)

**Phase 3.1: Planning**

**Lead Actions**:

1. **Receive complete test suite** from Phase 2
2. **Create planning task**: `TaskCreate` for redundancy analysis
3. **Spawn or reuse planner**:
   - Check pool for idle planner with `context_level` < 50%
   - If found: Reuse via `SendMessage`
   - If not: Spawn fresh `planner-1` using **opus** model, type `Plan`
4. **Assign task**: `TaskUpdate` to planner

**Planner Instructions**:

```
Subject: Analyze tests for redundancy

Description:
You are a Test Redundancy Analyst identifying unnecessary tests.

Read testing/meta.md + testing/scan.md to understand redundancy criteria.

Your task:
1. Read all test files from Phase 2
2. For each test, determine: covered lines, branches, unique behavior
3. Identify redundancy patterns (coverage is scoped to mirrored source file)
4. Create removal candidates list with risk assessment
5. Create removal tasks (max 10 tests per task)

CRITICAL: Tests that contribute to their mirrored source file MUST be kept.
Tests verifying different behavioral aspects must be kept separate.

Report: removal tasks with test names, reasons, risk levels, context_level.

You CANNOT delegate work to another subagent.
```

**Lead receives plan**, parses removal tasks, creates `TaskCreate` per removal task.

**Phase 3.2: Parallel Removal**

**Lead Actions**:

1. **Spawn or reuse removers** (max 10 concurrent):
   - Check pool for idle removers with `context_level` < 50%
   - If found: Reuse via `SendMessage`
   - If not: Spawn fresh `remover-N` using **opus** model
2. **Assign removal tasks**: `TaskUpdate` per remover

**Remover Instructions** (per task):

```
Subject: Remove redundant tests from task N

Description:
You are a Surgical Test Removal Expert preserving 100% coverage.

Your assignment: [list tests to attempt removal with reasons]

Critical workflow:
FOR EACH test:
1. Pre-removal: Check mirrored source file coverage (must be 100%)
2. Remove test (comment out or delete)
3. Post-removal: Check mirrored source file coverage again
4. KEEP removed if coverage at 100%, RESTORE if coverage dropped
5. Before removing, verify not documenting unique behavioral aspect

Report: tests removed, tests restored, final coverage, context_level.

You CANNOT delegate work to another subagent.
```

**Lead receives remover reports** with `context_level`. Update pool per remover:

- If `context_level` < 50%: Mark as `idle` for reuse
- If `context_level` >= 50%: Retire via shutdown request

**Output**: Optimized test suite with redundant tests removed

### Phase 4: Fix Test Issues (Lead + Fixer Teammates)

**Lead Actions**:

1. **List all test files** using Glob
2. **Determine batching**: If >25 files, batch (max 10 files per batch); else single fixer
3. **Discover standard file paths**:
   - testing/meta.md + testing/write.md
   - typescript/write.md
   - documentation/write.md
4. **Create fixer tasks**: `TaskCreate` per batch
5. **Spawn or reuse fixers**:
   - Check pool for idle fixers with `context_level` < 50%
   - If found: Reuse via `SendMessage`
   - If not: Spawn fresh `fixer-N` using **opus** model
6. **Assign tasks**: `TaskUpdate` per fixer

**Fixer Instructions**:

```
Subject: Fix issues in test files batch N

Description:
You are a Test Standards Enforcer fixing issues and ensuring compliance.

Read the following standards:
- [full path to testing/meta.md + testing/write.md]
- [full path to typescript.md]
- [full path to documentation.md]

Your batch: [list test files]

Your task:
1. Read each test file, identify issues
2. Fix TypeScript errors, AAA pattern, naming, documentation
3. Run tests, lint, type check
4. Verify coverage maintained at 100%

Report: issues fixed, verification results, standards compliance, context_level.

You CANNOT delegate work to another subagent.
```

**Lead receives fixer reports** with `context_level`. Update pool:

- If `context_level` < 50%: Mark as `idle`
- If `context_level` >= 50%: Retire via shutdown request

**Output**: Test files with all issues fixed

### Phase 5: Restructure Fixtures (Lead + Structure Planner + Refactorer Teammates)

**Phase 5.1: Planning**

**Lead Actions**:

1. **Create planning task**: `TaskCreate` for fixture restructuring
2. **Spawn or reuse structure planner**:
   - Check pool for idle planner (any previous planner) with `context_level` < 50%
   - If found: Reuse via `SendMessage`
   - If not: Spawn fresh `structure-planner-1` using **opus** model, type `Plan`
3. **Assign task**: `TaskUpdate` to planner

**Structure Planner Instructions**:

```
Subject: Analyze fixture structure and create restructuring plan

Description:
You are a Test Structure Architect analyzing fixture organization.

Read testing/write.md (Test Double Organization), typescript/write.md, documentation/write.md.

Your task:
1. Discover all fixtures/mocks (spec/fixtures/**, spec/mocks/**, inline in tests)
2. Identify duplication patterns
3. Analyze organization and naming
4. Find unused files
5. Create restructuring plan: consolidations, organization improvements, deletions

Report: comprehensive restructuring plan with migration strategy, context_level.

You CANNOT delegate work to another subagent.
```

**Lead receives plan**, parses restructuring tasks.

**Phase 5.2: Execute Restructuring**

**Lead Actions**:

1. **Create restructuring task(s)**: `TaskCreate` (1 or more based on plan complexity)
2. **Spawn or reuse refactorer**:
   - Check pool for idle refactorer with `context_level` < 50%
   - If found: Reuse via `SendMessage`
   - If not: Spawn fresh `refactorer-1` using **opus** model
3. **Assign task**: `TaskUpdate` to refactorer

**Refactorer Instructions**:

```
Subject: Execute fixture restructuring plan

Description:
You are a Test Refactoring Specialist executing the restructuring plan.

Read testing/write.md, typescript/write.md, documentation/write.md.

Your assignment: [relevant portion of restructuring plan]

Your task:
1. Create new shared fixture/mock files
2. Migrate fixtures/mocks from old locations
3. Update imports in all test files
4. Remove old fixture definitions
5. Delete unused files
6. Verify tests pass after each change
7. Type check and lint

Report: files created/modified/deleted, verification results, context_level.

You CANNOT delegate work to another subagent.
```

**Lead receives report** with `context_level`. Update pool:

- If `context_level` < 50%: Mark as `idle`
- If `context_level` >= 50%: Retire via shutdown request

**Output**: Restructured fixture/mock organization

### Phase 6: Final Verification (Lead + Verifier Teammate)

**Lead Actions**:

1. **Create verification task**: `TaskCreate` for final validation
2. **Spawn or reuse verifier**:
   - Check pool for idle agent (could be analyst from Phase 1 if still < 50%) with `context_level` < 50%
   - If found: Reuse via `SendMessage`
   - If not: Spawn fresh `verifier-1` using **opus** model
3. **Assign task**: `TaskUpdate` to verifier

**Verifier Instructions**:

```
Subject: Perform final comprehensive verification

Description:
You are a Quality Assurance Validator performing final verification.

Read testing/write.md, typescript/write.md, documentation/write.md.

Your task:
1. Coverage verification: Run coverage, verify 100% (line, branch, statement, function)
2. Test execution: Run tests, verify all pass, count total tests, note execution time
3. Standards compliance: Lint, type check, manual review (AAA, naming, JSDoc, type safety)
4. Efficiency metrics: Calculate tests per file, coverage per test, execution time
5. Final quality assessment: Grade (A/B/C/D/F), production readiness, blockers, recommendations

Report: comprehensive verification with pass/fail verdict, context_level.

You CANNOT delegate work to another subagent.
```

**Lead receives verification report** with `context_level`.

**Output**: Final validation report

### Phase 7: Cleanup (Lead)

1. **Collect all results** via `TaskGet` for completed tasks
2. **Aggregate** final statistics across all phases
3. **Shutdown all teammates** via `SendMessage` shutdown requests
4. **Delete team** via `TeamDelete`
5. Proceed to Step 3: Reporting

### Agent Summary

| Agent | Model | Role | Lifecycle |
|-------|-------|------|-----------|
| Lead (skill agent) | opus | Orchestration only | Entire workflow |
| `analyst-1` | opus | Baseline coverage analysis | Phase 1; reused as `verifier-1` in Phase 6 if `context_level` < 50% |
| `writer-N` | opus | Progressive test writing | Phase 2; spawned on demand; reused across batches if `context_level` < 50%; retired if >= 50% |
| `planner-1` | opus (Plan) | Redundancy analysis | Phase 3.1; may be reused as `structure-planner-1` in Phase 5.1 if `context_level` < 50% |
| `remover-N` | opus | Redundant test removal | Phase 3.2; spawned on demand; reused across removal tasks if `context_level` < 50%; retired if >= 50% |
| `fixer-N` | opus | Fix test issues | Phase 4; spawned on demand; reused across batches if `context_level` < 50%; retired if >= 50% |
| `structure-planner-1` | opus (Plan) | Fixture restructuring planning | Phase 5.1; could be reused planner from Phase 3.1 if still < 50% |
| `refactorer-1` | opus | Execute fixture restructuring | Phase 5.2; spawned on demand |
| `verifier-1` | opus | Final verification | Phase 6; could be reused analyst from Phase 1 if still < 50% |

**Key Lifecycle Points**:

- All agents report `context_level` (calculated as `input_tokens / 200000 * 100`) in completion messages
- Agents with `context_level` < 50% return to idle pool for reuse
- Agents with `context_level` >= 50% are retired via shutdown request
- Lead tracks agent pool and makes reuse decisions based on reported context levels
- Analyst from Phase 1 can become Verifier in Phase 6 if context allows
- Planner from Phase 3 can become Structure Planner in Phase 5 if context allows
- Writers, removers, fixers are reused within their respective phases when possible
