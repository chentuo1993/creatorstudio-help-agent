"""Stage 2 — clean HTML to structured text using trafilatura.

Returns a stream of `Document` records (one per page) preserving heading
hierarchy via Markdown-like headings, which downstream chunking uses to
split along section boundaries.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import trafilatura


@dataclass
class Document:
    url: str
    title: str
    body: str
    breadcrumbs: list[str]


def _filename_to_url(path: Path) -> str:
    name = path.stem
    return "https://" + name.replace("_", "/")


_VERSION_RE = re.compile(r"/\d+(?:\.\d+)+/(mac|macos|ipados|ios|ipad|iphone)/[0-9.]+(?=/|$)")


def canonical_url(url: str) -> str:
    """Strip Apple's version segments so /foo/1.1/mac/13.0 == /foo/mac."""
    return _VERSION_RE.sub(r"/\1", url).rstrip("/")


def body_hash(body: str) -> str:
    return hashlib.sha1(body.encode("utf-8", "ignore")).hexdigest()[:16]


def _strip_sidebar_toc(body: str) -> tuple[str, str] | None:
    """Apple guide pages prepend a long sidebar TOC; the actual page starts at
    the first H1. Return (page_title, content) for chapter pages, or None for
    welcome/TOC pages (no H1 → not useful for Q&A)."""
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            page_title = line[2:].strip()
            content = "\n".join(lines[i + 1 :]).strip()
            return page_title, content
    return None


def extract_one(path: Path) -> Document | None:
    html = path.read_text(encoding="utf-8")
    body = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
        output_format="markdown",
    )
    if not body:
        return None

    stripped = _strip_sidebar_toc(body)
    if stripped is None:
        return None
    page_title, content = stripped
    if not content.strip() or len(content) < 200:
        return None

    md = trafilatura.metadata.extract_metadata(html)
    title = page_title or (md.title if md and md.title else path.stem)
    breadcrumbs = (md.categories if md and md.categories else [])

    return Document(
        url=_filename_to_url(path),
        title=title,
        body=content,
        breadcrumbs=list(breadcrumbs),
    )


def _dedupe(docs: list[Document]) -> list[Document]:
    """Drop documents that share a canonical URL or identical body."""
    seen_canon: set[str] = set()
    seen_hash: set[str] = set()
    keep: list[Document] = []
    for d in docs:
        canon = canonical_url(d.url)
        h = body_hash(d.body)
        if canon in seen_canon or h in seen_hash:
            continue
        seen_canon.add(canon)
        seen_hash.add(h)
        d.url = canon
        keep.append(d)
    return keep


def iter_extracted(raw_dir: Path) -> list[Document]:
    docs: list[Document] = []
    for html_path in raw_dir.rglob("*.html"):
        doc = extract_one(html_path)
        if doc and doc.body.strip():
            docs.append(doc)
    return _dedupe(docs)


def iter_extracted_parallel(raw_dir: Path, workers: int | None = None) -> list[Document]:
    """Extract docs in parallel via multiprocessing. trafilatura is CPU-bound,
    so this gives near-linear speedup with cores."""
    from concurrent.futures import ProcessPoolExecutor

    paths = list(raw_dir.rglob("*.html"))
    docs: list[Document] = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for doc in ex.map(extract_one, paths, chunksize=8):
            if doc and doc.body.strip():
                docs.append(doc)
    return _dedupe(docs)
