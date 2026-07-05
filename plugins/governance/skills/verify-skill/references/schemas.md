# Verify-Skill YAML Schemas

## Section & Report Boundary Convention

Each important section of a skill is encircled with a semantic XML boundary tag alongside its markdown heading — `<introduction>`, `<skill_overview>`, `<skill_implementation>` — and every machine-readable report or output contract (subagent reports, per-step reports, the final Skill Completion block) is wrapped in `<report> … </report>`, so every major part carries an unambiguous boundary and cannot bleed into a neighbour. The tags are the boundary; a ` ```yaml ` fence kept inside `<report>` is a syntax hint. Subagent-prompt envelopes keep the `>>>` / `<<<` delimiters. The canonical statement (full tag set + rules) lives in `../../../constitution/references/authoring-invariants.md`.

Template Compliance (Step 2, Subagent B) records this as `boundary_tags: pass | warn`, rolled up under `template_compliance` in the final report. It is **advisory** — a `warn` means some sections or reports are not yet wrapped and MUST NOT set the compliance status (or the final verification status) to `fail`. Skills authored before the convention are flagged for gradual migration via `update-skill`, not failed.

## evals.yaml — Evaluation Definition

Located at: `[skill-dir]/evals/evals.yaml`

```yaml
# Schema for skill evaluation definitions
test_cases:
  - name: string          # Unique test case identifier (e.g., "basic_usage")
    prompt: string         # User prompt to test the skill with
    expectations:
      - text: string       # What to check for
        type: string       # One of: content, filesystem, structure
        # content: check output text contains/matches
        # filesystem: check file exists at path
        # structure: check output format (YAML, sections, etc.)

trigger_eval:
  should_trigger:          # Queries that SHOULD invoke this skill
    - string
  should_not_trigger:      # Queries that should NOT invoke this skill (near-misses)
    - string
```

### Example

```yaml
test_cases:
  - name: basic_creation
    prompt: "Create a new skill called 'deploy-service' in the coding plugin"
    expectations:
      - text: "SKILL.md created"
        type: content
      - text: "coding/skills/deploy-service/SKILL.md"
        type: filesystem
      - text: "frontmatter contains name: deploy-service"
        type: structure

  - name: with_instructions
    prompt: "Create a skill for reviewing PRs with these steps: 1) fetch PR 2) analyze changes 3) post review"
    expectations:
      - text: "Step 1"
        type: content
      - text: "fetch PR"
        type: content

trigger_eval:
  should_trigger:
    - "create a new skill for deploying services"
    - "build a skill that reviews pull requests"
    - "I need a skill for running database migrations"
  should_not_trigger:
    - "update an existing skill"
    - "delete the deploy skill"
    - "run the deploy-service skill"
    - "what skills are available?"
```

## Grading Report — Per-Test-Case Output

Produced by the grader agent for each test case.

```yaml
test_name: string
grade: pass | partial | fail
level_1:
  expectations_met: integer
  expectations_total: integer
  details:
    - expectation: string
      type: content | filesystem | structure
      result: met | not_met | partial
      evidence: string
level_2:
  claims_verified: integer
  claims_total: integer
  details:
    - claim: string
      result: verified | unverified | contradicted
      evidence: string
level_3:
  eval_quality: good | adequate | needs_improvement
  suggestions:
    - string
overall_notes: string
```

## Benchmark Summary — Aggregated Results

Produced by `aggregate_benchmark.py`.

```yaml
total_tests: integer
passed: integer
failed: integer
partial: integer
pass_rate: float           # 0.0 to 1.0
by_test:
  - name: string
    grade: pass | partial | fail
    expectations_met: integer
    expectations_total: integer
common_failures:
  - string                 # Most frequent failure reasons
```

## Trigger Evaluation Report

Produced by `run_trigger_eval.py`.

```yaml
trigger_rate: float        # 0.0 to 1.0
false_positive_rate: float # 0.0 to 1.0
total_should_trigger: integer
correct_triggers: integer
total_should_not_trigger: integer
false_triggers: integer
details:
  - query: string
    expected: boolean
    actual: boolean
    correct: boolean
```

## Description Optimization Report

Produced by `run_trigger_loop.py`.

```yaml
original_description: string
optimized_description: string
original_train_accuracy: float
optimized_train_accuracy: float
original_test_accuracy: float
optimized_test_accuracy: float
improvement: float         # Test accuracy delta
iterations_run: integer
history:
  - iteration: integer
    description: string
    train_acc: float
    test_acc: float
```

## Content Placement Validation Report

Produced by the **Content Placement Validator** subagent (Step 2, Subagent D) in verify-skill.

Enforces the Content Placement Rule: SKILL.md must contain only the always-on core workflow. Conditional content (mode-, scope-, flag-, language-gated) exceeding ~50 lines must be offloaded to `references/<topic>.md`. Reference files must not hide unconditional core steps.

```yaml
status: pass | fail
summary: string
checks:
  no_inline_conditional_bulk: pass | fail   # SKILL.md has no >50-line gated blocks inline
  no_hidden_core_in_references: pass | fail # references/ files contain only conditional content
findings:
  - severity: required_offload | hidden_core | suggestion
    # required_offload: gated block >50 lines inline in SKILL.md (MUST move)
    # hidden_core: reference file contains unconditional core steps (MUST inline)
    # suggestion: candidate for splitting into a separate skill (user decides)
    location: string                # 'SKILL.md:line_start-line_end' or 'references/<file>.md'
    gate: string                    # e.g., 'mode=functional', 'flag --fix', 'language=ts', 'always-on (inverse)'
    line_count: integer
    summary: string                 # one-line description of the block
    recommendation: string          # 'move to references/<topic>.md' | 'split into separate skill <name>' | 'inline into SKILL.md core'
    replacement_pointer: string     # only present when recommending offload, e.g., 'For X, see references/<topic>.md'
issues:
  - string
suggestions:
  - string
```

### Severity Semantics

- `required_offload` — blocks the verify-skill pass; the skill MUST be refactored.
- `hidden_core` — blocks the verify-skill pass; the always-on steps MUST be inlined back into SKILL.md.
- `suggestion` — informational; the user chooses per case whether to split into a separate skill.

### Example

```yaml
status: fail
summary: 'Content placement validation of complete-test'
checks:
  no_inline_conditional_bulk: fail
  no_hidden_core_in_references: pass
findings:
  - severity: required_offload
    location: 'SKILL.md:412-587'
    gate: 'language=python'
    line_count: 175
    summary: 'Python-specific pytest fixture generation walkthrough'
    recommendation: 'move to references/python-fixtures.md'
    replacement_pointer: 'For Python pytest fixtures, see references/python-fixtures.md'
  - severity: suggestion
    location: 'SKILL.md:880-1020'
    gate: 'mode=mutation-testing'
    line_count: 140
    summary: 'Mutation testing workflow with stryker setup, run, and report'
    recommendation: 'split into separate skill mutation-test'
issues:
  - 'Python fixtures section (175 lines) is gated by language but lives inline'
suggestions:
  - 'Mutation testing reads as an independent workflow; consider promoting to its own skill'
```

## Verification Report — Final Output

The consolidated report produced by verify-skill.

```yaml
status: pass | fail | partial
structural:
  frontmatter: pass | fail
  template_compliance: pass | fail
  content_quality: pass | fail
  content_placement: pass | fail
functional:                # Only present if mode=functional|full
  pass_rate: float
  test_cases: integer
  grading_summary: string
trigger:                   # Only present if mode=functional|full
  trigger_rate: float
  false_positive_rate: float
description:               # Only present if optimize_description=true
  original: string
  optimized: string
  improvement: string      # e.g., "+15%"
issues:
  - string
suggestions:
  - string
```
