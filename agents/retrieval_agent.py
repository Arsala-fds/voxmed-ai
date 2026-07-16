"""
VoxMed_AI - Retrieval Agent
Takes the cleaned query from the Intake Agent, runs it through the RAG
retriever, and returns the top matching chunks + their sources.
"""

import sys
import os

# allow importing rag/retriever.py from a sibling folder
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rag"))
from retriever import retrieve


def get_context(intake_result: dict, k: int = 3) -> dict:
    """
    Takes the Intake Agent's output dict, retrieves relevant chunks,
    and returns a dict ready for the Reasoning Agent.
    """
    query = intake_result["cleaned_query"]
    results = retrieve(query, k=k)

    chunks = [chunk for chunk, source, distance in results]
    sources = list(set(source for chunk, source, distance in results))
    best_distance = results[0][2] if results else None

    return {
        **intake_result,
        "retrieved_chunks": chunks,
        "sources": sources,
        "top_match_distance": best_distance,
    }


if __name__ == "__main__":
    from intake_agent import process_query

    test_query = "what should i do for a burn"
    intake_result = process_query(test_query)
    full_result = get_context(intake_result)

    print("Query:", full_result["cleaned_query"])
    print("Sources found:", full_result["sources"])
    print("Top match distance:", full_result["top_match_distance"])
    print("\nFirst chunk preview:")
    print(full_result["retrieved_chunks"][0][:200])