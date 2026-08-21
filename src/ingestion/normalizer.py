import json
from pathlib import Path
from typing import Optional


class KnowledgeNormalizer:
    """
    Normalize Jira, Confluence and Known Issues
    records into a common internal schema.
    """

    def __init__(self, data_root: str = "data"):

        self.data_root = Path(data_root)

    # --------------------------------------------------
    # Generic JSON loader
    # --------------------------------------------------

    def _load_json(self, path: Path):

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    # --------------------------------------------------
    # Extract fix version from solution text
    # --------------------------------------------------

    def _extract_fix_version(
        self,
        solution: Optional[str]
    ) -> Optional[str]:

        if not solution:
            return None

        text = solution.lower()

        # Example:
        # "software version 4.2.3"
        #
        # Example:
        # "Camera Stack 4.2.3"
        #
        # Example:
        # "release 4.3.0"

        import re

        patterns = [
            r"software version\s+([0-9]+\.[0-9]+\.[0-9]+)",
            r"camera stack\s+([0-9]+\.[0-9]+\.[0-9]+)",
            r"release\s+([0-9]+\.[0-9]+\.[0-9]+)",
            r"version\s+([0-9]+\.[0-9]+\.[0-9]+)",
            r"\bto\s+([0-9]+\.[0-9]+\.[0-9]+)\s+or\s+later\b",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text
            )

            if match:
                return match.group(1)

        return None

    # --------------------------------------------------
    # Normalize Jira
    # --------------------------------------------------

    def _normalize_jira(self, record):

        solution = record.get(
            "solution"
        )

        return {
            "source": "JIRA",

            "id": record.get(
                "id"
            ),

            "title": record.get(
                "title"
            ),

            "component": record.get(
                "component"
            ),

            "description": record.get(
                "description",
                ""
            ),

            "root_cause": record.get(
                "root_cause"
            ),

            "solution": solution,

            "affected_software_version": (
                record.get(
                    "software_version"
                )
            ),

            "fix_software_version": (
                self._extract_fix_version(
                    solution
                )
            ),
        }

    # --------------------------------------------------
    # Normalize Confluence
    # --------------------------------------------------

    def _normalize_confluence(self, record):

        content = record.get(
            "content",
            ""
        )

        fix_version = (
            self._extract_fix_version(
                content
            )
        )

        return {
            "source": "CONFLUENCE",

            "id": record.get(
                "id"
            ),

            "title": record.get(
                "title"
            ),

            "component": record.get(
                "component"
            ),

            "description": content,

            "root_cause": None,

            "solution": content,

            "affected_software_version": None,

            "fix_software_version": (
                fix_version
                or record.get(
                    "software_version"
                )
            ),
        }

    # --------------------------------------------------
    # Normalize Known Issues
    # --------------------------------------------------

    def _normalize_known_issue(
        self,
        record
    ):

        solution = record.get(
            "solution"
        )

        return {
            "source": "KNOWN_ISSUES",

            "id": record.get(
                "id"
            ),

            "title": record.get(
                "title"
            ),

            "component": record.get(
                "component"
            ),

            "description": record.get(
                "description",
                ""
            ),

            "root_cause": record.get(
                "root_cause"
            ),

            "solution": solution,

            "affected_software_version": (
                record.get(
                    "software_version"
                )
            ),

            "fix_software_version": (
                self._extract_fix_version(
                    solution
                )
            ),
        }

    # --------------------------------------------------
    # Normalize everything
    # --------------------------------------------------

    def normalize(self):

        normalized = []

        # ----------------------------------------------
        # Jira
        # ----------------------------------------------

        jira_path = (
            self.data_root
            / "jira"
            / "issues.json"
        )

        jira_records = self._load_json(
            jira_path
        )

        for record in jira_records:

            normalized.append(
                self._normalize_jira(
                    record
                )
            )

        # ----------------------------------------------
        # Confluence
        # ----------------------------------------------

        confluence_path = (
            self.data_root
            / "confluence"
            / "pages.json"
        )

        confluence_records = (
            self._load_json(
                confluence_path
            )
        )

        for record in confluence_records:

            normalized.append(
                self._normalize_confluence(
                    record
                )
            )

        # ----------------------------------------------
        # Known Issues
        # ----------------------------------------------

        known_issues_path = (
            self.data_root
            / "known_issues"
            / "issues.json"
        )

        known_issue_records = (
            self._load_json(
                known_issues_path
            )
        )

        for record in known_issue_records:

            normalized.append(
                self._normalize_known_issue(
                    record
                )
            )

        return normalized


def main():

    normalizer = KnowledgeNormalizer()

    records = normalizer.normalize()

    print()
    print("======================================")
    print("NORMALIZED KNOWLEDGE BASE")
    print("======================================")
    print()

    for record in records:

        print("--------------------------------------")

        print(
            f"ID: "
            f"{record['id']}"
        )

        print(
            f"Source: "
            f"{record['source']}"
        )

        print(
            f"Component: "
            f"{record['component']}"
        )

        print(
            f"Affected software: "
            f"{record['affected_software_version']}"
        )

        print(
            f"Fix software: "
            f"{record['fix_software_version']}"
        )

        print(
            f"Root cause: "
            f"{record['root_cause']}"
        )

        print(
            f"Solution: "
            f"{record['solution']}"
        )


if __name__ == "__main__":
    main()