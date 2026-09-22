#!/usr/bin/env python3
"""Deterministic protocol smoke adapter; this is not a model baseline."""
from __future__ import annotations

import json
import sys


def output(request: dict) -> dict:
    inp = request["input"]
    clause = inp["clause_text"]
    if clause == "__INVALID_JSON__":
        raise RuntimeError("__INVALID_JSON__")
    ref = {
        "document_id": inp["document_id"],
        "document_version": inp["document_version"],
        "page": inp["source_location"]["page"],
        "section": inp["source_location"]["section"],
    }
    span = {
        "text": clause,
        "anchor": "CLAUSE",
        "context_id": None,
        **ref,
        "start_char": 0,
        "end_char": len(clause),
    }
    if "本市注册" in clause:
        state, subtype, factors, questions, review = (
            "MATCH", "SUPPLIER_REGISTRATION_LOCATION",
            ["supplier_location_attribute", "pre_award_condition", "market_entry_gate"], [], False,
        )
    elif "本地化服务能力" in clause:
        state, subtype, factors, questions, review = (
            "NEEDS_CONTEXT", "NONE", ["local_service_term_ambiguous"],
            ["是否要求投标时已在指定地区注册或设立机构？"], True,
        )
    else:
        state, subtype, factors, questions, review = (
            "NO_MATCH", "NONE", ["post_award_service"], [], False,
        )
    return {
        "item_id": request["task_id"],
        "requirement_id": inp["requirement_id"],
        "match_state": state,
        "subtype": subtype,
        "evidence_text": clause,
        "evidence_spans": [span],
        "evidence_refs": [ref],
        "reasoning_factors": factors,
        "missing_context_questions": questions,
        "confidence": None,
        "human_review_required": review,
    }


request = json.load(sys.stdin)
if request["input"]["clause_text"] == "__INVALID_JSON__":
    sys.stdout.write("{invalid-json")
else:
    sys.stdout.write(json.dumps(output(request), ensure_ascii=False))
