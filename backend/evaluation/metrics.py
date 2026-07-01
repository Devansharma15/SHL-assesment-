"""Evaluation metrics for the SHL Assessment Recommender."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def recall_at_k(
    recommended_names: list[str],
    expected_keywords: list[str],
    k: int = 10,
) -> float:
    """Calculate Recall@K: fraction of expected keywords found in recommendations.

    Args:
        recommended_names: List of recommended assessment names.
        expected_keywords: List of expected keyword substrings.
        k: Only consider the top-K recommendations.

    Returns:
        Recall score between 0.0 and 1.0.
    """
    if not expected_keywords:
        return 1.0  # No expectations = perfect recall

    top_k_names = " ".join(recommended_names[:k]).lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in top_k_names)
    return hits / len(expected_keywords)


def hallucination_rate(
    recommended_names: list[str],
    catalog_names: set[str],
) -> float:
    """Calculate the hallucination rate: fraction of recommendations not in the catalog.

    Args:
        recommended_names: List of recommended assessment names.
        catalog_names: Set of all valid assessment names (lowercased).

    Returns:
        Hallucination rate between 0.0 and 1.0.
    """
    if not recommended_names:
        return 0.0

    hallucinated = 0
    for name in recommended_names:
        name_lower = name.lower()
        # Check if name matches any catalog entry (exact or partial)
        if not any(cat_name in name_lower or name_lower in cat_name for cat_name in catalog_names):
            hallucinated += 1
            logger.warning("Hallucinated assessment: '%s'", name)

    return hallucinated / len(recommended_names)


def schema_valid(response: dict) -> bool:
    """Check if the response has the required schema fields.

    Args:
        response: The API response dict.

    Returns:
        True if schema is valid.
    """
    required_fields = {"reply", "recommendations", "end_of_conversation"}
    if not all(field in response for field in required_fields):
        return False

    if not isinstance(response["reply"], str):
        return False

    if not isinstance(response["recommendations"], list):
        return False

    if not isinstance(response["end_of_conversation"], bool):
        return False

    # Validate each recommendation
    for rec in response["recommendations"]:
        if not isinstance(rec, dict):
            return False
        if "name" not in rec or "url" not in rec:
            return False

    return True


def recommendation_count_valid(
    count: int,
    min_expected: int,
    max_expected: int,
) -> bool:
    """Check if recommendation count is within expected range.

    Args:
        count: Actual number of recommendations.
        min_expected: Minimum expected count.
        max_expected: Maximum expected count.

    Returns:
        True if count is within range.
    """
    return min_expected <= count <= max_expected


def evaluate_test_case(
    test_case: dict,
    response: dict,
    catalog_names: set[str],
) -> dict:
    """Evaluate a single test case against the API response.

    Args:
        test_case: Test case definition.
        response: API response dict.
        catalog_names: Set of valid catalog assessment names.

    Returns:
        Dict with metric scores and pass/fail status.
    """
    rec_names = [r.get("name", "") for r in response.get("recommendations", [])]
    rec_count = len(rec_names)

    results = {
        "test_id": test_case["id"],
        "test_name": test_case["name"],
        "schema_valid": schema_valid(response),
        "recommendation_count": rec_count,
        "count_valid": recommendation_count_valid(
            rec_count,
            test_case["min_recommendations"],
            test_case["max_recommendations"],
        ),
        "recall_at_10": recall_at_k(rec_names, test_case.get("expected_assessment_keywords", [])),
        "hallucination_rate": hallucination_rate(rec_names, catalog_names),
    }

    # Check refusal behavior
    if test_case.get("should_refuse"):
        results["refusal_correct"] = rec_count == 0
    else:
        results["refusal_correct"] = True  # Not a refusal test

    # Overall pass/fail
    results["passed"] = all(
        [
            results["schema_valid"],
            results["count_valid"],
            results["hallucination_rate"] == 0.0,
            results["refusal_correct"],
        ]
    )

    return results
