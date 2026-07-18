
# Evaluation Notes - Phase 5 & Phase 8

## Phase 8 results (after knowledge base expansion to 63 topics + hybrid fallback)

- Retrieval accuracy: 80% (12/15)
- Emergency detection accuracy: 100% (15/15)
- Answer-type accuracy (verified vs general): 93.3% (14/15)

## Threshold tuning history

Tried DISTANCE_THRESHOLD = 1.0, 1.3, and 1.15 in reasoning_agent.py.
Retrieval accuracy stayed at 80% across all three values - the failures are
not threshold-sensitive, they are genuine topic-overlap issues in the
embedding space (see below). Settled on 1.15 as a reasonable middle ground.

## Known limitations

1. **Overlapping first-aid vocabulary**: Queries about cuts, burns, and
   wounds frequently retrieve each other's documents because they share
   words like "wound," "clean," "dressing," "bandage." The final answers
   are still usually correct (first_aid_steps.txt, which covers multiple
   topics, is often retrieved alongside the "wrong" specific document),
   but the source citation isn't always the most precise match.
2. **"Weight loss" query retrieves loosely related documents**: obesity.txt,
   high_cholesterol.txt, and similar weight-adjacent topics get pulled in
   for general lifestyle questions, causing the system to answer as
   "verified" when it should ideally use the general-knowledge fallback.
   This is a precision/recall tradeoff inherent to semantic search on a
   knowledge base with many related-but-distinct health topics.
3. **Small test set (15 questions)**: Further threshold tuning on this set
   risks overfitting to these specific 15 queries rather than improving
   real-world performance. A larger test set (50-100 queries) would be
   needed before further tuning is worthwhile.

## Safety-critical metrics remain strong

Despite the retrieval precision limitations above, the metrics that matter
most for user safety are unaffected:

- Emergency detection: 100% across all phases and threshold values tested
- No fabricated answers observed in any test run
- General-knowledge fallback always includes appropriate safety disclaimers

## Recommended future work (not applied yet)

- Add a reranking step after initial retrieval to improve precision
- Expand test set to 50+ questions before further threshold tuning
- Consider a stronger embedding model for better topic separation
