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


def run_pipeline(user_query: str, conversation_history: list = None) -> dict:
    """
    Runs the full VoxMed_AI pipeline for a single user query.
    conversation_history: optional list of {"query": ..., "answer": ...}
    from earlier turns, so follow-up questions are understood in context.
    Returns a dict with everything the frontend needs: final answer,
    sources, and emergency flag.
    """
    # Build a context-enriched query for retrieval, so short follow-up
    # questions ("which one should I take?") pull in the right documents
    # by combining them with the previous turn's question.
    if conversation_history:
        last_query = conversation_history[-1]["query"]
        retrieval_query = f"{last_query} {user_query}"
    else:
        retrieval_query = user_query

    intake_result = process_query(retrieval_query)
    retrieval_result = get_context(intake_result)  # uses the enriched query for search
    # AFTER retrieval, swap back to the actual short query for reasoning/display
    retrieval_result["cleaned_query"] = user_query
    reasoning_result = generate_answer(retrieval_result, conversation_history=conversation_history)
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