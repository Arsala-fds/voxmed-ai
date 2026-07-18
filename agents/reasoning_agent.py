"""
VoxMed_AI - Reasoning Agent
Generates a grounded answer when relevant context is retrieved.
Falls back to the LLM's general medical knowledge (clearly labeled)
when no relevant document is found, always including a safety reminder.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

DISTANCE_THRESHOLD = 1.15  # above this, retrieved context is considered irrelevant

GROUNDED_SYSTEM_PROMPT = """You are VoxMed, a careful medical information assistant.
Answer ONLY using the provided context below. If the context does not
contain the answer, say clearly that you don't have that information.
Never invent facts. Keep answers short and speakable (2-4 sentences),
since they will be read aloud. Always end with a brief reminder to
consult a doctor for serious concerns."""

GENERAL_KNOWLEDGE_SYSTEM_PROMPT = """You are VoxMed, a medical information
assistant. No verified reference document was found for this question, so
answer using your own general medical knowledge instead. Keep the answer
short, speakable (2-4 sentences), and clearly factual/well-established
information only - do not speculate on rare or uncertain details.
ALWAYS start your answer with "Based on general medical knowledge (not a
verified source):" and ALWAYS end with: "If this is urgent or severe,
please call your local emergency number or see a doctor right away.\""""


def get_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Check your .env file or Streamlit secrets.")
    return Groq(api_key=api_key)


def generate_answer(retrieval_result: dict) -> dict:
    """
    Takes the Retrieval Agent's output dict, generates an answer, and
    tags it as 'verified' (grounded in retrieved docs) or 'general'
    (LLM's own knowledge, used only when no relevant doc was found).
    """
    client = get_client()

    query = retrieval_result["cleaned_query"]
    chunks = retrieval_result["retrieved_chunks"]
    top_distance = retrieval_result.get("top_match_distance")

    has_relevant_context = (
        chunks and top_distance is not None and top_distance <= DISTANCE_THRESHOLD
    )

    if has_relevant_context:
        context_text = "\n\n---\n\n".join(chunks)
        user_message = f"Context:\n{context_text}\n\nQuestion: {query}"
        system_prompt = GROUNDED_SYSTEM_PROMPT
        answer_type = "verified"
    else:
        user_message = f"Question: {query}"
        system_prompt = GENERAL_KNOWLEDGE_SYSTEM_PROMPT
        answer_type = "general"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=300,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )

    answer = response.choices[0].message.content

    return {
        **retrieval_result,
        "answer": answer,
        "answer_type": answer_type,  # "verified" or "general"
    }


if __name__ == "__main__":
    from intake_agent import process_query
    from retrieval_agent import get_context

    test_query = "what should i do for a burn"
    intake_result = process_query(test_query)
    retrieval_result = get_context(intake_result)
    final_result = generate_answer(retrieval_result)

    print("Query:", final_result["cleaned_query"])
    print("Answer type:", final_result["answer_type"])
    print("Sources:", final_result["sources"])
    print("\nAnswer:")
    print(final_result["answer"])