import json
import os
import re
from functools import lru_cache

from groq import Groq

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


@lru_cache(maxsize=1)
def _client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return Groq(api_key=api_key)


def chat(
    system: str,
    user: str,
    *,
    model: str | None = None,
    temperature: float = 0.4,
    max_tokens: int = 2048,
) -> str:
    response = _client().chat.completions.create(
        model=model or DEFAULT_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content or ""


def parse_json_response(raw: str) -> list | dict:
    """Parse a model reply as JSON, stripping ```json fences if present."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)


def chat_json(system: str, user: str, **kwargs) -> list | dict:
    return parse_json_response(chat(system, user, **kwargs))
