from functools import lru_cache
from backend.config import get_settings

@lru_cache(maxsize=1)
def embedding_model():
    from sentence_transformers import SentenceTransformer
    settings = get_settings()
    model = SentenceTransformer(settings.embedding_model)
    get_dimension = getattr(model, "get_embedding_dimension", None)
    dimension = get_dimension() if get_dimension else model.get_sentence_embedding_dimension()
    if dimension != settings.embedding_dimension or settings.embedding_dimension != 384:
        raise ValueError("Embedding model must match the 384-dimensional database schema; migrate and reindex first.")
    return model

def embed(texts: list[str]) -> list[list[float]]:
    return embedding_model().encode(texts, batch_size=32, normalize_embeddings=True).tolist()

@lru_cache(maxsize=1)
def reranker():
    from sentence_transformers import CrossEncoder
    return CrossEncoder(get_settings().reranker_model)

def embed_query(query: str) -> list[float]:
    """Optional Redis cache; failure falls back to uncached local inference."""
    import hashlib
    import json
    settings = get_settings()
    if not settings.redis_url:
        return embed([query])[0]
    client = None
    key = "rag:embedding:" + hashlib.sha256((settings.embedding_model + "\0" + query).encode()).hexdigest()
    try:
        import redis
        client = redis.Redis.from_url(settings.redis_url, socket_timeout=1, socket_connect_timeout=1)
        cached = client.get(key)
        if cached:
            vector = json.loads(cached)
            if len(vector) == settings.embedding_dimension:
                return vector
    except Exception:
        client = None
    vector = embed([query])[0]
    if client:
        try:
            client.setex(key, 3600, json.dumps(vector))
        except Exception:
            pass
    return vector
