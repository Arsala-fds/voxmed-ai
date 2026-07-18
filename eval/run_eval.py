"""
VoxMed_AI - Evaluation Script (v2 - includes answer_type check for hybrid fallback)
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
    answer_type_correct = 0

    print(f"Running evaluation on {total} test questions...\n")
    print("=" * 70)

    for i, item in enumerate(questions, 1):
        query = item["query"]
        expected_source = item["expected_source"]
        expected_emergency = item["expected_emergency"]
        expected_answer_type = item.get("expected_answer_type", "verified")

        result = run_pipeline(query)

        if expected_source is None:
            source_ok = len(result["sources"]) == 0 or result["answer_type"] == "general"
        else:
            source_ok = expected_source in result["sources"]
        if source_ok:
            source_correct += 1

        emergency_ok = result["is_emergency"] == expected_emergency
        if emergency_ok:
            emergency_correct += 1

        answer_type_ok = result["answer_type"] == expected_answer_type
        if answer_type_ok:
            answer_type_correct += 1

        print(f"[{i}/{total}] Query: {query}")
        print(f"  Source check:       {'PASS' if source_ok else 'FAIL'}  (expected: {expected_source}, got: {result['sources']})")
        print(f"  Emergency check:    {'PASS' if emergency_ok else 'FAIL'}  (expected: {expected_emergency}, got: {result['is_emergency']})")
        print(f"  Answer type check:  {'PASS' if answer_type_ok else 'FAIL'}  (expected: {expected_answer_type}, got: {result['answer_type']})")
        print(f"  Answer: {result['answer'][:120]}...")
        print("-" * 70)

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Retrieval accuracy:    {source_correct}/{total} ({source_correct/total*100:.1f}%)")
    print(f"Emergency accuracy:    {emergency_correct}/{total} ({emergency_correct/total*100:.1f}%)")
    print(f"Answer-type accuracy:  {answer_type_correct}/{total} ({answer_type_correct/total*100:.1f}%)")
    print(f"\nTarget from SRS (NFR-2): >= 90% groundedness")


if __name__ == "__main__":
    run_evaluation()