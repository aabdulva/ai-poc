import json
from pathlib import Path

from src.llm.analyzer import TestLogAnalyzer
from src.retrieval.hybrid_search import HybridSearch


def load_test_cases():
    """
    Load evaluation test cases from evaluation_cases.json.
    """

    path = (
        Path(__file__).parent
        / "evaluation_cases.json"
    )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def evaluate():

    test_cases = load_test_cases()

    analyzer = TestLogAnalyzer()
    search = HybridSearch()

    results = []

    print()
    print("========================================")
    print("AI AGENT POC EVALUATION")
    print("========================================")
    print()

    for case in test_cases:

        print(
            f"Running {case['id']}: "
            f"{case['name']}"
        )

        # --------------------------------------
        # Step 1: Analyze test log with LLM
        # --------------------------------------

        analysis = analyzer.analyze(
            case["test_log"]
        )

        # --------------------------------------
        # Step 2: Hybrid retrieval
        # --------------------------------------

        ranked_results = search.search(
            analysis,
            top_k=5
        )

        # --------------------------------------
        # Step 3: Get top result
        # --------------------------------------

        if ranked_results:

            top_result = ranked_results[0]

            retrieved_id = top_result["id"]

            retrieved_score = (
                top_result["final_score"]
            )

        else:

            retrieved_id = "NO_RESULT"
            retrieved_score = 0.0

        # --------------------------------------
        # Step 4: Expected results
        # --------------------------------------

        expected_ids = case.get(
            "expected_ids",
            []
        )

        # --------------------------------------
        # Step 5: Determine PASS / FAIL
        # --------------------------------------

        if not expected_ids:

            # This is a NO_MATCH test case.
            #
            # We currently use a simple threshold
            # for the evaluation baseline.
            #
            # This is NOT our final production
            # relevance logic.

            passed = (
                retrieved_score < 0.20
            )

            expected_display = "NO_MATCH"

        else:

            # One or more historical records are
            # considered acceptable answers.

            passed = (
                retrieved_id in expected_ids
            )

            expected_display = ", ".join(
                expected_ids
            )

        # --------------------------------------
        # Step 6: Store result
        # --------------------------------------

        results.append(
            {
                "id": case["id"],
                "name": case["name"],
                "expected": expected_display,
                "retrieved": retrieved_id,
                "score": retrieved_score,
                "passed": passed,
            }
        )

        # --------------------------------------
        # Step 7: Print test result
        # --------------------------------------

        print(
            f"  Expected:  "
            f"{expected_display}"
        )

        print(
            f"  Retrieved: "
            f"{retrieved_id}"
        )

        print(
            f"  Score:     "
            f"{retrieved_score:.3f}"
        )

        print(
            f"  Result:    "
            f"{'PASS' if passed else 'FAIL'}"
        )

        print()

    # ------------------------------------------
    # Calculate accuracy
    # ------------------------------------------

    total = len(results)

    passed_count = sum(
        1
        for result in results
        if result["passed"]
    )

    failed_count = (
        total - passed_count
    )

    accuracy = (
        passed_count / total * 100
        if total
        else 0
    )

    # ------------------------------------------
    # Summary
    # ------------------------------------------

    print("========================================")
    print("EVALUATION SUMMARY")
    print("========================================")
    print()

    print(
        f"Total tests:     {total}"
    )

    print(
        f"Passed:          {passed_count}"
    )

    print(
        f"Failed:          {failed_count}"
    )

    print(
        f"Top-1 Accuracy:  "
        f"{accuracy:.1f}%"
    )

    print()

    # ------------------------------------------
    # Detailed results
    # ------------------------------------------

    print(
        "Detailed results:"
    )

    print()

    print(
        f"{'Test':<12}"
        f"{'Expected':<25}"
        f"{'Retrieved':<15}"
        f"{'Score':<10}"
        f"Result"
    )

    print("-" * 80)

    for result in results:

        print(
            f"{result['id']:<12}"
            f"{result['expected']:<25}"
            f"{result['retrieved']:<15}"
            f"{result['score']:<10.3f}"
            f"{'PASS' if result['passed'] else 'FAIL'}"
        )


if __name__ == "__main__":
    evaluate()