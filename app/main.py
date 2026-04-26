"""FastAPI app: serves static SPA + Q&A endpoint."""

from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .answer import answer as compose_answer
from .answer import answer_stream
from .bundle_knowledge import bundle_preamble, is_bundle_intent
from .config import load_settings
from .rerank import rerank
from .retrieval import RetrievedChunk, hybrid_search
from .router import classify_apps

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Apple Creator Studio Help Agent", version="0.1.0")


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


def _retrieval_text(history: list[ChatMessage], question: str) -> str:
    if not history:
        return question
    prior = [m.content for m in history if m.role == "user"][-2:]
    return " ".join(prior + [question])[:800]


def _router_text(history: list[ChatMessage], question: str) -> str:
    if not history:
        return question
    parts = [f"{m.role}:{(m.content or '')[:220]}" for m in history[-6:]]
    parts.append(f"user:{question}")
    return " ".join(parts)[:1000]


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class Citation(BaseModel):
    n: int
    app: str
    title: str
    url: str
    breadcrumbs: list[str]


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    matched_apps: list[str]


def _to_citations(chunks: list[RetrievedChunk]) -> list[Citation]:
    return [
        Citation(
            n=i + 1,
            app=c.app,
            title=c.doc_title,
            url=c.url,
            breadcrumbs=c.breadcrumbs,
        )
        for i, c in enumerate(chunks)
    ]


def _run_pipeline(
    req: ChatRequest,
) -> tuple[str, list[RetrievedChunk], list[str], list[dict[str, str]], str]:
    """Return question, top chunks, matched app names, history for LLM, bundle preamble."""
    q = req.question.strip()
    h = [m for m in req.history if m.content.strip()]
    rt = _retrieval_text(h, q)
    router = _router_text(h, q)
    matched = classify_apps(router)
    settings = load_settings()
    try:
        candidates = hybrid_search(
            rt,
            app_filter=matched or None,
            limit=settings.retrieve_top_k,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=500, detail=f"db error: {exc}") from exc

    if settings.enable_rerank:
        top = rerank(rt, candidates, top_n=settings.answer_top_k)
    else:
        top = candidates[: settings.answer_top_k]

    hist_for_llm = [{"role": m.role, "content": m.content} for m in h]
    bn = ""
    if is_bundle_intent(router) or is_bundle_intent(q):
        bn = bundle_preamble()
    return q, top, matched, hist_for_llm, bn


@app.get("/healthz")
def healthz() -> dict:
    settings = load_settings()
    db_exists = Path(settings.db_path).exists()
    return {
        "ok": True,
        "db_exists": db_exists,
        "answer_model": settings.answer_model,
        "enable_rerank": settings.enable_rerank,
        "retrieve_top_k": settings.retrieve_top_k,
        "answer_top_k": settings.answer_top_k,
        "perf_mode": os.getenv("PERF_MODE", "false").lower() == "true",
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest) -> ChatResponse:
    q, top, matched, hist_for_llm, bn = _run_pipeline(req)
    text = compose_answer(q, top, history=hist_for_llm, bundle_note=bn)
    return ChatResponse(answer=text, citations=_to_citations(top), matched_apps=matched)


def _sse_data(obj: dict) -> str:
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"


@app.post("/api/chat/stream")
def chat_stream_endpoint(req: ChatRequest):
    """Server-Sent Events: first `meta` event, then `d` (token) events, then `done`."""
    q, top, matched, hist_for_llm, bn = _run_pipeline(req)
    cite_model = [c.model_dump() for c in _to_citations(top)]

    def event_gen() -> Iterator[str]:
        yield _sse_data(
            {
                "t": "meta",
                "citations": cite_model,
                "matched_apps": matched,
            }
        )
        for part in answer_stream(q, top, history=hist_for_llm, bundle_note=bn):
            yield _sse_data({"t": "d", "d": part})
        yield _sse_data({"t": "done"})

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "concept-a.html")


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
