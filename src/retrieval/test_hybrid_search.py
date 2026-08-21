from src.llm.analyzer import TestLogAnalyzer
from src.retrieval.hybrid_search import HybridSearch


def main():

    test_log = """
    ECU: CAM
    Component: CameraService
    State: WAKEUP

    ERROR CAM_1032

    Camera service failed to initialize.
    CAN communication timeout.
    Retry count exceeded.
    """

    # ------------------------------------------
    # Analyze test log
    # ------------------------------------------

    analyzer = TestLogAnalyzer()

    analysis = analyzer.analyze(
        test_log
    )

    # ------------------------------------------
    # Hybrid search
    # ------------------------------------------

    search = HybridSearch()

    results = search.search(
        analysis,
        top_k=5,
    )

    # ------------------------------------------
    # Display results
    # ------------------------------------------

    print()
    print("======================================")
    print("HYBRID SEARCH")
    print("======================================")
    print()

    for index, result in enumerate(
        results
    ):

        print("--------------------------------------")

        print(
            f"Rank:              {index + 1}"
        )

        print(
            f"ID:                "
            f"{result['id']}"
        )

        print(
            f"Source:            "
            f"{result['source']}"
        )

        print(
            f"Title:             "
            f"{result['title']}"
        )

        print(
            f"Affected software: "
            f"{result['affected_software_version']}"
        )

        print(
            f"Fix software:      "
            f"{result['fix_software_version']}"
        )

        print(
            f"Semantic score:    "
            f"{result['semantic_score']:.3f}"
        )

        print(
            f"Component match:   "
            f"{result['component_match']:.3f}"
        )

        print(
            f"Error match:       "
            f"{result['error_match']:.3f}"
        )

        print(
            f"Symptom match:     "
            f"{result['symptom_match']:.3f}"
        )

        print(
            f"FINAL SCORE:       "
            f"{result['final_score']:.3f}"
        )


if __name__ == "__main__":
    main()