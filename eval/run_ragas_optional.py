#!/usr/bin/env python3
"""Optional RAGAS-based evaluation. Install extras first:

    pip install ragas datasets

Then set OPENAI_API_KEY or use the same AI Builders base URL with your
AI_BUILDER_TOKEN in the environment. This script is a stub: wire RAGAS
`evaluate()` with your dataset and LLM/embedding when you need faithfulness
scores in CI. For day-to-day checks, use `run_golden.py` instead.
"""

from __future__ import annotations

import os
import sys

def main() -> None:
    try:
        import ragas  # noqa: F401
    except ImportError:
        print(
            "RAGAS is not installed. To use full faithfulness/answer_relevancy metrics:\n"
            "  pip install ragas datasets\n"
            "Then implement dataset loading from eval/golden_set.json and call ragas.evaluate()."
        )
        sys.exit(0)
    print("RAGAS is available. Add your evaluate() integration here (optional).")
    if not os.environ.get("AI_BUILDER_TOKEN"):
        print("Tip: set AI_BUILDER_TOKEN for OpenAI-compatible endpoints on AI Builders Space.")


if __name__ == "__main__":
    main()
