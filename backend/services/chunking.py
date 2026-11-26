from dataclasses import dataclass
from io import BytesIO
import re

@dataclass(frozen=True)
class Chunk:
    page: int | None
    content: str

def normalize(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.replace("\r\n", "\n").replace("\x00", "")).strip()

def extract_pages(data: bytes, filename: str) -> list[tuple[int | None, str]]:
    if filename.lower().endswith(".pdf"):
        if not data.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF")
        import pymupdf
        with pymupdf.open(stream=data, filetype="pdf") as pdf:
            if pdf.needs_pass:
                raise ValueError("Encrypted PDF is not supported")
            if len(pdf) > 1000:
                raise ValueError("PDF exceeds the page limit")
            pages = [(i + 1, normalize(page.get_text(sort=True))) for i, page in enumerate(pdf)]
    elif filename.lower().endswith((".txt", ".md", ".csv")):
        pages = [(None, normalize(data.decode("utf-8-sig")))]
    else:
        raise ValueError("Supported types: PDF, TXT, Markdown and CSV")
    pages = [(page, content) for page, content in pages if content]
    if not pages:
        raise ValueError("No extractable text. Scanned documents require OCR.")
    return pages

def chunk_pages(pages, tokenizer, size=220, overlap=32) -> list[Chunk]:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    if not 0 <= overlap < size:
        raise ValueError("Invalid chunk overlap")
    splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer, chunk_size=size, chunk_overlap=overlap, separators=["\n\n", "\n", ". ", " ", ""]
    )
    return [Chunk(page, part) for page, text in pages for part in splitter.split_text(text) if part.strip()]
