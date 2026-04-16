"""Optimize skill description for better trigger accuracy.

Uses train/test split (60/40) to iteratively improve description
without overfitting to specific queries.

Can be run standalone: python run_trigger_loop.py /path/to/SKILL.md [--max-iterations 5]
"""

from __future__ import annotations

import argparse
import random
import re
import sys

import yaml

from run_trigger_eval import _tokenize, load_trigger_queries, test_trigger
from utils import get_skill_dir, parse_frontmatter

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def split_train_test(
    queries: dict, train_ratio: float = 0.6
) -> tuple[dict, dict]:
    """Split trigger queries into train and test sets.

    Uses a deterministic seed for reproducibility.

    Args:
        queries: Dict with ``should_trigger`` and ``should_not_trigger`` lists.
        train_ratio: Fraction of queries to assign to the training set.

    Returns:
        Tuple of (train_queries, test_queries), each with the same structure.
    """
    rng = random.Random(42)

    def _split(items: list[str]) -> tuple[list[str], list[str]]:
        shuffled = list(items)
        rng.shuffle(shuffled)
        split_idx = max(1, int(len(shuffled) * train_ratio))
        return shuffled[:split_idx], shuffled[split_idx:]

    st_train, st_test = _split(queries.get("should_trigger", []))
    snt_train, snt_test = _split(queries.get("should_not_trigger", []))

    train = {"should_trigger": st_train, "should_not_trigger": snt_train}
    test = {"should_trigger": st_test, "should_not_trigger": snt_test}
    return train, test


def evaluate_description(description: str, queries: dict) -> float:
    """Calculate trigger accuracy for a description against a query set.

    Args:
        description: The skill description text to evaluate.
        queries: Dict with ``should_trigger`` and ``should_not_trigger`` lists.

    Returns:
        Accuracy as a float between 0.0 and 1.0.
    """
    total = 0
    correct = 0

    for query in queries.get("should_trigger", []):
        total += 1
        if test_trigger(description, query):
            correct += 1

    for query in queries.get("should_not_trigger", []):
        total += 1
        if not test_trigger(description, query):
            correct += 1

    return correct / total if total > 0 else 0.0


def suggest_improvement(
    current_description: str,
    train_queries: dict,
    train_accuracy: float,
) -> str:
    """Generate an improved description based on training set failures.

    Analyses which queries failed to match (or falsely matched) and adjusts
    the description's keyword set and ``Use when`` clause accordingly.

    This is a heuristic optimizer -- it cannot replace a language-model-driven
    rewrite, but it can make measurable incremental improvements.

    Args:
        current_description: The current skill description.
        train_queries: Training query set.
        train_accuracy: Current accuracy on the training set.

    Returns:
        An improved description string.
    """
    # Identify missed triggers (should trigger but did not).
    missed: list[str] = []
    for query in train_queries.get("should_trigger", []):
        if not test_trigger(current_description, query):
            missed.append(query)

    # Identify false positives (should not trigger but did).
    false_positives: list[str] = []
    for query in train_queries.get("should_not_trigger", []):
        if test_trigger(current_description, query):
            false_positives.append(query)

    desc_tokens = _tokenize(current_description)

    # Strategy 1: Add keywords from missed trigger queries to increase recall.
    keywords_to_add: set[str] = set()
    for query in missed:
        query_tokens = _tokenize(query)
        # Find significant query tokens not already in the description.
        novel_tokens = query_tokens - desc_tokens
        # Only add tokens that appear in at least one missed query.
        keywords_to_add.update(novel_tokens)

    # Strategy 2: Identify tokens unique to false-positive queries that we
    # should avoid amplifying.  We do not remove existing description tokens,
    # but we avoid adding these.
    fp_tokens: set[str] = set()
    for query in false_positives:
        fp_tokens.update(_tokenize(query))

    safe_keywords = keywords_to_add - fp_tokens

    # Build improved description.  Preserve the original structure but enrich
    # the ``Use when`` clause with additional trigger keywords.
    improved = current_description

    # If there is an existing "Use when" clause, extend it.
    use_when_match = re.search(r"([Uu]se when\s+.+?)(\.|$)", improved)
    if use_when_match and safe_keywords:
        clause = use_when_match.group(1)
        # Append a selection of the most relevant new keywords.
        extras = sorted(safe_keywords)[:5]  # Cap additions per iteration.
        extended_clause = clause + ", " + ", ".join(extras)
        improved = improved.replace(clause, extended_clause)
    elif safe_keywords:
        # No "Use when" clause -- append one.
        extras = sorted(safe_keywords)[:5]
        improved = improved.rstrip(". ") + ". Use when " + ", ".join(extras) + "."

    # If no improvement was possible (no safe keywords), try minor rephrasing
    # by ensuring the description starts with a verb phrase.
    if improved == current_description and missed:
        # Extract the dominant action verb from missed queries.
        for query in missed:
            tokens = _tokenize(query)
            action_candidates = tokens - desc_tokens
            if action_candidates:
                verb = sorted(action_candidates)[0]
                improved = improved.rstrip(". ") + f", {verb}."
                break

    return improved


def optimize(skill_path: str, max_iterations: int = 5) -> dict:
    """Run the description optimization loop.

    1. Load current description and trigger queries.
    2. Split queries 60/40 into train/test.
    3. Iteratively improve the description, stopping early when gains plateau.

    Args:
        skill_path: Absolute path to the SKILL.md file.
        max_iterations: Maximum number of improvement iterations.

    Returns:
        Optimization report dict matching the schema in schemas.md.
    """
    frontmatter = parse_frontmatter(skill_path)
    original_description = str(frontmatter.get("description", ""))
    skill_dir = get_skill_dir(skill_path)
    queries = load_trigger_queries(skill_dir)

    train, test = split_train_test(queries)

    original_train_acc = evaluate_description(original_description, train)
    original_test_acc = evaluate_description(original_description, test)

    current_description = original_description
    current_train_acc = original_train_acc
    best_test_acc = original_test_acc

    history: list[dict] = [
        {
            "iteration": 0,
            "description": original_description,
            "train_acc": round(original_train_acc, 4),
            "test_acc": round(original_test_acc, 4),
        }
    ]

    no_improvement_streak = 0
    iterations_run = 0

    for i in range(1, max_iterations + 1):
        iterations_run = i

        candidate = suggest_improvement(current_description, train, current_train_acc)
        candidate_train_acc = evaluate_description(candidate, train)

        # Check for meaningful train improvement (> 5%).
        train_delta = candidate_train_acc - current_train_acc
        if train_delta > 0.05:
            # Evaluate on test set to check generalisation.
            candidate_test_acc = evaluate_description(candidate, test)
            test_delta = candidate_test_acc - best_test_acc

            history.append(
                {
                    "iteration": i,
                    "description": candidate,
                    "train_acc": round(candidate_train_acc, 4),
                    "test_acc": round(candidate_test_acc, 4),
                }
            )

            if test_delta > 0:
                # Genuine improvement -- keep candidate.
                current_description = candidate
                current_train_acc = candidate_train_acc
                best_test_acc = candidate_test_acc
                no_improvement_streak = 0
            else:
                # Train improved but test did not -- possible overfitting.
                no_improvement_streak += 1
        else:
            # No meaningful train improvement.
            history.append(
                {
                    "iteration": i,
                    "description": candidate,
                    "train_acc": round(candidate_train_acc, 4),
                    "test_acc": round(evaluate_description(candidate, test), 4),
                }
            )
            no_improvement_streak += 1

        if no_improvement_streak >= 2:
            break

    final_test_acc = evaluate_description(current_description, test)
    improvement = final_test_acc - original_test_acc

    return {
        "original_description": original_description,
        "optimized_description": current_description,
        "original_train_accuracy": round(original_train_acc, 4),
        "optimized_train_accuracy": round(current_train_acc, 4),
        "original_test_accuracy": round(original_test_acc, 4),
        "optimized_test_accuracy": round(final_test_acc, 4),
        "improvement": round(improvement, 4),
        "iterations_run": iterations_run,
        "history": history,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Optimize skill description for better trigger accuracy."
    )
    parser.add_argument("skill_path", help="Path to the SKILL.md file")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum optimization iterations (default: 5)",
    )
    args = parser.parse_args()

    result = optimize(args.skill_path, max_iterations=args.max_iterations)

    print(yaml.safe_dump(result, default_flow_style=False, sort_keys=False))

    # Exit 0 if any improvement was achieved, 1 otherwise.
    sys.exit(0 if result["improvement"] > 0 else 1)


if __name__ == "__main__":
    main()
