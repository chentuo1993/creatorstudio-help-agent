"""Top-level offline pipeline: crawl → extract → chunk → embed → index.

Usage:
    python -m ingest.run --app final-cut-pro --max-pages 20
    python -m ingest.run --all --max-pages 200
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from .chunk import chunk_document
from .config import APPS, AppSource
from .crawl import RAW_DIR, crawl_app
from .extract import iter_extracted_parallel
from .index import BATCH, _connect, embed_batch, init_schema, insert_chunks


def _select_apps(slug: str | None) -> list[AppSource]:
    if not slug:
        return list(APPS)
    matched = [a for a in APPS if a.slug == slug]
    if not matched:
        raise SystemExit(f"unknown app slug: {slug}")
    return matched


def _platform_for_url(app: AppSource, url: str) -> str:
    for plat in app.platforms:
        if plat in url:
            return plat
    return app.platforms[0]


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", help="single app slug; omit for all", default=None)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--max-pages", type=int, default=10)
    parser.add_argument("--db", default=os.getenv("DB_PATH", "data/index.db"))
    parser.add_argument("--skip-crawl", action="store_true")
    args = parser.parse_args()

    apps = _select_apps(None if args.all else args.app)

    client = OpenAI(
        base_url=os.getenv("AI_BUILDERS_BASE_URL", "https://space.ai-builders.com/backend/v1"),
        api_key=os.environ["AI_BUILDER_TOKEN"],
    )
    embed_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    conn = _connect(Path(args.db))
    init_schema(conn)

    for app in apps:
        if not args.skip_crawl:
            print(f"\n=== crawling {app.name} ===")
            crawl_app(app, max_pages=args.max_pages)

        print(f"\n=== indexing {app.name} ===")
        docs = iter_extracted_parallel(RAW_DIR / app.slug)
        all_chunks = [c for d in docs for c in chunk_document(d)]
        print(f"  {len(docs)} docs → {len(all_chunks)} chunks")

        for i in range(0, len(all_chunks), BATCH):
            batch = all_chunks[i : i + BATCH]
            vectors = embed_batch(client, embed_model, [c.text for c in batch])
            payload = [
                (c, app.name, _platform_for_url(app, c.url), v)
                for c, v in zip(batch, vectors)
            ]
            n = insert_chunks(conn, payload)
            print(f"  inserted batch {i//BATCH + 1}: +{n}")

    conn.close()
    print(f"\n✓ index written to {args.db}")


if __name__ == "__main__":
    main()
