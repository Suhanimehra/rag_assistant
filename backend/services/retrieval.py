"""Independent dense and lexical candidate retrieval, fusion and optional reranking."""
from sqlalchemy import text
from backend.config import get_settings
from backend.services.embeddings import embed_query, reranker
from backend.services.ranking import Candidate, reciprocal_rank_fusion, bm25_rank, tokens

def retrieve(db, query: str, document_ids: list[int] | None = None) -> list[Candidate]:
    settings = get_settings()
    vector = embed_query(query)
    params = {"embedding": str(vector), "query": " OR ".join(dict.fromkeys(tokens(query)[:32])), "limit": settings.candidate_count,
              "threshold": settings.min_cosine_similarity, "document_ids": document_ids}
    base = """SELECT c.id, c.document_id, d.filename, c.page, c.content, {score} AS score
              FROM document_chunks c JOIN documents d ON d.id=c.document_id
              WHERE (CAST(:document_ids AS integer[]) IS NULL OR c.document_id=ANY(CAST(:document_ids AS integer[])))"""
    cosine = "1 - (c.embedding <=> CAST(:embedding AS vector))"
    dense_sql = base.format(score=cosine) + f" AND {cosine} >= :threshold ORDER BY c.embedding <=> CAST(:embedding AS vector) LIMIT :limit"
    lexical_sql = base.format(score="ts_rank_cd(to_tsvector('simple', c.content), websearch_to_tsquery('simple', :query))") + """
        AND to_tsvector('simple', c.content) @@ websearch_to_tsquery('simple', :query)
        ORDER BY score DESC LIMIT :limit"""
    dense = [Candidate(*row) for row in db.execute(text(dense_sql), params)]
    lexical = [Candidate(*row) for row in db.execute(text(lexical_sql), params)] if settings.enable_hybrid else []
    lexical_ranked = bm25_rank(query, lexical)
    fused = reciprocal_rank_fusion(dense, lexical_ranked) if settings.enable_hybrid else dense
    if settings.enable_reranking and fused:
        scores = reranker().predict([(query, chunk.content) for chunk in fused])
        fused = [c for c, _ in sorted(zip(fused, scores), key=lambda x: float(x[1]), reverse=True)]
    seen = set()
    result = []
    for candidate in fused:
        key = (candidate.document_id, candidate.content)
        if key not in seen:
            seen.add(key)
            result.append(candidate)
        if len(result) >= settings.top_k:
            break
    return result
