#!/usr/bin/env python3
"""Run golden-set checks against a running /api/chat (local or deployed).

    export AI_BUILDER_TOKEN=...  # if needed for a protected endpoint
    python eval/run_golden.py --base http://127.0.0.1:8000

Heuristics (not full RAGAS; see eval/run_ragas_optional.py for RAGAS):
- has_answer: response must not be the standard out-of-doc refusal
- refuse: must include the refusal phrase
- apps_any: at least one matched app or citation app in the list
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import httpx

REFUSAL = "couldn't find this in the official apple creator studio documentation"

ROOT = Path(__file__).resolve().parent


def _load() -> dict[str, Any]:
    with open(ROOT / "golden_set.json", encoding="utf-8") as f:
        return json.load(f)


def _check_item(data: dict[str, Any], item: dict[str, Any]) -> tuple[bool, str]:
    ans = (data.get("answer") or "").lower()
    expect = item.get("expect", "any")
    if expect == "refuse":
        if REFUSAL in ans:
            return True, "ok refuse"
        return False, "expected refusal, got answer"
    if expect == "has_answer":
        if REFUSAL in ans:
            return False, "unexpected refusal"
    apps_any = item.get("apps_any")
    if apps_any:
        matched = set(data.get("matched_apps") or [])
        cites = data.get("citations") or []
        from_cite = {c.get("app") for c in cites if c.get("app")}
        if not (matched & set(apps_any)) and not (from_cite & set(apps_any)):
            return False, f"app check: want one of {apps_any}, got matched={matched} cite_apps={from_cite}"
    return True, "ok"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--base", default=os.getenv("EVAL_BASE", "http://127.0.0.1:8000"), help="API base URL")
    p.add_argument("--limit", type=int, default=0, help="only first N items (0 = all)")
    args = p.parse_args()
    spec = _load()
    items = spec["items"]
    if args.limit:
        items = items[: args.limit]

    times: list[float] = []
    fail = 0
    for it in items:
        t0 = time.perf_counter()
        r = httpx.post(
            f"{args.base.rstrip('/')}/api/chat",
            json={"question": it["q"], "history": []},
            timeout=120.0,
        )
        dt = (time.perf_counter() - t0) * 1000
        times.append(dt)
        if r.status_code != 200:
            print(f"[FAIL] id={it['id']} HTTP {r.status_code} {r.text[:200]}")
            fail += 1
            continue
        data = r.json()
        ok, msg = _check_item(data, it)
        if not ok:
            print(f"[FAIL] id={it['id']}: {msg} | q={it['q'][:60]}…")
            fail += 1
        else:
            print(f"[ ok ] id={it['id']} {int(dt):>5d}ms | {it['q'][:52]}…")

    n = len(items)
    print("---")
    print(f"passed: {n - fail}/{n}  |  p50 latency: {statistics.median(times):.0f}ms  p95: {_p95(times):.0f}ms")
    sys.exit(1 if fail else 0)


def _p95(xs: list[float]) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    i = max(0, int(0.95 * (len(s) - 1)))
    return s[i]


if __name__ == "__main__":
    main()
