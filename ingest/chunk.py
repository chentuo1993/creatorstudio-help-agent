"""Stage 3 — split documents into ~400-token chunks along H2/H3 boundaries.

We tokenize with tiktoken's cl100k_base (close enough for both OpenAI and
most other models) and slide a window when a section is too large.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import tiktoken

from .extract import Document

TOKEN_ENCODING = tiktoken.get_encoding("cl100k_base")
TARGET_TOKENS = 400
OVERLAP_TOKENS = 80


@dataclass
class Chunk:
    text: str
    breadcrumbs: list[str]
    url: str
    doc_title: str


def _count(tokens: list[int]) -> int:
    return len(tokens)


def _split_by_heading(body: str) -> list[tuple[list[str], str]]:
    """Yield (heading_path, section_body) tuples by walking H1/H2/H3 markers."""
    sections: list[tuple[list[str], str]] = []
    current_path: list[str] = []
    buffer: list[str] = []

    def flush():
        if buffer:
            sections.append((list(current_path), "\n".join(buffer).strip()))
            buffer.clear()

    for line in body.splitlines():
        m = re.match(r"^(#{1,3})\s+(.+)$", line)
        if m:
            flush()
            level = len(m.group(1))
            title = m.group(2).strip()
            current_path = current_path[: level - 1] + [title]
        else:
            buffer.append(line)
    flush()
    return sections


def _window(tokens: list[int]) -> list[list[int]]:
    if _count(tokens) <= TARGET_TOKENS:
        return [tokens]
    out: list[list[int]] = []
    step = TARGET_TOKENS - OVERLAP_TOKENS
    for start in range(0, len(tokens), step):
        out.append(tokens[start : start + TARGET_TOKENS])
        if start + TARGET_TOKENS >= len(tokens):
            break
    return out


def chunk_document(doc: Document) -> list[Chunk]:
    chunks: list[Chunk] = []
    sections = _split_by_heading(doc.body) or [([], doc.body)]
    for heading_path, body in sections:
        if not body.strip():
            continue
        tokens = TOKEN_ENCODING.encode(body)
        for window in _window(tokens):
            text = TOKEN_ENCODING.decode(window).strip()
            if not text:
                continue
            chunks.append(
                Chunk(
                    text=text,
                    breadcrumbs=doc.breadcrumbs + heading_path,
                    url=doc.url,
                    doc_title=doc.title,
                )
            )
    return chunks
