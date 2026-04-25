"""Parallel wrapper around `crawl_app` — runs every app in its own thread.

All apps share `support.apple.com`, so we cap to a small pool to stay polite
(8 workers × 0.4s/req per worker ≈ 20 req/s on Apple's CDN).
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import APPS, AppSource
from .crawl import crawl_app


def crawl_all_parallel(max_pages_per_app: int = 800, workers: int = 8) -> None:
    print(f"=== parallel crawl: {len(APPS)} apps × ≤{max_pages_per_app} pages, {workers} workers ===")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(crawl_app, app, max_pages_per_app): app for app in APPS}
        for fut in as_completed(futures):
            app: AppSource = futures[fut]
            try:
                pages = fut.result()
                print(f"✓ {app.slug}: {len(pages)} pages")
            except Exception as exc:
                print(f"✗ {app.slug}: {exc}")


if __name__ == "__main__":
    crawl_all_parallel()
