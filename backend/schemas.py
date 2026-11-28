from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

def _not_blank(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Value must not be blank")
    return value

class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

    @field_validator("username")
    @classmethod
    def username_not_blank(cls, value: str) -> str:
        return _not_blank(value)

class ChatRequest(BaseModel):
    conversation_id: int = Field(gt=0)
    question: str = Field(min_length=1, max_length=4000)
    document_ids: list[int] | None = Field(default=None, max_length=100)

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, value: str) -> str:
        return _not_blank(value)

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
