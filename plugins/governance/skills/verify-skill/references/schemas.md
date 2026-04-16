# Verify-Skill YAML Schemas

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

## Verification Report — Final Output

The consolidated report produced by verify-skill.

```yaml
status: pass | fail | partial
structural:
  frontmatter: pass | fail
  template_compliance: pass | fail
  content_quality: pass | fail
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
