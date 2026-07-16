"""
VoxMed_AI - Reasoning Agent
Takes the retrieved context and generates a grounded, spoken-friendly
answer using Groq (free tier LLM). Answers ONLY from the provided context.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are VoxMed, a careful medical information assistant.
Answer ONLY using the provided context below. If the context does not
contain the answer, say clearly that you don't have that information and
recommend consulting a healthcare professional. Never invent facts.
Keep answers short and speakable (2-4 sentences), since they will be
read aloud to the user. Always end with a brief reminder to consult a
doctor for serious concerns."""


def get_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Check your .env file.")
    return Groq(api_key=api_key)


def generate_answer(retrieval_result: dict) -> dict:
    client = get_client()

    query = retrieval_result["cleaned_query"]
    chunks = retrieval_result["retrieved_chunks"]
    context_text = "\n\n---\n\n".join(chunks)

    user_message = f"Context:\n{context_text}\n\nQuestion: {query}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=300,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    answer = response.choices[0].message.content

    return {
        **retrieval_result,
        "answer": answer,
    }


if __name__ == "__main__":
    from intake_agent import process_query
    from retrieval_agent import get_context

    test_query = "what should i do for a burn"
    intake_result = process_query(test_query)
    retrieval_result = get_context(intake_result)
    final_result = generate_answer(retrieval_result)

    print("Query:", final_result["cleaned_query"])
    print("Sources:", final_result["sources"])
    print("\nAnswer:")
    print(final_result["answer"])