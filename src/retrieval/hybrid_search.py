import re

from src.retrieval.vector_store import VectorStore


SEMANTIC_WEIGHT = 0.50
COMPONENT_WEIGHT = 0.15
ERROR_CODE_WEIGHT = 0.20
SYMPTOM_WEIGHT = 0.15


def normalize_words(text: str) -> set[str]:
    """
    Convert text into a set of normalized words.
    """

    words = re.findall(
        r"[a-zA-Z0-9_]+",
        text.lower()
    )

    return set(words)


class HybridSearch:

    def __init__(self):

        self.vector_store = VectorStore()

    def search(
        self,
        analysis,
        top_k: int = 5,
    ):

        # ------------------------------------------
        # Build semantic query
        # ------------------------------------------

        query_parts = []

        if analysis.component:
            query_parts.append(
                analysis.component
            )

        if analysis.error_codes:
            query_parts.append(
                " ".join(
                    analysis.error_codes
                )
            )

        if analysis.symptoms:
            query_parts.extend(
                analysis.symptoms
            )

        if analysis.operating_condition:
            query_parts.append(
                analysis.operating_condition
            )

        query = " ".join(query_parts)

        # ------------------------------------------
        # Semantic search
        # ------------------------------------------

        results = self.vector_store.search(
            query=query,
            top_k=top_k,
        )

        ids = results["ids"][0]
        distances = results["distances"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        ranked_results = []

        # ------------------------------------------
        # Calculate hybrid score
        # ------------------------------------------

        for i in range(len(ids)):

            distance = distances[i]

            # --------------------------------------
            # Semantic similarity
            # --------------------------------------

            semantic_score = max(
                0,
                1 - distance
            )

            # --------------------------------------
            # Component match
            # --------------------------------------

            candidate_component = (
                metadatas[i]
                .get("component", "")
                .lower()
            )

            query_component = (
                analysis.component or ""
            ).lower()

            component_match = (
                1.0
                if (
                    query_component
                    and query_component
                    == candidate_component
                )
                else 0.0
            )

            # --------------------------------------
            # Error code match
            # --------------------------------------

            candidate_text = (
                documents[i]
                + " "
                + metadatas[i].get(
                    "title",
                    ""
                )
            ).lower()

            error_match = 0.0

            for error_code in (
                analysis.error_codes
            ):

                if (
                    error_code.lower()
                    in candidate_text
                ):

                    error_match = 1.0
                    break

            # --------------------------------------
            # Symptom matching
            # --------------------------------------

            candidate_words = normalize_words(
                documents[i]
            )

            query_symptom_words = set()

            for symptom in analysis.symptoms:

                query_symptom_words.update(
                    normalize_words(
                        symptom
                    )
                )

            if query_symptom_words:

                overlapping_words = (
                    candidate_words
                    & query_symptom_words
                )

                symptom_match = (
                    len(overlapping_words)
                    / len(query_symptom_words)
                )

            else:

                symptom_match = 0.0

            # --------------------------------------
            # Final hybrid score
            # --------------------------------------

            final_score = (
                semantic_score
                * SEMANTIC_WEIGHT

                + component_match
                * COMPONENT_WEIGHT

                + error_match
                * ERROR_CODE_WEIGHT

                + symptom_match
                * SYMPTOM_WEIGHT
            )

            # --------------------------------------
            # Store result
            # --------------------------------------

            ranked_results.append(
                {
                    "id": ids[i],

                    "source": (
                        metadatas[i]
                        .get("source", "")
                    ),

                    "title": (
                        metadatas[i]
                        .get("title", "")
                    ),

                    "component": (
                        metadatas[i]
                        .get("component", "")
                    ),

                    "affected_software_version": (
                        metadatas[i]
                        .get(
                            "affected_software_version",
                            ""
                        )
                    ),

                    "fix_software_version": (
                        metadatas[i]
                        .get(
                            "fix_software_version",
                            ""
                        )
                    ),

                    "distance": distance,

                    "semantic_score": (
                        semantic_score
                    ),

                    "component_match": (
                        component_match
                    ),

                    "error_match": (
                        error_match
                    ),

                    "symptom_match": (
                        symptom_match
                    ),

                    "final_score": (
                        final_score
                    ),

                    "document": (
                        documents[i]
                    ),
                }
            )

        # ------------------------------------------
        # Sort by final score
        # ------------------------------------------

        ranked_results.sort(
            key=lambda x: x["final_score"],
            reverse=True,
        )

        return ranked_results