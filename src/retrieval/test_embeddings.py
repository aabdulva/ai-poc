from src.ingestion.loader import load_all_documents
from src.retrieval.embeddings import EmbeddingModel


def main():

    documents = load_all_documents()

    embedding_model = EmbeddingModel()

    vectors = embedding_model.embed_documents(documents)

    print()
    print("==============================")
    print("Embedding Test")
    print("==============================")

    print(f"Documents: {len(documents)}")
    print(f"Vectors:   {len(vectors)}")
    print(f"Vector dimensions: {len(vectors[0])}")


if __name__ == "__main__":
    main()