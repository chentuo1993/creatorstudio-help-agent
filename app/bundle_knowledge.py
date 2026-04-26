"""Text drawn from public Apple product descriptions for bundle-level Q&A.

Used when a query looks about the *Apple Creator Studio* subscription, not
only a single app. RAG can still add per-app Support pages; this grounds
“what is the bundle / what’s included” in consistent wording. Not legal advice;
always cite the retrieved Support links when the model answers.
"""

from __future__ import annotations

import re

# See https://support.apple.com/125029 (About Apple Creator Studio) and
# https://www.apple.com/creator-studio/ (product overview) for up-to-date facts.
BUNDLE_PREAMBLE = """BUNDLE CONTEXT (public Apple information, not a Support article)
Apple Creator Studio is a single subscription that provides professional creative
apps and related features, including (among others) Final Cut Pro, Logic Pro,
Pixelmator Pro, Motion, Compressor, and MainStage on supported platforms, plus
premium/AI and collaboration capabilities in iWork family apps: Keynote, Pages,
Numbers, and Freeform. The Final Cut Camera iPhone app is part of the
video/creative line users often use alongside the bundle. Exact availability,
pricing, device requirements, and regional offers change over time; prefer the
official Support articles in CONTEXT for specifics on subscribing, trials,
education pricing, and Family Sharing.
---
"""


BUNDLE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"apple creator studio|what'?s in creator studio|what is (included in )? creator studio|"
        r"creator studio bundle|the creator studio( subscription| plan)?\b|"
        r"what(’|')?s included( in| with)?( the)? (apple )?creator|"
        r"creator studio (subscription|price|cost|student|educat|family|trial)\b|"
        r"subscribe to( apple)? creator|included with creator studio|"
        r"与 creator studio|合辑|訂閱|订阅",
        re.IGNORECASE,
    ),
)


def is_bundle_intent(text: str) -> bool:
    t = (text or "").strip()
    if not t or len(t) < 4:
        return False
    return any(p.search(t) for p in BUNDLE_PATTERNS)


def bundle_preamble() -> str:
    return BUNDLE_PREAMBLE
