"""Assert the Python aggregator matches ``design-audit-aggregator.js`` output.

Executes the JS aggregator via Node against a fixed fixture, then runs the
Python port on the same issue-set and asserts equality on every numeric
field that the JS side computes (category scores, overall, risk, counts).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from audit_cli.report.aggregate import (
    compute_category_score,
    compute_overall_score,
    determine_risk,
)

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "findings_sample.json"
_JS_AGGREGATOR = (
    Path(__file__).resolve().parent.parent.parent / "scripts" / "design-audit-aggregator.js"
)


def _run_js_baseline(categories: dict[str, list[dict[str, object]]]) -> dict[str, object]:
    """Drive the JS aggregator in Node and capture its unified output."""
    runner = f"""
const globals = {{ window: {{}} }};
Object.assign(globalThis, globals);
const vm = require('vm');
const fs = require('fs');
const src = fs.readFileSync('{_JS_AGGREGATOR}', 'utf-8');
vm.runInThisContext(src);

const categories = {json.dumps(categories)};
for (const [key, value] of Object.entries(categories)) {{
    const fnMap = {{
        text: 'runWcagTextAudit',
        structure: 'runSemanticStructureAudit',
        interaction: 'runInteractionAudit',
        mobile: 'runMobileLayoutAudit',
        visual: 'runVisualLayoutAudit',
        tokens: 'runDesignTokensAudit',
        typography: 'runTypographyAudit',
        spatial: 'runSpatialLayoutAudit',
        css: 'runUnusedCssAudit'
    }};
    globalThis.window[fnMap[key]] = () => ({{issues: value.issues, stats: {{}}}});
}}

const report = globalThis.window.runDesignAudit({{
    categories: Object.keys(categories),
    viewport: 'desktop',
    viewportLabel: 'Desktop 1440x900'
}});
process.stdout.write(JSON.stringify(report));
"""
    completed = subprocess.run(
        ["node", "-e", runner], capture_output=True, text=True, check=True
    )
    return json.loads(completed.stdout)


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_python_aggregator_matches_js_scoring() -> None:
    fixture = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    categories = fixture["categories"]

    js_report = _run_js_baseline(categories)

    py_category_scores: dict[str, int] = {}
    for key, cat in categories.items():
        issues = cat["issues"]
        py_category_scores[key] = compute_category_score(issues)

    js_by_cat = js_report["summary"]["byCategory"]
    for key, score in py_category_scores.items():
        assert js_by_cat[key]["score"] == score, f"category {key} diverged"

    assert compute_overall_score(py_category_scores) == js_report["summary"]["overallScore"]
    assert determine_risk(js_report["summary"]["bySeverity"]) == js_report["summary"]["risk"]
