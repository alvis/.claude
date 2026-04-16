"""Test skill trigger accuracy by evaluating description matching.

Tests whether a skill's description correctly triggers for matching queries
and doesn't trigger for non-matching queries.

Can be run standalone: python run_trigger_eval.py /path/to/SKILL.md
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys

import yaml

from utils import get_skill_dir, load_evals, parse_frontmatter

# ---------------------------------------------------------------------------
# Stop-words excluded from keyword overlap scoring
# ---------------------------------------------------------------------------

_STOP_WORDS: set[str] = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "must", "can", "could", "of", "in", "to",
    "for", "with", "on", "at", "from", "by", "about", "as", "into",
    "through", "during", "before", "after", "above", "below", "between",
    "out", "off", "over", "under", "again", "further", "then", "once",
    "and", "but", "or", "nor", "not", "so", "yet", "both", "either",
    "neither", "each", "every", "all", "any", "few", "more", "most",
    "other", "some", "such", "no", "only", "own", "same", "than", "too",
    "very", "just", "because", "if", "when", "while", "that", "this",
    "these", "those", "it", "its", "i", "me", "my", "we", "our", "you",
    "your", "he", "him", "his", "she", "her", "they", "them", "their",
    "what", "which", "who", "whom", "how", "where", "why",
}

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def load_trigger_queries(skill_dir: str) -> dict:
    """Load should_trigger and should_not_trigger lists from evals.yaml.

    Args:
        skill_dir: Absolute path to the skill directory.

    Returns:
        Dict with ``should_trigger`` and ``should_not_trigger`` lists.

    Raises:
        FileNotFoundError: If evals.yaml does not exist.
        ValueError: If trigger_eval section is missing.
    """
    evals = load_evals(skill_dir)
    if evals is None:
        raise FileNotFoundError(f"No evals/evals.yaml found in {skill_dir}")

    trigger_eval = evals.get("trigger_eval")
    if not trigger_eval:
        raise ValueError("evals.yaml has no 'trigger_eval' section")

    return {
        "should_trigger": trigger_eval.get("should_trigger", []),
        "should_not_trigger": trigger_eval.get("should_not_trigger", []),
    }


def _tokenize(text: str) -> set[str]:
    """Lowercase, split on non-alpha, remove stop words."""
    words = set(re.findall(r"[a-z]+", text.lower()))
    return words - _STOP_WORDS


def test_trigger(description: str, query: str) -> bool:
    """Test if a skill description would trigger for a given query.

    Uses a heuristic approach combining:
    1. Significant-word overlap between description and query.
    2. ``Use when`` clause intent matching against query keywords.

    The threshold is calibrated to be moderately permissive so that related
    queries trigger while clearly unrelated ones do not.

    Args:
        description: The skill's frontmatter description text.
        query: A user query to test against.

    Returns:
        ``True`` if the description is deemed to match the query.
    """
    desc_tokens = _tokenize(description)
    query_tokens = _tokenize(query)

    if not desc_tokens or not query_tokens:
        return False

    # Overlap ratio relative to the query (how much of the query is covered).
    overlap = desc_tokens & query_tokens
    query_coverage = len(overlap) / len(query_tokens) if query_tokens else 0.0

    # Also measure overlap relative to the description's significant terms.
    desc_coverage = len(overlap) / len(desc_tokens) if desc_tokens else 0.0

    # Combined score: favour query coverage but reward description coverage too.
    score = 0.6 * query_coverage + 0.4 * desc_coverage

    # Extract the "Use when" clause if present -- it narrows trigger intent.
    use_when_match = re.search(r"[Uu]se when\s+(.+?)(?:\.|$)", description)
    if use_when_match:
        use_when_tokens = _tokenize(use_when_match.group(1))
        if use_when_tokens:
            uw_overlap = use_when_tokens & query_tokens
            uw_score = len(uw_overlap) / len(use_when_tokens)
            # Boost score when the "Use when" clause aligns well.
            score = max(score, uw_score * 0.85)

    return score >= 0.25


def evaluate_triggers(skill_path: str) -> dict:
    """Run full trigger evaluation using heuristic matching.

    Args:
        skill_path: Absolute path to the SKILL.md file.

    Returns:
        Trigger evaluation report dict matching the schema in schemas.md.
    """
    frontmatter = parse_frontmatter(skill_path)
    description = str(frontmatter.get("description", ""))
    skill_dir = get_skill_dir(skill_path)
    queries = load_trigger_queries(skill_dir)

    should_trigger: list[str] = queries.get("should_trigger", [])
    should_not_trigger: list[str] = queries.get("should_not_trigger", [])

    details: list[dict] = []
    correct_triggers = 0
    false_triggers = 0

    for query in should_trigger:
        actual = test_trigger(description, query)
        correct = actual is True
        if correct:
            correct_triggers += 1
        details.append(
            {
                "query": query,
                "expected": True,
                "actual": actual,
                "correct": correct,
            }
        )

    for query in should_not_trigger:
        actual = test_trigger(description, query)
        correct = actual is False
        if not correct:
            false_triggers += 1
        details.append(
            {
                "query": query,
                "expected": False,
                "actual": actual,
                "correct": correct,
            }
        )

    total_st = len(should_trigger)
    total_snt = len(should_not_trigger)

    return {
        "trigger_rate": round(correct_triggers / total_st, 4) if total_st else 0.0,
        "false_positive_rate": round(false_triggers / total_snt, 4) if total_snt else 0.0,
        "total_should_trigger": total_st,
        "correct_triggers": correct_triggers,
        "total_should_not_trigger": total_snt,
        "false_triggers": false_triggers,
        "details": details,
    }


def evaluate_triggers_with_cli(skill_path: str) -> dict | None:
    """Enhanced trigger evaluation using ``claude -p`` CLI.

    This is slower but more accurate than the heuristic approach because it
    uses the actual language model to judge trigger matches.

    Args:
        skill_path: Absolute path to the SKILL.md file.

    Returns:
        Trigger evaluation report dict, or ``None`` if the CLI is unavailable.
    """
    if not shutil.which("claude"):
        return None

    frontmatter = parse_frontmatter(skill_path)
    description = str(frontmatter.get("description", ""))
    skill_dir = get_skill_dir(skill_path)
    queries = load_trigger_queries(skill_dir)

    should_trigger: list[str] = queries.get("should_trigger", [])
    should_not_trigger: list[str] = queries.get("should_not_trigger", [])

    details: list[dict] = []
    correct_triggers = 0
    false_triggers = 0

    prompt_template = (
        "Given this skill description:\n"
        '"{description}"\n\n'
        "Would this user query trigger this skill? Answer ONLY 'yes' or 'no'.\n"
        'Query: "{query}"'
    )

    all_queries = [(q, True) for q in should_trigger] + [
        (q, False) for q in should_not_trigger
    ]

    for query, expected in all_queries:
        prompt = prompt_template.format(description=description, query=query)
        try:
            result = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=30,
            )
            answer = result.stdout.strip().lower()
            actual = answer.startswith("yes")
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            # Fall back to heuristic on CLI failure.
            actual = test_trigger(description, query)

        correct = actual == expected
        if expected and actual:
            correct_triggers += 1
        if not expected and actual:
            false_triggers += 1

        details.append(
            {
                "query": query,
                "expected": expected,
                "actual": actual,
                "correct": correct,
            }
        )

    total_st = len(should_trigger)
    total_snt = len(should_not_trigger)

    return {
        "trigger_rate": round(correct_triggers / total_st, 4) if total_st else 0.0,
        "false_positive_rate": round(false_triggers / total_snt, 4) if total_snt else 0.0,
        "total_should_trigger": total_st,
        "correct_triggers": correct_triggers,
        "total_should_not_trigger": total_snt,
        "false_triggers": false_triggers,
        "details": details,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test skill trigger accuracy by evaluating description matching."
    )
    parser.add_argument("skill_path", help="Path to the SKILL.md file")
    parser.add_argument(
        "--use-cli",
        action="store_true",
        default=False,
        help="Use 'claude -p' for more accurate trigger testing (slower)",
    )
    args = parser.parse_args()

    if args.use_cli:
        result = evaluate_triggers_with_cli(args.skill_path)
        if result is None:
            print(
                "Error: 'claude' CLI not found. Falling back to heuristic mode.",
                file=sys.stderr,
            )
            result = evaluate_triggers(args.skill_path)
    else:
        result = evaluate_triggers(args.skill_path)

    print(yaml.safe_dump(result, default_flow_style=False, sort_keys=False))

    # Pass if trigger_rate >= 0.8 and false_positive_rate <= 0.2.
    trigger_ok = result["trigger_rate"] >= 0.8
    fp_ok = result["false_positive_rate"] <= 0.2
    sys.exit(0 if trigger_ok and fp_ok else 1)


if __name__ == "__main__":
    main()
