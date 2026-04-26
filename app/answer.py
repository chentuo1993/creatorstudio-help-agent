"""Compose grounded answer with citations."""

from __future__ import annotations

from .config import load_settings
from .llm import chat
from .retrieval import RetrievedChunk

ANSWER_SYSTEM = """You are a helpful assistant for Apple Creator Studio.
Answer ONLY using the provided CONTEXT. If the answer is not in the context, reply: "I couldn't find this in the official Apple Creator Studio documentation."
Cite sources inline using [1], [2], etc. matching the order of the context items.
Keep answers concise and step-by-step when explaining how to do something. If a RECENT CONVERSATION is present, the user's latest message may refer to it; stay grounded in CONTEXT and resolve pronouns when possible."""


def _format_context(chunks: list[RetrievedChunk]) -> str:
    blocks = []
    for i, c in enumerate(chunks, start=1):
        crumbs = " > ".join(c.breadcrumbs) if c.breadcrumbs else c.doc_title
        blocks.append(f"[{i}] {c.app} ({c.platform}) — {crumbs}\n{c.text}")
    return "\n\n---\n\n".join(blocks)


def _format_history(history: list[dict[str, str]] | None) -> str:
    if not history:
        return ""
    lines: list[str] = []
    for m in history[-8:]:  # last 4 back-and-forth, enough for "it"/"that"
        r = m.get("role", "user")
        c = (m.get("content") or "")[:800]
        label = "User" if r == "user" else "Assistant"
        lines.append(f"{label}: {c}")
    return "RECENT CONVERSATION:\n" + "\n".join(lines) + "\n\n"


def answer(
    query: str,
    chunks: list[RetrievedChunk],
    history: list[dict[str, str]] | None = None,
) -> str:
    if not chunks:
        return "I couldn't find this in the official Apple Creator Studio documentation."
    s = load_settings()
    h = _format_history(history)
    user = f"{h}CONTEXT:\n{_format_context(chunks)}\n\nQUESTION: {query}\n\nAnswer:"
    return chat(model=s.answer_model, system=ANSWER_SYSTEM, user=user, max_tokens=700)
