"""Run a document-level retrieval baseline with the repository's sample corpus."""
import argparse
import json
from pathlib import Path
from statistics import mean
from time import perf_counter

def main():
    from backend.database import session_factory
    from backend.services.retrieval import retrieve
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=Path, default=Path("evaluation/questions.jsonl"))
    args = parser.parse_args()
    cases = [json.loads(line) for line in args.questions.read_text().splitlines() if line.strip()]
    rows = []
    with session_factory()() as db:
        for case in cases:
            start = perf_counter()
            candidates = retrieve(db, case["question"])
            expected = set(case["documents"])
            retrieved = list(dict.fromkeys(c.filename for c in candidates))
            hits = expected.intersection(retrieved)
            rank = next((i for i, name in enumerate(retrieved, 1) if name in expected), None)
            rows.append({"question": case["question"], "recall": len(hits)/len(expected),
                         "mrr": 1/rank if rank else 0, "latency_ms": (perf_counter()-start)*1000,
                         "retrieved": retrieved})
    print(json.dumps({"cases": rows, "mean_document_recall": mean(r["recall"] for r in rows),
                      "mean_document_mrr": mean(r["mrr"] for r in rows),
                      "mean_latency_ms": mean(r["latency_ms"] for r in rows)}, indent=2))
if __name__ == "__main__":
    main()
