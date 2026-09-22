#!/usr/bin/env python3
"""Protocol-only adapter used by the local smoke check; never a model baseline."""

import json
import sys


def main() -> int:
    request = json.load(sys.stdin)
    source = request["input"]
    prediction = {
        "item_id": "C1-01_LOCAL_ENTRY_PRECONDITION",
        "requirement_id": source["requirement_id"],
        "match_state": "NO_MATCH",
        "subtype": "NONE",
        "evidence_text": None,
        "evidence_spans": [],
        "evidence_refs": [],
        "reasoning_factors": [],
        "missing_context_questions": [],
        "confidence": None,
        "human_review_required": False,
    }
    sys.stdout.write(json.dumps(prediction, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
