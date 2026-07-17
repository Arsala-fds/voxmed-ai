"""
VoxMed_AI - Evaluation Script
Runs the full pipeline against a fixed set of test questions and
measures retrieval accuracy and emergency-detection accuracy.

Run with:
    python3 eval/run_eval.py
"""

import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "agents"))
from orchestrator import run_pipeline

TEST_FILE = os.path.join(os.path.dirname(__file__), "test_questions.json")


def load_test_questions():
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def run_evaluation():
    questions = load_test_questions()
    total = len(questions)
    source_correct = 0
    emergency_correct = 0
    no_fabrication_count = 0

    print(f"Running evaluation on {total} test questions...\n")
    print("=" * 70)

    for i, item in enumerate(questions, 1):
        query = item["query"]
        expected_source = item["expected_source"]
        expected_emergency = item["expected_emergency"]

        result = run_pipeline(query)

        # Check 1: did we retrieve the expected source? (None = expect no match)
        if expected_source is None:
            source_ok = len(result["sources"]) == 0 or "don't have" in result["answer"].lower() or "do not have" in result["answer"].lower()
        else:
            source_ok = expected_source in result["sources"]

        if source_ok:
            source_correct += 1

        # Check 2: did emergency detection match expectation?
        emergency_ok = result["is_emergency"] == expected_emergency
        if emergency_ok:
            emergency_correct += 1

        # Check 3: for the out-of-scope question, did it avoid fabricating an answer?
        if expected_source is None:
            fabricated = "don't have" not in result["answer"].lower() and "do not have" not in result["answer"].lower()
            if not fabricated:
                no_fabrication_count += 1

        status_source = "PASS" if source_ok else "FAIL"
        status_emergency = "PASS" if emergency_ok else "FAIL"

        print(f"[{i}/{total}] Query: {query}")
        print(f"  Source check:     {status_source}  (expected: {expected_source}, got: {result['sources']})")
        print(f"  Emergency check:  {status_emergency}  (expected: {expected_emergency}, got: {result['is_emergency']})")
        print(f"  Answer: {result['answer'][:120]}...")
        print("-" * 70)

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Retrieval accuracy:  {source_correct}/{total} ({source_correct/total*100:.1f}%)")
    print(f"Emergency accuracy:  {emergency_correct}/{total} ({emergency_correct/total*100:.1f}%)")
    print(f"\nTarget from SRS (NFR-2): >= 90% groundedness")
    print(f"Target from SRS (NFR-1): all answers traceable to source")


if __name__ == "__main__":
    run_evaluation()