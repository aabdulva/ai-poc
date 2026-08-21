import chromadb

from sentence_transformers import SentenceTransformer

from src.ingestion.normalizer import KnowledgeNormalizer


MODEL_NAME = "all-MiniLM-L6-v2"

CHROMA_PATH = "chroma_db"

COLLECTION_NAME = "knowledge_base"


class VectorStore:

    def __init__(self):

        print(
            f"Loading embedding model: {MODEL_NAME}"
        )

        self.embedding_model = (
            SentenceTransformer(
                MODEL_NAME
            )
        )

        print("Embedding model loaded.")

        self.client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=COLLECTION_NAME
            )
        )

    # --------------------------------------------------
    # Build searchable document
    # --------------------------------------------------

    def _build_document(self, record):

        return f"""
Title:
{record["title"]}

Source:
{record["source"]}

Record ID:
{record["id"]}

Component:
{record["component"]}

Description:
{record["description"]}

Root Cause:
{record["root_cause"]}

Solution:
{record["solution"]}

Affected Software Version:
{record["affected_software_version"]}

Fix Software Version:
{record["fix_software_version"]}
""".strip()

    # --------------------------------------------------
    # Create / rebuild vector database
    # --------------------------------------------------

    def rebuild(self):

        normalizer = KnowledgeNormalizer()

        records = normalizer.normalize()

        print(
            f"Normalizing {len(records)} documents."
        )

        # ----------------------------------------------
        # Delete existing collection
        # ----------------------------------------------

        try:

            self.client.delete_collection(
                COLLECTION_NAME
            )

            print(
                "Existing Chroma collection deleted."
            )

        except Exception:

            pass

        # ----------------------------------------------
        # Create fresh collection
        # ----------------------------------------------

        self.collection = (
            self.client.create_collection(
                name=COLLECTION_NAME
            )
        )

        documents = []
        embeddings = []
        ids = []
        metadatas = []

        # ----------------------------------------------
        # Prepare documents
        # ----------------------------------------------

        for record in records:

            document = self._build_document(
                record
            )

            embedding = (
                self.embedding_model.encode(
                    document
                ).tolist()
            )

            documents.append(
                document
            )

            embeddings.append(
                embedding
            )

            ids.append(
                record["id"]
            )

            metadatas.append(
                {
                    "source": record["source"],

                    "title": record["title"],

                    "component": record["component"],

                    "affected_software_version": (
                        record[
                            "affected_software_version"
                        ]
                        or ""
                    ),

                    "fix_software_version": (
                        record[
                            "fix_software_version"
                        ]
                        or ""
                    ),
                }
            )

        # ----------------------------------------------
        # Store in Chroma
        # ----------------------------------------------

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print(
            f"Indexed {len(records)} documents."
        )

    # --------------------------------------------------
    # Semantic search
    # --------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
    ):

        query_embedding = (
            self.embedding_model.encode(
                query
            ).tolist()
        )

        return self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=top_k,
        )


def main():

    vector_store = VectorStore()

    vector_store.rebuild()

    print()
    print("======================================")
    print("VECTOR DATABASE REBUILT")
    print("======================================")
    print()

    print(
        f"Collection: {COLLECTION_NAME}"
    )

    print(
        f"Database:   {CHROMA_PATH}"
    )


if __name__ == "__main__":
    main()