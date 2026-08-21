from src.retrieval.vector_store import VectorStore


def main():

    vector_store = VectorStore()

    query = """
    The camera fails to initialize when the vehicle wakes up.
    The service becomes unavailable during startup.
    """

    print()
    print("======================================")
    print("Semantic Search")
    print("======================================")

    print()
    print("Query:")
    print(query)

    results = vector_store.search(
        query=query,
        top_k=5
    )

    print()
    print("Results:")
    print()

    ids = results["ids"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    for i in range(len(ids)):

        similarity = max(
            0,
            (1 - distances[i]) * 100
        )

        print("--------------------------------------")

        print(f"Rank:       {i + 1}")
        print(f"ID:         {ids[i]}")
        print(f"Similarity: {similarity:.2f}%")

        print(
            f"Source:     "
            f"{metadatas[i]['source']}"
        )

        print(
            f"Title:      "
            f"{metadatas[i]['title']}"
        )

        print(
            f"Component:  "
            f"{metadatas[i]['component']}"
        )

        print(
            f"Software:   "
            f"{metadatas[i]['software_version']}"
        )


if __name__ == "__main__":
    main()