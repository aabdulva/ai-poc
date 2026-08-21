from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingModel:

    def __init__(self):
        print(f"Loading embedding model: {MODEL_NAME}")

        self.model = SentenceTransformer(MODEL_NAME)

        print("Embedding model loaded.")

    def embed(self, text: str):
        """
        Convert text into a numerical vector.
        """

        return self.model.encode(
            text,
            normalize_embeddings=True
        )

    def embed_documents(self, documents: list[dict]):

        texts = [
            document["content"]
            for document in documents
        ]

        return self.model.encode(
            texts,
            normalize_embeddings=True
        )