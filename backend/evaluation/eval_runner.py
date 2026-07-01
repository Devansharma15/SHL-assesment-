"""Evaluation runner for the SHL Assessment Recommender."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

import httpx

from evaluation.metrics import evaluate_test_case

logger = logging.getLogger(__name__)

TEST_CASES_PATH = Path(__file__).resolve().parent / "test_cases.json"
CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "shl_product_catalog.json"


async def run_evaluation(
    api_url: str = "http://localhost:8000",
    test_cases_path: Path | None = None,
) -> dict:
    """Run the full evaluation suite against a running API instance.

    Args:
        api_url: Base URL of the running API.
        test_cases_path: Path to test cases JSON.

    Returns:
        Dict with overall results and per-test-case details.
    """
    tc_path = test_cases_path or TEST_CASES_PATH

    # Load test cases
    with open(tc_path, encoding="utf-8") as f:
        test_cases = json.load(f)

    # Load catalog for hallucination checking
    with open(CATALOG_PATH, encoding="utf-8") as f:
        catalog = json.load(f)
    catalog_names = {a["name"].lower() for a in catalog}

    results = []
    passed = 0
    failed = 0

    async with httpx.AsyncClient(timeout=35.0) as client:
        for tc in test_cases:
            print(f"\n--- Running: {tc['id']} - {tc['name']} ---")

            try:
                response = await client.post(
                    f"{api_url}/chat",
                    json={"messages": tc["messages"]},
                )

                if response.status_code == 200:
                    data = response.json()
                else:
                    data = {
                        "reply": f"HTTP {response.status_code}",
                        "recommendations": [],
                        "end_of_conversation": False,
                    }

                # Evaluate
                result = evaluate_test_case(tc, data, catalog_names)
                results.append(result)

                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                print(f"  {status}")
                print(f"  Recommendations: {result['recommendation_count']}")
                print(f"  Recall@10: {result['recall_at_10']:.2f}")
                print(f"  Hallucination: {result['hallucination_rate']:.2f}")

                if result["passed"]:
                    passed += 1
                else:
                    failed += 1

            except Exception as e:
                print(f"  ❌ ERROR: {e}")
                failed += 1
                results.append(
                    {
                        "test_id": tc["id"],
                        "test_name": tc["name"],
                        "passed": False,
                        "error": str(e),
                    }
                )

    # Summary
    total = passed + failed
    print("\n" + "=" * 60)
    print(f"EVALUATION RESULTS: {passed}/{total} passed ({100 * passed / total:.0f}%)")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print("=" * 60)

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / total if total > 0 else 0,
        "details": results,
    }


def main():
    """CLI entry point for running evaluation."""
    logging.basicConfig(level=logging.INFO)

    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    print(f"Running evaluation against: {api_url}")

    results = asyncio.run(run_evaluation(api_url))

    # Save results
    output_path = Path(__file__).resolve().parent / "eval_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {output_path}")


if __name__ == "__main__":
    main()
