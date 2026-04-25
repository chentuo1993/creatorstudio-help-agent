"""Stage 1 — discover and fetch Apple Support guide pages.

Strategy: BFS from each app's welcome URL(s), following every in-scope
link under support.apple.com/guide/{slug}/.... Persists raw HTML so
later stages are deterministic and re-runnable.
"""

from __future__ import annotations

import time
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from .config import (
    ALLOWED_DOMAIN,
    APPS,
    REQUEST_DELAY_SEC,
    URL_PREFIX,
    USER_AGENT,
    AppSource,
)

RAW_DIR = Path("raw")


def _safe_filename(url: str) -> str:
    return url.replace("https://", "").replace("/", "_")[:200] + ".html"


def _normalize(url: str) -> str:
    """Strip fragment and trailing slash so /foo and /foo#x dedupe."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def _scope_keys(app: AppSource) -> tuple[str, ...]:
    """Path fragments that identify pages belonging to this app's guide."""
    keys = [f"/guide/{app.slug}/", f"/guide/{app.slug}-"]
    return tuple(keys)


def _is_in_scope(url: str, app: AppSource) -> bool:
    if not url.startswith(URL_PREFIX):
        return False
    if urlparse(url).netloc != ALLOWED_DOMAIN:
        return False
    return any(k in url for k in _scope_keys(app))


def crawl_app(app: AppSource, max_pages: int = 1000) -> list[Path]:
    """BFS-crawl a single app's user guide. Stops when frontier is empty
    or max_pages is reached.
    """
    out_dir = RAW_DIR / app.slug
    out_dir.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    queue: deque[str] = deque()
    written: list[Path] = []

    for w in app.welcome_urls:
        n = _normalize(w)
        if n not in seen:
            seen.add(n)
            queue.append(n)

    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=20.0) as client:
        while queue and len(written) < max_pages:
            url = queue.popleft()
            path = out_dir / _safe_filename(url)
            html: str
            if path.exists() and path.stat().st_size > 0:
                html = path.read_text(encoding="utf-8")
            else:
                try:
                    resp = client.get(url, follow_redirects=True)
                except httpx.HTTPError as exc:
                    print(f"[skip] {url}: {exc}")
                    continue
                if resp.status_code != 200:
                    print(f"[skip] {url}: {resp.status_code}")
                    continue
                html = resp.text
                path.write_text(html, encoding="utf-8")
                time.sleep(REQUEST_DELAY_SEC)

            written.append(path)
            if len(written) % 50 == 0:
                print(f"  [{app.slug}] {len(written)} pages, queue={len(queue)}")

            soup = BeautifulSoup(html, "lxml")
            for a in soup.select("a[href]"):
                href = a.get("href")
                if not href or href.startswith("#"):
                    continue
                cand = _normalize(urljoin(url, href))
                if _is_in_scope(cand, app) and cand not in seen:
                    seen.add(cand)
                    queue.append(cand)

    print(f"[{app.slug}] done: {len(written)} pages, frontier left={len(queue)}")
    return written


def crawl_all(max_pages_per_app: int = 1000) -> None:
    for app in APPS:
        print(f"\n=== crawling {app.name} ===")
        crawl_app(app, max_pages=max_pages_per_app)


if __name__ == "__main__":
    crawl_all(max_pages_per_app=1000)
