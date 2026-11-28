"""Runtime configuration; secrets are never committed."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, model_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    jwt_secret: SecretStr = Field(min_length=32)
    # Sessions stay valid until the user signs out (or the token expires).
    access_token_minutes: int = 60 * 24 * 30
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    groq_api_key: SecretStr
    groq_model: str = "openai/gpt-oss-20b"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_max_completion_tokens: int = 1024
    chunk_tokens: int = 220
    overlap_tokens: int = 32
    max_upload_bytes: int = 20 * 1024 * 1024
    candidate_count: int = 24
    top_k: int = 5
    min_cosine_similarity: float = 0.35
    enable_hybrid: bool = True
    enable_reranking: bool = False
    enable_query_rewriting: bool = True
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    request_timeout: float = 120
    redis_url: str | None = None

    @model_validator(mode="after")
    def validate_limits(self):
        if not 0 <= self.overlap_tokens < self.chunk_tokens <= 240:
            raise ValueError("Chunk size must be <=240 tokens with a smaller nonnegative overlap")
        if not 1 <= self.top_k <= self.candidate_count <= 100:
            raise ValueError("Require 1 <= top_k <= candidate_count <= 100")
        if not -1 <= self.min_cosine_similarity <= 1 or self.max_upload_bytes <= 0:
            raise ValueError("Invalid retrieval or upload limits")
        if not 64 <= self.groq_max_completion_tokens <= 8192:
            raise ValueError("Groq max completion tokens must be between 64 and 8192")
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()
