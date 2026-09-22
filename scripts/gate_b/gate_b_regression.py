#!/usr/bin/env python3
"""Run Gate-B synthetic evaluator, alignment, and access-boundary regressions."""
from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any

from isolated_evaluator import evaluate, evaluate_files
from runtime_acl import probe_matrix


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/gate_b/C1_01_Synthetic_Blind_Input_V0.1.jsonl"
TASK = "C1-01_LOCAL_ENTRY_PRECONDITION"


CASES = {
    "S-C101-GB-001": ("MATCH", "SUPPLIER_REGISTRATION_LOCATION", "TYPICAL_POSITIVE", None),
    "S-C101-GB-002": ("MATCH", "DISTANCE_TO_PURCHASER", "TYPICAL_POSITIVE", None),
    "S-C101-GB-003": ("MATCH", "PREEXISTING_LOCAL_BRANCH", "TYPICAL_POSITIVE", None),
    "S-C101-GB-004": ("MATCH", "OTHER_RELATED", "HARD_POSITIVE", None),
    "S-C101-GB-005": ("NO_MATCH", "NONE", "NORMAL_NEGATIVE", None),
    "S-C101-GB-006": ("NO_MATCH", "NONE", "HARD_NEGATIVE", None),
    "S-C101-GB-007": ("NEEDS_CONTEXT", "NONE", "MISSING_CONTEXT", None),
    "S-C101-GB-008": ("NEEDS_CONTEXT", "NONE", "EXCEPTION_REVIEW", None),
    "S-C101-GB-009": ("MATCH", "SUPPLIER_REGISTRATION_LOCATION", "COUNTERFACTUAL_POSITIVE", "PAIR-GB-001"),
    "S-C101-GB-010": ("NO_MATCH", "NONE", "COUNTERFACTUAL_HARD_NEGATIVE", "PAIR-GB-001"),
    "S-C101-GB-011": ("MATCH", "PREEXISTING_LOCAL_BRANCH", "OFFICIAL_ANCHOR_HARD_POSITIVE", None),
    "S-C101-GB-012": ("NO_MATCH", "NONE", "OFFICIAL_ANCHOR_HARD_NEGATIVE", None),
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def target_for(row: dict[str, Any], state: str, subtype: str) -> dict[str, Any]:
    inp = row["input"]
    ref = {
        "document_id": inp["document_id"],
        "document_version": inp["document_version"],
        "page": inp["source_location"]["page"],
        "section": inp["source_location"]["section"],
    }
    clause = inp["clause_text"]
    span = {"text": clause, "anchor": "CLAUSE", "context_id": None, **ref, "start_char": 0, "end_char": len(clause)}
    if state == "MATCH":
        factors = {
            "SUPPLIER_REGISTRATION_LOCATION": ["supplier_location_attribute", "market_entry_gate"],
            "DISTANCE_TO_PURCHASER": ["distance_to_purchaser", "market_entry_gate"],
            "PREEXISTING_LOCAL_BRANCH": ["preexisting_branch", "market_entry_gate"],
            "OTHER_RELATED": ["supplier_location_attribute", "pre_award_condition"],
        }[subtype]
        questions: list[str] = []
        human_review = False
    elif state == "NEEDS_CONTEXT":
        factors = ["cross_reference_missing"] if "第七项" in clause else ["exception_needs_review"]
        questions = ["请补充缺失的适用依据或完整交叉引用。"]
        human_review = True
    else:
        factors = ["post_award_service"] if "中标后" in clause or "任意地区" in clause else ["location_mention_only"]
        questions = []
        human_review = False
    return {
        "item_id": TASK,
        "requirement_id": inp["requirement_id"],
        "match_state": state,
        "subtype": subtype,
        "evidence_text": clause,
        "evidence_spans": [span],
        "evidence_refs": [ref],
        "reasoning_factors": factors,
        "missing_context_questions": questions,
        "confidence": None,
        "human_review_required": human_review,
    }


def make_gold(inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gold: list[dict[str, Any]] = []
    for row in inputs:
        state, subtype, case_slice, pair_id = CASES[row["sample_id"]]
        gold.append({
            "sample_id": row["sample_id"],
            "input": row["input"],
            "target": target_for(row, state, subtype),
            "metadata": {"case_slice": case_slice, "pair_id": pair_id},
        })
    return gold


def make_predictions(gold: list[dict[str, Any]]) -> list[dict[str, Any]]:
    predictions: list[dict[str, Any]] = []
    for row in gold:
        if row["sample_id"] == "S-C101-GB-006":
            predictions.append({
                "sample_id": row["sample_id"],
                "requirement_id": row["input"]["requirement_id"],
                "status": "INVALID",
                "raw_output": "{invalid-json",
                "prediction": None,
                "validation_errors": ["INVALID_JSON"],
            })
        else:
            prediction = copy.deepcopy(row["target"])
            predictions.append({
                "sample_id": row["sample_id"],
                "requirement_id": row["input"]["requirement_id"],
                "status": "VALID",
                "raw_output": json.dumps(prediction, ensure_ascii=False),
                "prediction": prediction,
                "validation_errors": [],
            })
    return predictions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/gate_b")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    inputs = read_jsonl(FIXTURE)
    gold = make_gold(inputs)
    predictions = make_predictions(gold)
    with tempfile.TemporaryDirectory(prefix="c101-gate-b-regression-") as directory:
        temp = Path(directory)
        gold_path = temp / "blind_test_gold.jsonl"
        prediction_path = temp / "predictions.jsonl"
        gold_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in gold), encoding="utf-8")
        prediction_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in predictions), encoding="utf-8")
        evaluation_path = temp / "evaluation.json"
        result = evaluate_files(
            gold_path,
            prediction_path,
            evaluation_path,
            temp / "access_audit.jsonl",
            "C1_01_Synthetic_GateB_Regression_V0.1",
        )
        assert result["status"] == "READINESS_GAP"
        assert result["gate_decision"] == "BLOCKED_READINESS_GAP"
        assert result["metrics"]["sample_count"] == len(inputs)
        assert result["metrics"]["invalid_prediction_count"] == 1
        assert result["metrics"]["structured_output_valid_rate"] == (len(inputs) - 1) / len(inputs)
        alignment_checks = {}
        duplicate = predictions + [copy.deepcopy(predictions[0])]
        alignment_checks["duplicate_id"] = evaluate(gold, duplicate, "synthetic") ["gate_decision"]
        unknown = copy.deepcopy(predictions)
        unknown[0]["sample_id"] = "S-C101-GB-UNKNOWN"
        alignment_checks["unknown_id"] = evaluate(gold, unknown, "synthetic")["gate_decision"]
        missing = predictions[:-1]
        alignment_checks["missing_id"] = evaluate(gold, missing, "synthetic")["gate_decision"]
        assert all(value == "INVALID_SUBMISSION" for value in alignment_checks.values())
        evaluation_report = {
            "status": "PASS",
            "fixture": FIXTURE.relative_to(ROOT).as_posix(),
            "synthetic_sample_count": len(inputs),
            "coverage_declared_by_fixture": {
                "match_subtypes": sorted({case[1] for case in CASES.values() if case[0] == "MATCH"}),
                "match_states": sorted({case[0] for case in CASES.values()}),
                "hard_negative": True,
                "counterfactual_pair": True,
            },
            "evaluation_status": result["status"],
            "gate_decision": result["gate_decision"],
            "invalid_denominator_check": {
                "invalid_count": result["metrics"]["invalid_prediction_count"],
                "structured_output_valid_rate": result["metrics"]["structured_output_valid_rate"],
                "pass": result["metrics"]["invalid_prediction_count"] == 1,
            },
            "alignment_checks": alignment_checks,
            "gold_written_to_repository": False,
            "readiness_gap": "synthetic fixture has N<50; no formal Benchmark Ready claim",
        }
        (args.output_dir / "C1_01_Gate_B_Evaluator_Regression_V0.1.json").write_text(json.dumps(evaluation_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        acl_report = probe_matrix(temp / "acl", args.output_dir / "C1_01_Gate_B_Access_Boundary_Regression_V0.1.json")
        assert acl_report["status"] == "PASS"
    print(json.dumps({"status": "PASS", "evaluator": evaluation_report, "acl": {"status": acl_report["status"], "denied_probe_count": acl_report["denied_probe_count"], "allowed_probe_count": acl_report["allowed_probe_count"]}}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
