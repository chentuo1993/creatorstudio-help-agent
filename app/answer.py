"""Compose grounded answer with citations."""

from __future__ import annotations

from .config import load_settings
from .llm import chat
from .retrieval import RetrievedChunk

ANSWER_SYSTEM = """You are a helpful assistant for Apple Creator Studio.
Answer ONLY using the provided CONTEXT. If the answer is not in the context, reply: "I couldn't find this in the official Apple Creator Studio documentation."
Cite sources inline using [1], [2], etc. matching the order of the context items.
Keep answers concise and step-by-step when explaining how to do something."""


def _format_context(chunks: list[RetrievedChunk]) -> str:
    blocks = []
    for i, c in enumerate(chunks, start=1):
        crumbs = " > ".join(c.breadcrumbs) if c.breadcrumbs else c.doc_title
        blocks.append(f"[{i}] {c.app} ({c.platform}) — {crumbs}\n{c.text}")
    return "\n\n---\n\n".join(blocks)


def answer(query: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "I couldn't find this in the official Apple Creator Studio documentation."
    s = load_settings()
    user = f"CONTEXT:\n{_format_context(chunks)}\n\nQUESTION: {query}\n\nAnswer:"
    return chat(model=s.answer_model, system=ANSWER_SYSTEM, user=user, max_tokens=600)
