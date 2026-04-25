"""LLM-as-reranker: ask a cheap model to score chunks 0–10 against the query.

Trades some accuracy for fitting in 256 MB (no local cross-encoder).
Replace with `BAAI/bge-reranker-v2-m3` once we move to a larger plan.
"""

from __future__ import annotations

import json
import re

from .config import load_settings
from .llm import chat
from .retrieval import RetrievedChunk

RERANK_SYSTEM = """You are a relevance scorer. For each candidate, output a JSON array of integer scores 0-10 measuring how well the candidate answers the user's question. Output ONLY the JSON array, no prose."""


def _format_candidates(chunks: list[RetrievedChunk]) -> str:
    parts = []
    for i, c in enumerate(chunks):
        snippet = c.text[:600].replace("\n", " ")
        crumbs = " > ".join(c.breadcrumbs[-3:]) if c.breadcrumbs else ""
        parts.append(f"[{i}] ({c.app} | {crumbs}) {snippet}")
    return "\n".join(parts)


def rerank(query: str, candidates: list[RetrievedChunk], top_n: int = 5) -> list[RetrievedChunk]:
    if not candidates:
        return []
    s = load_settings()
    user = (
        f"Question: {query}\n\nCandidates:\n{_format_candidates(candidates)}\n\n"
        f"Return a JSON array with exactly {len(candidates)} integers 0-10."
    )
    raw = chat(model=s.rerank_model, system=RERANK_SYSTEM, user=user, max_tokens=400)
    match = re.search(r"\[[\d,\s]+\]", raw)
    if not match:
        return candidates[:top_n]
    try:
        scores = json.loads(match.group(0))
    except json.JSONDecodeError:
        return candidates[:top_n]
    if len(scores) != len(candidates):
        return candidates[:top_n]
    ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])
    return [c for c, _ in ranked[:top_n]]
