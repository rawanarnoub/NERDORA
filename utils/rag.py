"""RAG over uploaded PDFs using OpenAI embeddings + LangChain's in-memory store."""

from __future__ import annotations

import hashlib
import os

import fitz  # PyMuPDF
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

_embeddings: OpenAIEmbeddings | None = None


def _get_embeddings() -> OpenAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        _embeddings = OpenAIEmbeddings(
            model=EMBED_MODEL, openai_api_key=api_key
        )
    return _embeddings


def file_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def _extract_pdf_text(data: bytes) -> str:
    with fitz.open(stream=data, filetype="pdf") as doc:
        return "\n\n".join(page.get_text("text") for page in doc).strip()


def build_index(pdf_bytes: bytes) -> InMemoryVectorStore:
    text = _extract_pdf_text(pdf_bytes)
    if not text:
        raise ValueError("PDF appears to be empty or contains no extractable text.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    return InMemoryVectorStore.from_texts(chunks, _get_embeddings())


def retrieve(index: InMemoryVectorStore, query: str, k: int = 5) -> str:
    """Return top-k chunks joined as a single context string."""
    docs = index.similarity_search(query, k=k)
    return "\n\n---\n\n".join(d.page_content for d in docs)