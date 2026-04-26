"""Runtime config — read from env vars (Koyeb injects them at runtime)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key: str
    embedding_model: str
    rerank_model: str
    answer_model: str
    db_path: str
    port: int
    enable_rerank: bool
    retrieve_top_k: int
    answer_top_k: int


def load_settings() -> Settings:
    enable = os.getenv("ENABLE_RERANK", "true").lower() == "true"
    default_retr = "40" if enable else "20"
    retrieve_k = int(os.getenv("RETRIEVE_TOP_K", default_retr))
    return Settings(
        base_url=os.getenv("AI_BUILDERS_BASE_URL", "https://space.ai-builders.com/backend/v1"),
        api_key=os.environ.get("AI_BUILDER_TOKEN", ""),
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        rerank_model=os.getenv("RERANK_MODEL", "deepseek"),
        answer_model=os.getenv("ANSWER_MODEL", "grok-4-fast"),
        db_path=os.getenv("DB_PATH", "data/index.db"),
        port=int(os.getenv("PORT", "8000")),
        enable_rerank=enable,
        retrieve_top_k=retrieve_k,
        answer_top_k=int(os.getenv("ANSWER_TOP_K", "5")),
    )
