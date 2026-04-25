"""FastAPI app: serves static SPA + Q&A endpoint."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .answer import answer as compose_answer
from .config import load_settings
from .rerank import rerank
from .retrieval import RetrievedChunk, hybrid_search
from .router import classify_apps

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Apple Creator Studio Help Agent", version="0.1.0")


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=500)


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


@app.get("/healthz")
def healthz() -> dict:
    settings = load_settings()
    db_exists = Path(settings.db_path).exists()
    return {"ok": True, "db_exists": db_exists, "answer_model": settings.answer_model}


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest) -> ChatResponse:
    settings = load_settings()
    matched = classify_apps(req.question)
    try:
        candidates = hybrid_search(
            req.question,
            app_filter=matched or None,
            limit=settings.retrieve_top_k,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=500, detail=f"db error: {exc}")

    if settings.enable_rerank:
        top = rerank(req.question, candidates, top_n=settings.answer_top_k)
    else:
        top = candidates[: settings.answer_top_k]

    text = compose_answer(req.question, top)
    return ChatResponse(answer=text, citations=_to_citations(top), matched_apps=matched)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "concept-a.html")


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
