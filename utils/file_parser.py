"""Extract plain text from uploaded PDFs and plain-text files."""

from __future__ import annotations

from typing import IO

import fitz  # PyMuPDF

MAX_CHARS = 20_000


def _truncate(text: str) -> str:
    if len(text) <= MAX_CHARS:
        return text
    return text[:MAX_CHARS] + "\n\n[...truncated...]"


def parse_pdf(data: bytes) -> str:
    pages: list[str] = []
    with fitz.open(stream=data, filetype="pdf") as doc:
        for page in doc:
            pages.append(page.get_text("text"))
    return _truncate("\n\n".join(pages).strip())


def parse_txt(data: bytes) -> str:
    return _truncate(data.decode("utf-8", errors="replace").strip())


def parse_upload(uploaded) -> str:
    """Dispatch based on the file extension of a Streamlit UploadedFile."""
    name = (uploaded.name or "").lower()
    data = uploaded.getvalue()
    if name.endswith(".pdf"):
        return parse_pdf(data)
    if name.endswith((".txt", ".md")):
        return parse_txt(data)
    raise ValueError(f"Unsupported file type: {uploaded.name}")
