"""Cheap app classifier — narrows retrieval to one or two apps when possible."""

from __future__ import annotations

import re

KNOWN_APPS = {
    "Final Cut Pro": [r"final\s*cut\s*pro", r"\bfcp\b"],
    "Final Cut Camera": [r"final\s*cut\s*camera", r"\bfcc\b"],
    "Motion": [r"\bmotion\b"],
    "Compressor": [r"\bcompressor\b"],
    "Logic Pro": [r"logic\s*pro", r"\blogic\b"],
    "MainStage": [r"main\s*stage"],
    "Pixelmator Pro": [r"pixelmator"],
    "Keynote": [r"\bkeynote\b"],
    "Pages": [r"\bpages\b"],
    "Numbers": [r"\bnumbers\b"],
    "Freeform": [r"\bfreeform\b"],
}


def classify_apps(query: str) -> list[str]:
    """Return the list of apps mentioned in `query`. Empty = search all."""
    q = query.lower()
    hits: list[str] = []
    for app, patterns in KNOWN_APPS.items():
        if any(re.search(p, q) for p in patterns):
            hits.append(app)
    return hits
