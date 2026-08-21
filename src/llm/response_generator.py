import re

from ollama import chat


MODEL_NAME = "llama3.2"


class ResponseGenerator:

    def __init__(self):
        self.model = MODEL_NAME

    # --------------------------------------------------
    # Check whether an exact error code exists in the
    # historical document.
    # --------------------------------------------------

    def _find_historical_error_codes(
        self,
        error_codes,
        document,
    ):
        """
        Deterministically check whether the exact
        current error codes appear in a historical
        document.

        The LLM is NOT used for this comparison.
        """

        historical_matches = []

        document_upper = document.upper()

        for error_code in error_codes:

            if error_code.upper() in document_upper:

                historical_matches.append(
                    error_code
                )

        return historical_matches

    # --------------------------------------------------
    # Generate evidence blocks
    # --------------------------------------------------

    def _build_evidence_blocks(
        self,
        ids,
        documents,
        metadatas,
        distances,
        current_error_codes,
    ):

        evidence_blocks = []

        for i in range(len(ids)):

            metadata = metadatas[i]

            affected_version = metadata.get(
                "affected_software_version",
                ""
            )

            fix_version = metadata.get(
                "fix_software_version",
                ""
            )

            historical_error_codes = (
                self._find_historical_error_codes(
                    current_error_codes,
                    documents[i],
                )
            )

            if historical_error_codes:

                error_match = (
                    "YES - exact error code(s) "
                    "explicitly found: "
                    + ", ".join(
                        historical_error_codes
                    )
                )

            else:

                error_match = (
                    "NO - current error codes "
                    "were not explicitly found "
                    "in this historical record"
                )

            evidence_block = f"""
==================================================
HISTORICAL RECORD {i + 1}
==================================================

Record ID:
{ids[i]}

Source:
{metadata.get("source", "")}

Title:
{metadata.get("title", "")}

Component:
{metadata.get("component", "")}

Affected Software Version:
{affected_version or "Not specified"}

Fix Software Version:
{fix_version or "Not specified"}

VERIFIED ERROR-CODE MATCH:
{error_match}

Historical Record Content:
{documents[i]}

==================================================
END HISTORICAL RECORD {i + 1}
==================================================
"""

            evidence_blocks.append(
                evidence_block
            )

        return "\n".join(
            evidence_blocks
        )

    # --------------------------------------------------
    # Generate final engineering analysis
    # --------------------------------------------------

    def generate(
        self,
        test_log: str,
        analysis,
        search_results,
    ) -> str:

        ids = search_results["ids"][0]
        documents = search_results["documents"][0]
        metadatas = search_results["metadatas"][0]
        distances = search_results["distances"][0]

        evidence_text = (
            self._build_evidence_blocks(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                distances=distances,
                current_error_codes=(
                    analysis.error_codes
                ),
            )
        )

        prompt = f"""
You are an automotive software test failure
analysis assistant.

You are analyzing ONE CURRENT TEST FAILURE
against HISTORICAL ENGINEERING RECORDS.

Your job is to reason about the evidence.

You must NOT invent historical facts.

==================================================
CURRENT TEST FAILURE
==================================================

The following information comes from the current
test log.

CURRENT LOG:

{test_log}

CURRENT STRUCTURED ANALYSIS:

Component:
{analysis.component}

Error Codes:
{analysis.error_codes}

Symptoms:
{analysis.symptoms}

Operating Condition:
{analysis.operating_condition}

Current Software Version:
{analysis.software_version}

==================================================
HISTORICAL EVIDENCE
==================================================

{evidence_text}

==================================================
CRITICAL EVIDENCE RULES
==================================================

RULE 1:
The CURRENT TEST FAILURE and HISTORICAL RECORDS
are separate sources.

Never transfer facts from the current failure
into a historical record.

RULE 2:
The "VERIFIED ERROR-CODE MATCH" field is calculated
programmatically.

You MUST trust this field.

Do NOT override it.

If it says:

NO - current error codes were not explicitly found
in this historical record

then you MUST report that the historical record
does NOT explicitly contain the current error code.

RULE 3:
Never claim that CAM_1032 exists in a historical
record unless the evidence explicitly says so.

RULE 4:
Similarity is not identity.

If the current symptom is:

"CAN communication timeout"

and the historical record says:

"CAN communication may be lost"

describe this as:

"similar or related CAN communication behavior"

Do NOT say:

"the symptoms are identical."

RULE 5:
Do not invent historical operating conditions.

If the historical record says:

"after vehicle wakeup"

you may report that.

If it does not specify an operating condition,
say:

"Not specified in the historical record."

RULE 6:
Never confuse software versions.

Affected Software Version:
The version associated with the historical issue.

Fix Software Version:
The version in which the documented fix was
introduced.

RULE 7:
A historical solution is not automatically a
recommended solution for the current failure.

RULE 8:
Every historical claim must be traceable to the
record ID.

RULE 9:
Do not claim that two records are related merely
because they contain similar words.

==================================================
REQUIRED RESPONSE
==================================================

Previous issue found:
YES / NO

Best historical match:
<record ID or NONE>

Source:
<JIRA / CONFLUENCE / KNOWN_ISSUES / OTHER / NONE>

Relevance:
HIGH / MEDIUM / LOW / NONE

Why it is relevant:
<evidence-based explanation>

Historical symptom:
<what the historical record actually says>

Historical root cause:
<what the historical record actually says>

Affected software version:
<version or Not specified>

Fix software version:
<version or Not specified>

Historical solution:
<documented historical solution>

Related historical records:
<IDs and sources>

Current vs historical comparison:

Current error codes:
<current codes>

Historical error-code match:
<YES or NO based ONLY on VERIFIED ERROR-CODE MATCH>

Current symptoms:
<current symptoms>

Historical symptoms:
<historical symptoms actually supported by evidence>

Important differences:
<differences supported by evidence>

Assessment:
<careful engineering assessment>

Confidence:
HIGH / MEDIUM / LOW

Evidence:
<important historical claims followed by record IDs>

==================================================
IMPORTANT
==================================================

Do not make the answer more certain than the
evidence allows.

If the evidence shows a similar historical issue
but does not prove the same root cause, say:

"The historical evidence suggests a possible
relationship, but does not establish that the
current failure has the same root cause."

If the current error code does not appear in the
historical record, explicitly state:

"The current error code CAM_1032 is not explicitly
present in the historical record."

"""

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise automotive "
                        "software diagnostics assistant. "
                        "Never invent historical facts. "
                        "Programmatically verified evidence "
                        "takes precedence over inference."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            options={
                "temperature": 0,
            },
        )

        return response.message.content