"""
VoxMed_AI - Safety Agent
Final check before the answer goes to the user. Uses the LLM to properly
assess whether the query describes a medical emergency (more reliable
than the Intake Agent's simple keyword check), and prepends an urgent
care recommendation if so.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SAFETY_PROMPT = """You are a medical safety classifier. Read the user's
question and respond with ONLY one word: "EMERGENCY" if it describes a
potentially life-threatening situation (e.g. severe difficulty breathing,
chest pain, unconsciousness, severe bleeding, signs of stroke, severe
allergic reaction), or "ROUTINE" if it is a general first-aid or health
information question. Respond with exactly one word, nothing else."""

EMERGENCY_PREFIX = (
    "This sounds like it could be a medical emergency. "
    "Please call your local emergency number or go to the nearest "
    "emergency room right away. "
)


def get_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Check your .env file.")
    return Groq(api_key=api_key)


def check_safety(reasoning_result: dict) -> dict:
    """
    Takes the Reasoning Agent's output dict, classifies emergency risk,
    and prepends an urgent-care message to the answer if needed.
    """
    client = get_client()
    query = reasoning_result["cleaned_query"]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=10,
        messages=[
            {"role": "system", "content": SAFETY_PROMPT},
            {"role": "user", "content": query},
        ],
    )

    classification = response.choices[0].message.content.strip().upper()
    is_emergency = "EMERGENCY" in classification

    final_answer = reasoning_result["answer"]
    if is_emergency:
        final_answer = EMERGENCY_PREFIX + final_answer

    return {
        **reasoning_result,
        "safety_classification": classification,
        "is_emergency": is_emergency,
        "final_answer": final_answer,
    }


if __name__ == "__main__":
    from intake_agent import process_query
    from retrieval_agent import get_context
    from reasoning_agent import generate_answer

    test_queries = [
        "what should i do for a burn",
        "i have severe chest pain and can't breathe",
    ]

    for q in test_queries:
        intake_result = process_query(q)
        retrieval_result = get_context(intake_result)
        reasoning_result = generate_answer(retrieval_result)
        final_result = check_safety(reasoning_result)

        print(f"\nQuery: {q}")
        print(f"Safety classification: {final_result['safety_classification']}")
        print(f"Final answer: {final_result['final_answer']}")