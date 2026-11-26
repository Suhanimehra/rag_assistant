"""Pure ranking helpers (no DB or model imports)."""
from dataclasses import dataclass, replace
from collections import defaultdict
import math
import re

@dataclass(frozen=True)
class Candidate:
    id: int
    document_id: int
    filename: str
    page: int | None
    content: str
    score: float

def tokens(text: str) -> list[str]:
    return re.findall(r"\w+", text.casefold())

def bm25_rank(query: str, candidates: list[Candidate]) -> list[Candidate]:
    from collections import Counter
    if not candidates:
        return []
    corpus = [Counter(tokens(c.content)) for c in candidates]
    avg_length = sum(sum(counts.values()) for counts in corpus) / len(corpus) or 1
    query_tokens = set(tokens(query))
    scores = []
    for candidate, counts in zip(candidates, corpus):
        length = sum(counts.values())
        score = 0.0
        for term in query_tokens:
            freq = counts[term]
            df = sum(term in c for c in corpus)
            idf = math.log(1 + (len(corpus) - df + .5) / (df + .5))
            score += idf * (freq * 2.5) / (freq + 1.5 * (.25 + .75 * length / avg_length))
        if score:
            scores.append(replace(candidate, score=score))
    return sorted(scores, key=lambda c: (-c.score, c.id))

def reciprocal_rank_fusion(*rankings: list[Candidate], k: int = 60) -> list[Candidate]:
    scores = defaultdict(float)
    items = {}
    for ranking in rankings:
        seen = set()
        for rank, candidate in enumerate(ranking, 1):
            if candidate.id in seen:
                continue
            seen.add(candidate.id)
            scores[candidate.id] += 1 / (k + rank)
            items[candidate.id] = candidate
    return [replace(c, score=scores[c.id])
            for c in sorted(items.values(), key=lambda c: (-scores[c.id], c.id))]
