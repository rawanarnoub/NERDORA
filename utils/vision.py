"""OpenAI GPT-4o wrapper for image-based questions."""

from __future__ import annotations

import base64
import os

from openai import OpenAI

DEFAULT_MODEL = os.getenv("VISION_MODEL", "gpt-4o")
_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is not None:
        return _client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    _client = OpenAI(api_key=api_key)
    return _client


def analyze_image(
    image_bytes: bytes,
    mime_type: str,
    prompt: str,
    system_prompt: str = "",
    *,
    model: str | None = None,
) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:{mime_type};base64,{b64}"

    user_content = [
        {"type": "image_url", "image_url": {"url": image_url}},
        {"type": "text", "text": prompt},
    ]

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_content})

    response = _get_client().chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
    )
    return (response.choices[0].message.content or "").strip()