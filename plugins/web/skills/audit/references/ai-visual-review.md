# Phase 3 -- AI Visual Review (Detail)

Loaded by `SKILL.md` Step 3. Fills in AI verdicts for findings the CLI marked `needs_ai_review`, and resolves cross-origin expansion questions.

**Step Configuration**:
- **Purpose**: Fill in AI verdicts for findings the CLI marked `needs_ai_review`, and resolve cross-origin expansion questions
- **Input**: `<out>/report.json` (contract v3; see `cli/audit_cli/types.py`)
- **Output**: `<out>/report-final.json` with `ai_verdict` populated
- **Parallel Execution**: No

Claude does **not** re-run the crawl, does **not** re-audit code-shaped rules, and does **not** second-guess automated findings. Claude fills in `ai_verdict` only for items the CLI explicitly flagged.

## 3.1 Read the Report

1. Read `<out>/report.json` (path captured from Phase 2 stdout).
2. Validate the contract version matches v3 (see `cli/audit_cli/types.py`). If not, stop and surface the mismatch.

## 3.2 Resolve Cross-Origin Candidates

If `report.cross_origin_candidates` is non-empty:

1. Use **AskUserQuestion once** with the list grouped by origin (social-media hosts are already excluded by the CLI).
2. The user's answer determines which cross-origin pages to include in a follow-up scope. Record declined origins for the Phase 4 site-level section.
3. Do not prompt again during this audit.

If the list is empty, skip this step.

## 3.3 Adjudicate `needs_ai_review` Findings

The 11 AI-grounded rules are: **DES-CONS-01 (visual), DES-PRIM-01, DES-HIER-02, DES-FEED-01, DES-FEED-02, DES-NAV-01, DES-NAV-02, DES-COPY-01, DES-COPY-02, DES-ICON-01, DES-MOTI-01**.

For each finding where `needs_ai_review` is true:

1. Open `evidence.crop_path` (image on disk).
2. Apply `finding.ai_prompt` literally -- it is a specific question written by the CLI. Do not paraphrase or expand it.
3. Fill `finding.ai_verdict`:
   ```json
   {
     "passed": true,
     "confidence": 0.0,
     "rationale": ""
   }
   ```
   - `passed` (bool): whether the rule passes based on what is visible in the crop
   - `confidence` (float 0.0-1.0): your confidence in the verdict
   - `rationale` (str): concise explanation citing visible evidence

## 3.4 Persist Merged Report

Write the merged report to `<out>/report-final.json`. Phase 4 reads exclusively from this file.
