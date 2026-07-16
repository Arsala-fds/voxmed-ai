"""
VoxMed_AI - Ingestion Script
Reads documents from ../data, chunks them, generates embeddings,
and stores them in a local ChromaDB collection.

Run this once (or whenever /data changes) with:
    python3 rag/ingest.py
"""

import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
import glob
import chromadb
from chromadb.utils import embedding_functions

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "medical_knowledge"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def load_documents(data_dir):
    docs = []
    for filepath in glob.glob(os.path.join(data_dir, "*.txt")):
        with open(filepath, "r", encoding="utf-8") as f:
            docs.append({"source": os.path.basename(filepath), "text": f.read()})
    return docs


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def main():
    print("Loading documents from /data ...")
    documents = load_documents(DATA_DIR)
    if not documents:
        print("No .txt files found in /data. Run fetch_medlineplus.py first.")
        return

    print(f"Found {len(documents)} document(s). Chunking...")

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    client = chromadb.PersistentClient(path=DB_DIR)

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME, embedding_function=embedding_fn
    )

    ids, texts, metadatas = [], [], []
    for doc in documents:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            ids.append(f"{doc['source']}-{i}")
            texts.append(chunk)
            metadatas.append({"source": doc["source"]})

    print(f"Embedding and storing {len(texts)} chunks...")
    collection.add(ids=ids, documents=texts, metadatas=metadatas)

    print(f"Done. Vector DB saved to {DB_DIR}")


if __name__ == "__main__":
    main()