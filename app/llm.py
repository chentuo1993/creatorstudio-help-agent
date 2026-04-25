"""Thin wrapper around the AI Builders Space OpenAI-compatible endpoint."""

from __future__ import annotations

from functools import lru_cache

from openai import OpenAI

from .config import load_settings


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    s = load_settings()
    if not s.api_key:
        raise RuntimeError("AI_BUILDER_TOKEN is not set")
    return OpenAI(base_url=s.base_url, api_key=s.api_key)


def embed(text: str) -> list[float]:
    s = load_settings()
    resp = get_client().embeddings.create(model=s.embedding_model, input=[text])
    return resp.data[0].embedding


def chat(model: str, system: str, user: str, max_tokens: int = 600) -> str:
    resp = get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_tokens,
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""
