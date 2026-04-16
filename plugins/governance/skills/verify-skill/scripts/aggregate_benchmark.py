"""Aggregate grading results into benchmark summary.

Reads individual grading YAML reports and produces a consolidated benchmark.
Can be run standalone: python aggregate_benchmark.py /path/to/results/
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import yaml

from utils import read_yaml

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def load_grading_results(results_dir: str) -> list[dict]:
    """Load all .yaml grading result files from a directory.

    Args:
        results_dir: Absolute path to the directory containing YAML results.

    Returns:
        List of parsed grading result dicts.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    dirpath = Path(results_dir)
    if not dirpath.is_dir():
        raise FileNotFoundError(f"Results directory not found: {results_dir}")

    results: list[dict] = []
    for yaml_file in sorted(dirpath.glob("*.yaml")):
        try:
            data = read_yaml(str(yaml_file))
            results.append(data)
        except Exception as exc:
            print(f"Warning: failed to load {yaml_file}: {exc}", file=sys.stderr)
    return results


def aggregate(results: list[dict]) -> dict:
    """Aggregate individual grading results into a benchmark summary.

    Expects each result dict to follow the grading report schema from
    ``references/schemas.md`` (fields: ``test_name``, ``grade``,
    ``level_1.expectations_met``, ``level_1.expectations_total``).

    Args:
        results: List of per-test-case grading dicts.

    Returns:
        Benchmark summary dict.
    """
    total = len(results)
    if total == 0:
        return {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "partial": 0,
            "pass_rate": 0.0,
            "by_test": [],
            "common_failures": [],
        }

    grade_counts = Counter(r.get("grade", "fail") for r in results)
    passed = grade_counts.get("pass", 0)
    failed = grade_counts.get("fail", 0)
    partial = grade_counts.get("partial", 0)
    pass_rate = passed / total if total > 0 else 0.0

    by_test: list[dict] = []
    failure_reasons: list[str] = []

    for r in results:
        level_1 = r.get("level_1", {})
        met = level_1.get("expectations_met", 0)
        exp_total = level_1.get("expectations_total", 0)

        by_test.append(
            {
                "name": r.get("test_name", "unknown"),
                "grade": r.get("grade", "fail"),
                "expectations_met": met,
                "expectations_total": exp_total,
            }
        )

        # Collect unmet expectations as failure reasons.
        details = level_1.get("details", [])
        for detail in details:
            if detail.get("result") in ("not_met", "partial"):
                reason = detail.get("expectation", "unknown expectation")
                failure_reasons.append(reason)

    # Most common failure reasons.
    reason_counts = Counter(failure_reasons)
    common_failures = [reason for reason, _ in reason_counts.most_common(5)]

    return {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "partial": partial,
        "pass_rate": round(pass_rate, 4),
        "by_test": by_test,
        "common_failures": common_failures,
    }


def format_report(benchmark: dict) -> str:
    """Format a benchmark summary dict as a YAML string.

    Args:
        benchmark: The aggregated benchmark dict.

    Returns:
        YAML-formatted string.
    """
    return yaml.safe_dump(benchmark, default_flow_style=False, sort_keys=False)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate grading results into benchmark summary."
    )
    parser.add_argument(
        "results_dir", help="Path to directory containing grading YAML files"
    )
    args = parser.parse_args()

    results = load_grading_results(args.results_dir)
    benchmark = aggregate(results)
    print(format_report(benchmark))

    # Exit 1 if pass_rate < 1.0 (not all tests passed).
    sys.exit(0 if benchmark["pass_rate"] >= 1.0 else 1)


if __name__ == "__main__":
    main()
