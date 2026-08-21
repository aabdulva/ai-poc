import json
from pathlib import Path

from src.ingestion.normalizer import normalize_documents


PROJECT_ROOT = Path(__file__).resolve().parents[2]

JIRA_FILE = PROJECT_ROOT / "data" / "jira" / "issues.json"
CONFLUENCE_FILE = PROJECT_ROOT / "data" / "confluence" / "pages.json"
KNOWN_ISSUES_FILE = PROJECT_ROOT / "data" / "known_issues" / "issues.json"


def load_json(file_path: Path):
    """Load JSON data from a file."""

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_jira():
    return load_json(JIRA_FILE)


def load_confluence():
    return load_json(CONFLUENCE_FILE)


def load_known_issues():
    return load_json(KNOWN_ISSUES_FILE)


def load_all_documents():

    jira = load_jira()
    confluence = load_confluence()
    known_issues = load_known_issues()

    return normalize_documents(
        jira,
        confluence,
        known_issues,
    )


if __name__ == "__main__":

    documents = load_all_documents()

    print()
    print("======================================")
    print("AI Test Issue Agent - Data Loader")
    print("======================================")
    print()

    print(f"Total normalized documents: {len(documents)}")
    print()

    for document in documents:

        print("--------------------------------------")

        print(f"ID:       {document['id']}")
        print(f"Source:   {document['source']}")
        print(f"Title:    {document['title']}")

        print("Metadata:")
        print(f"  Component: {document['metadata'].get('component')}")
        print(
            f"  Software:  "
            f"{document['metadata'].get('software_version')}"
        )

        print()

        print("Content:")
        print(document["content"])