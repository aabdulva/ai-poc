from src.llm.analyzer import TestLogAnalyzer
from src.llm.response_generator import ResponseGenerator
from src.retrieval.hybrid_search import HybridSearch
from src.retrieval.query_builder import build_search_query


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

    print()
    print("======================================")
    print("AI Test Failure Analysis")
    print("======================================")

    # ------------------------------------------
    # Step 1: Analyze test log
    # ------------------------------------------

    print()
    print("Step 1: Analyzing test log...")

    analyzer = TestLogAnalyzer()
    analysis = analyzer.analyze(test_log)

    print()
    print("Component:", analysis.component)
    print("Error codes:", analysis.error_codes)
    print("Symptoms:", analysis.symptoms)
    print("Operating condition:", analysis.operating_condition)
    print("Software version:", analysis.software_version)

    # ------------------------------------------
    # Step 2: Build search query
    # ------------------------------------------

    search_query = build_search_query(analysis)

    print()
    print("Step 2: Search query:")
    print(search_query)

    # ------------------------------------------
    # Step 3: Hybrid retrieval
    # ------------------------------------------

    print()
    print("Step 3: Hybrid historical search...")

    hybrid_search = HybridSearch()
    ranked_results = hybrid_search.search(analysis, top_k=5)

    print()
    print("Retrieved historical records:")
    print()

    for index, result in enumerate(ranked_results):

        print("--------------------------------------")
        print(f"Rank: {index + 1}")
        print(f"ID: {result['id']}")
        print(f"Source: {result['source']}")
        print(f"Title: {result['title']}")
        print(f"Affected software: {result['affected_software_version']}")
        print(f"Fix software: {result['fix_software_version']}")
        print(f"Final score: {result['final_score']:.3f}")

    # ------------------------------------------
    # Convert to ResponseGenerator format
    # ------------------------------------------

    search_results = {
        "ids": [[r["id"] for r in ranked_results]],
        "documents": [[r["document"] for r in ranked_results]],
        "metadatas": [[
            {
                "source": r["source"],
                "title": r["title"],
                "component": r["component"],
                "affected_software_version": r["affected_software_version"],
                "fix_software_version": r["fix_software_version"],
            }
            for r in ranked_results
        ]],
        "distances": [[r["distance"] for r in ranked_results]],
    }

    # ------------------------------------------
    # Step 4: Generate grounded response
    # ------------------------------------------

    print()
    print("Step 4: Generating evidence-grounded analysis...")

    generator = ResponseGenerator()

    answer = generator.generate(
        test_log=test_log,
        analysis=analysis,
        search_results=search_results,
    )

    # ------------------------------------------
    # Step 5: Final output
    # ------------------------------------------

    print()
    print("======================================")
    print("FINAL ENGINEERING ANALYSIS")
    print("======================================")
    print()

    print(answer)


if __name__ == "__main__":
    main()