from pydantic import BaseModel, EmailStr, Field, ConfigDict

class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

class ChatRequest(BaseModel):
    conversation_id: int = Field(gt=0)
    question: str = Field(min_length=1, max_length=4000)
    document_ids: list[int] | None = Field(default=None, max_length=100)

class Source(BaseModel):
    source_id: str
    document_id: int
    filename: str
    page: int | None
    excerpt: str
    relevance: float

class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    retrieval_ms: float
    generation_ms: float
    insufficient_evidence: bool
