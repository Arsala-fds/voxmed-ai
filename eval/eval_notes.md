
# Evaluation Notes - Phase 5

**Results:** Retrieval accuracy 90% (9/10), Emergency detection accuracy 100% (10/10)

## Known limitation

Test #8 ("small cut" query) retrieved burns.txt instead of the expected
wounds_and_injuries.txt, though the final answer was still correct because
first_aid_steps.txt (which covers both) was also retrieved. Likely cause:
semantic overlap between burn and cut first-aid vocabulary (wound, clean,
dressing, bandage) confuses the embedding similarity search.

## Potential future fixes (not applied yet, tracked for iteration)

- Increase top_k from 3 to 5 to reduce chance of missing the right doc
- Try a stronger embedding model than all-MiniLM-L6-v2
- Add more distinct keywords to wounds_and_injuries.txt to differentiate it from burns.txt
