def build_search_query(analysis) -> str:
    """
    Convert the structured LLM analysis into
    a focused semantic search query.
    """

    parts = []

    if analysis.component:
        parts.append(
            f"Component: {analysis.component}"
        )

    if analysis.error_codes:
        parts.append(
            "Error codes: "
            + ", ".join(analysis.error_codes)
        )

    if analysis.symptoms:
        parts.append(
            "Symptoms: "
            + ", ".join(analysis.symptoms)
        )

    if analysis.operating_condition:
        parts.append(
            f"Operating condition: "
            f"{analysis.operating_condition}"
        )

    if analysis.software_version:
        parts.append(
            f"Software version: "
            f"{analysis.software_version}"
        )

    return "\n".join(parts)