"""Stage 4–5 — embed chunks and write to a single SQLite file.

Schema:
  chunks(id INTEGER PK, app TEXT, platform TEXT, breadcrumbs TEXT,
         url TEXT, doc_title TEXT, text TEXT)
  chunks_fts  — FTS5 virtual table mirroring `text` (BM25)
  chunks_vec  — sqlite-vec virtual table holding the 1536-dim embedding
"""

from __future__ import annotations

import json
import sqlite3
import struct
from pathlib import Path
from typing import Iterable

import sqlite_vec
from openai import OpenAI

from .chunk import Chunk

EMBED_DIM = 1536
BATCH = 96


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        f"""
        CREATE TABLE IF NOT EXISTS chunks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          app TEXT NOT NULL,
          platform TEXT NOT NULL,
          breadcrumbs TEXT NOT NULL,
          url TEXT NOT NULL,
          doc_title TEXT NOT NULL,
          text TEXT NOT NULL
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
          text,
          content='chunks',
          content_rowid='id',
          tokenize='porter unicode61'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
          embedding float[{EMBED_DIM}]
        );
        """
    )
    conn.commit()


def _pack(vec: list[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def insert_chunks(
    conn: sqlite3.Connection,
    chunks: Iterable[tuple[Chunk, str, str, list[float]]],
) -> int:
    cur = conn.cursor()
    n = 0
    for chunk, app_name, platform, vec in chunks:
        cur.execute(
            "INSERT INTO chunks (app, platform, breadcrumbs, url, doc_title, text)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                app_name,
                platform,
                json.dumps(chunk.breadcrumbs, ensure_ascii=False),
                chunk.url,
                chunk.doc_title,
                chunk.text,
            ),
        )
        rowid = cur.lastrowid
        cur.execute(
            "INSERT INTO chunks_fts(rowid, text) VALUES (?, ?)",
            (rowid, chunk.text),
        )
        cur.execute(
            "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)",
            (rowid, _pack(vec)),
        )
        n += 1
    conn.commit()
    return n


def embed_batch(client: OpenAI, model: str, texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=model, input=texts)
    return [d.embedding for d in resp.data]
