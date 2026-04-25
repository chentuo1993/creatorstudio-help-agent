"""Hybrid retrieval over SQLite: BM25 (FTS5) + vec (sqlite-vec) → RRF fusion."""

from __future__ import annotations

import json
import re
import sqlite3
import struct
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import sqlite_vec

from .config import load_settings
from .llm import embed

TOP_K_PER_RETRIEVER = 50
RRF_K = 60


@dataclass
class RetrievedChunk:
    id: int
    app: str
    platform: str
    breadcrumbs: list[str]
    url: str
    doc_title: str
    text: str
    score: float


@lru_cache(maxsize=1)
def get_conn() -> sqlite3.Connection:
    s = load_settings()
    db_path = Path(s.db_path)
    if not db_path.exists():
        raise RuntimeError(f"index not found at {db_path}; run `python -m ingest.run` first")
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.row_factory = sqlite3.Row
    return conn


def _pack(vec: list[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


_FTS_TOKEN = re.compile(r"[A-Za-z0-9]+")
_STOPWORDS = {"the", "a", "an", "is", "are", "was", "were", "be", "to", "of",
              "and", "or", "in", "on", "for", "with", "by", "as", "at",
              "what", "how", "do", "does", "did", "can", "could", "should",
              "i", "you", "it", "this", "that", "these", "those"}


def _fts_query(query: str) -> str:
    """Convert a free-form natural language query to a safe FTS5 expression."""
    tokens = [t.lower() for t in _FTS_TOKEN.findall(query)]
    keep = [t for t in tokens if t not in _STOPWORDS and len(t) > 1]
    if not keep:
        keep = tokens
    return " OR ".join(f'"{t}"' for t in keep) if keep else '""'


def _bm25(query: str, app_filter: list[str] | None, limit: int) -> list[tuple[int, float]]:
    sql = (
        "SELECT c.id, bm25(chunks_fts) AS score "
        "FROM chunks_fts JOIN chunks c ON c.id = chunks_fts.rowid "
        "WHERE chunks_fts MATCH ? "
    )
    params: list = [_fts_query(query)]
    if app_filter:
        placeholders = ",".join("?" for _ in app_filter)
        sql += f"AND c.app IN ({placeholders}) "
        params.extend(app_filter)
    sql += "ORDER BY score LIMIT ?"
    params.append(limit)
    rows = get_conn().execute(sql, params).fetchall()
    return [(r["id"], r["score"]) for r in rows]


def _vector(query_vec: list[float], app_filter: list[str] | None, limit: int) -> list[tuple[int, float]]:
    rows = get_conn().execute(
        "SELECT rowid, distance FROM chunks_vec "
        "WHERE embedding MATCH ? AND k = ? ORDER BY distance",
        (_pack(query_vec), limit),
    ).fetchall()
    candidates = [(r["rowid"], r["distance"]) for r in rows]
    if not app_filter:
        return candidates
    ids = [rid for rid, _ in candidates]
    if not ids:
        return []
    placeholders = ",".join("?" for _ in ids)
    keep = {
        r["id"]
        for r in get_conn().execute(
            f"SELECT id FROM chunks WHERE id IN ({placeholders}) AND app IN ({','.join('?' for _ in app_filter)})",
            ids + app_filter,
        ).fetchall()
    }
    return [(rid, dist) for rid, dist in candidates if rid in keep]


def _rrf(rankings: list[list[tuple[int, float]]], k: int = RRF_K) -> dict[int, float]:
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, (doc_id, _) in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return scores


def _hydrate(ids: list[int], rrf_scores: dict[int, float]) -> list[RetrievedChunk]:
    if not ids:
        return []
    placeholders = ",".join("?" for _ in ids)
    rows = get_conn().execute(
        f"SELECT id, app, platform, breadcrumbs, url, doc_title, text "
        f"FROM chunks WHERE id IN ({placeholders})",
        ids,
    ).fetchall()
    by_id = {r["id"]: r for r in rows}
    out: list[RetrievedChunk] = []
    for cid in ids:
        r = by_id.get(cid)
        if not r:
            continue
        out.append(
            RetrievedChunk(
                id=cid,
                app=r["app"],
                platform=r["platform"],
                breadcrumbs=json.loads(r["breadcrumbs"]),
                url=r["url"],
                doc_title=r["doc_title"],
                text=r["text"],
                score=rrf_scores.get(cid, 0.0),
            )
        )
    return out


def hybrid_search(
    query: str, app_filter: list[str] | None = None, limit: int = 50
) -> list[RetrievedChunk]:
    bm25 = _bm25(query, app_filter, TOP_K_PER_RETRIEVER)
    vec = _vector(embed(query), app_filter, TOP_K_PER_RETRIEVER)
    fused = _rrf([bm25, vec])
    top_ids = [doc_id for doc_id, _ in sorted(fused.items(), key=lambda kv: -kv[1])[:limit]]
    return _hydrate(top_ids, fused)
