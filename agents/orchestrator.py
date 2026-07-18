"""
VoxMed_AI - Orchestrator
Chains all four agents (Intake -> Retrieval -> Reasoning -> Safety)
into a single function. This is the one function the voice app
(frontend/app.py) will call.
"""

from intake_agent import process_query
from retrieval_agent import get_context
from reasoning_agent import generate_answer
from safety_agent import check_safety


def run_pipeline(user_query: str) -> dict:
    """
    Runs the full VoxMed_AI pipeline for a single user query.
    Returns a dict with everything the frontend needs: final answer,
    sources, and emergency flag.
    """
    intake_result = process_query(user_query)
    retrieval_result = get_context(intake_result)
    reasoning_result = generate_answer(retrieval_result)
    final_result = check_safety(reasoning_result)

    return {
        "query": user_query,
        "answer": final_result["final_answer"],
        "sources": final_result["sources"],
        "is_emergency": final_result["is_emergency"],
        "answer_type": final_result.get("answer_type", "verified"),
    }


if __name__ == "__main__":
    test_queries = [
        "how do i treat a nosebleed",
        "someone is choking and can't breathe",
    ]

    for q in test_queries:
        result = run_pipeline(q)
        print(f"\nQuery: {result['query']}")
        print(f"Emergency: {result['is_emergency']}")
        print(f"Sources: {result['sources']}")
        print(f"Answer: {result['answer']}")