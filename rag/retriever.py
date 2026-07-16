"""
VoxMed_AI - Retriever
Given a text query, finds the most relevant chunks from the vector database.
Used for testing retrieval quality, and later by the Retrieval Agent.

Run directly to test:
    python3 rag/retriever.py
"""

import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
import chromadb
from chromadb.utils import embedding_functions

DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "medical_knowledge"
TOP_K = 3


def get_collection():
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    client = chromadb.PersistentClient(path=DB_DIR)
    return client.get_collection(COLLECTION_NAME, embedding_function=embedding_fn)


def retrieve(query, k=TOP_K):
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=k)

    chunks = results["documents"][0]
    sources = [meta["source"] for meta in results["metadatas"][0]]
    distances = results["distances"][0]

    return list(zip(chunks, sources, distances))


if __name__ == "__main__":
    test_queries = [
        "what should I do for a burn",
        "how to treat a nosebleed",
        "someone is choking, help",
    ]

    for q in test_queries:
        print(f"\nQuery: {q}")
        print("-" * 50)
        for chunk, source, distance in retrieve(q):
            print(f"[{source}] (distance: {distance:.4f})")
            print(chunk[:150] + "...\n")