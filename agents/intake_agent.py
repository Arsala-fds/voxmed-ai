"""
VoxMed_AI - Intake Agent
First agent in the pipeline. Takes the raw user query (from voice
transcription) and does light cleanup + classification before passing
it to the Retrieval Agent.
"""

# Keywords that suggest an emergency - Safety Agent will double-check these later
EMERGENCY_KEYWORDS = [
    "can't breathe", "cannot breathe", "not breathing",
    "chest pain", "severe bleeding", "unconscious",
    "heart attack", "stroke", "seizure", "choking",
    "severe burn", "overdose", "suicidal", "not responding",
]


def process_query(raw_query: str) -> dict:
    """
    Takes raw transcribed text, returns a structured dict for the next agents.
    """
    cleaned = raw_query.strip()

    # crude emergency flag - a first pass, Safety Agent does the real check later
    lowered = cleaned.lower()
    possible_emergency = any(keyword in lowered for keyword in EMERGENCY_KEYWORDS)

    return {
        "original_query": raw_query,
        "cleaned_query": cleaned,
        "possible_emergency": possible_emergency,
    }


if __name__ == "__main__":
    test_inputs = [
        "what should i do for a burn",
        "my chest hurts and i can't breathe",
        "  how to treat a nosebleed  ",
    ]
    for q in test_inputs:
        result = process_query(q)
        print(result)