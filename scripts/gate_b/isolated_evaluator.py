#!/usr/bin/env python3
"""QA-only evaluator with strict ID alignment and invalid-output accounting."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime_acl import RuntimeACL, SERVICE_ACCOUNTS


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "contracts/task/c1_01_local_entry_precondition"
PREFLIGHT = BASE / "04_baseline_protocol/protocol/C1_01_Preflight_Check_V0.2.1.py"
METRIC_SPEC = BASE / "05_benchmark_metric_spec/C1_01_Benchmark_Metric_Spec_V0.2.md"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_jsonl_text(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"line {line_number}: expected object")
            rows.append(value)
    return rows


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return read_jsonl_text(path.read_text(encoding="utf-8"))


def load_prediction_validator():
    spec = importlib.util.spec_from_file_location("c101_prediction_validator", PREFLIGHT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validator: {PREFLIGHT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_prediction


def alignment(gold: list[dict[str, Any]], predictions: list[dict[str, Any]]) -> dict[str, Any]:
    gold_ids = [row.get("sample_id") for row in gold]
    prediction_ids = [row.get("sample_id") for row in predictions]
    gold_set = set(gold_ids)
    prediction_counts = Counter(prediction_ids)
    duplicate_count = sum(count > 1 for count in prediction_counts.values())
    unknown_count = sum(sample_id not in gold_set for sample_id in prediction_counts)
    missing_count = sum(sample_id not in prediction_counts for sample_id in gold_set)
    return {
        "gold_count": len(gold),
        "prediction_record_count": len(predictions),
        "duplicate_prediction_id_count": duplicate_count,
        "unknown_prediction_id_count": unknown_count,
        "missing_prediction_id_count": missing_count,
        "exact_id_alignment": duplicate_count == 0 and unknown_count == 0 and missing_count == 0 and len(gold_ids) == len(gold_set),
    }


def _prediction_state(prediction_row: dict[str, Any], validator, inp: dict[str, Any]) -> tuple[str | None, str | None, bool]:
    if prediction_row.get("status") != "VALID" or prediction_row.get("prediction") is None:
        return None, None, False
    errors = validator(prediction_row.get("prediction"), inp)
    if errors:
        return None, None, False
    prediction = prediction_row["prediction"]
    return prediction.get("match_state"), prediction.get("subtype"), True


def evaluate(gold: list[dict[str, Any]], predictions: list[dict[str, Any]], snapshot_id: str, evaluator_version: str = "C1_01_Isolated_Evaluator_V0.1") -> dict[str, Any]:
    validator = load_prediction_validator()
    align = alignment(gold, predictions)
    if not align["exact_id_alignment"]:
        return {
            "status": "INVALID_SUBMISSION",
            "snapshot_id": snapshot_id,
            "evaluator_version": evaluator_version,
            "alignment": align,
            "metrics": None,
            "gate_decision": "INVALID_SUBMISSION",
            "gold_content_exported": False,
        }
    predictions_by_id = {row["sample_id"]: row for row in predictions}
    totals = Counter()
    valid = 0
    invalid = 0
    match_tp = 0
    subtype_correct = 0
    predicted_match = 0
    gold_match = 0
    needs_context_total = 0
    needs_context_correct = 0
    hard_negative_total = 0
    hard_negative_fp = 0
    evidence_total = 0
    evidence_hit = 0
    pair_rows: defaultdict[str, list[tuple[str, str | None, str | None, str | None, str | None]]] = defaultdict(list)
    by_state = Counter()

    for gold_row in gold:
        sample_id = gold_row["sample_id"]
        target = gold_row.get("target") or {}
        gold_state = target.get("match_state")
        gold_subtype = target.get("subtype")
        pred_row = predictions_by_id[sample_id]
        pred_state, pred_subtype, is_valid = _prediction_state(pred_row, validator, gold_row["input"])
        valid += is_valid
        invalid += not is_valid
        totals["total"] += 1
        by_state[gold_state] += 1
        if gold_state == "MATCH":
            gold_match += 1
            if is_valid and pred_state == "MATCH":
                match_tp += 1
                if pred_subtype == gold_subtype:
                    subtype_correct += 1
            if is_valid and pred_state == "MATCH" and pred_row["prediction"].get("evidence_spans"):
                evidence_hit += 1
            evidence_total += 1
        if is_valid and pred_state == "MATCH":
            predicted_match += 1
        if gold_state == "NEEDS_CONTEXT":
            needs_context_total += 1
            if is_valid and pred_state == "NEEDS_CONTEXT":
                needs_context_correct += 1
        if gold_row.get("metadata", {}).get("case_slice") in {"HARD_NEGATIVE", "OFFICIAL_ANCHOR_HARD_NEGATIVE", "COUNTERFACTUAL_HARD_NEGATIVE"}:
            hard_negative_total += 1
            if is_valid and pred_state == "MATCH":
                hard_negative_fp += 1
        pair_id = gold_row.get("metadata", {}).get("pair_id")
        if pair_id:
            pair_rows[pair_id].append((gold_state, gold_subtype, pred_state, pred_subtype, "valid" if is_valid else "invalid"))

    structured_rate = valid / totals["total"] if totals["total"] else 0.0
    match_recall = match_tp / gold_match if gold_match else None
    match_precision = match_tp / predicted_match if predicted_match else None
    needs_context_accuracy = needs_context_correct / needs_context_total if needs_context_total else None
    hard_negative_fpr = hard_negative_fp / hard_negative_total if hard_negative_total else None
    evidence_hit_rate = evidence_hit / evidence_total if evidence_total else None
    match_f1 = (
        2 * match_precision * match_recall / (match_precision + match_recall)
        if match_precision is not None and match_recall is not None and match_precision + match_recall
        else None
    )
    pair_correct = sum(
        len(rows) == 2 and all(row[4] == "valid" and row[0] == row[2] and row[1] == row[3] for row in rows)
        for rows in pair_rows.values()
    )
    pair_accuracy = pair_correct / len(pair_rows) if pair_rows else None
    metrics = {
        "sample_count": totals["total"],
        "valid_prediction_count": valid,
        "invalid_prediction_count": invalid,
        "structured_output_valid_rate": structured_rate,
        "match_recall": match_recall,
        "match_precision": match_precision,
        "match_subtype_accuracy": subtype_correct / gold_match if gold_match else None,
        "match_f1": match_f1,
        "match_f1_vs_same_snapshot_base_model": None,
        "needs_context_accuracy": needs_context_accuracy,
        "hard_negative_fpr": hard_negative_fpr,
        "evidence_hit_rate": evidence_hit_rate,
        "counterfactual_pair_accuracy": pair_accuracy,
        "gold_state_counts": dict(by_state),
    }
    gate_results = {
        "blind_test_n_ge_50": totals["total"] >= 50,
        "structured_output_valid_rate": structured_rate >= 1.0,
        "match_recall": match_recall is not None and match_recall >= 0.90,
        "match_precision": match_precision is not None and match_precision >= 0.85,
        "hard_negative_fpr": hard_negative_fpr is not None and hard_negative_fpr <= 0.15,
        "evidence_hit_rate": evidence_hit_rate is not None and evidence_hit_rate >= 0.90,
        "counterfactual_pair_accuracy": pair_accuracy is not None and pair_accuracy >= 0.90,
        "match_f1_vs_same_snapshot_base_model": None,
    }
    decision = "PASS" if all(value is True for value in gate_results.values()) else ("BLOCKED_READINESS_GAP" if not gate_results["blind_test_n_ge_50"] or any(value is None for value in gate_results.values()) else "FAIL")
    return {
        "status": "PASS" if decision == "PASS" else "READINESS_GAP" if decision == "BLOCKED_READINESS_GAP" else "FAIL",
        "snapshot_id": snapshot_id,
        "evaluator_version": evaluator_version,
        "metric_spec": {"version": "C1_01_Benchmark_Metric_Spec_V0.2", "sha256": sha256_bytes(METRIC_SPEC.read_bytes())},
        "alignment": align,
        "metrics": metrics,
        "gate_results": gate_results,
        "gate_decision": decision,
        "gold_content_exported": False,
    }


def evaluate_files(gold_path: Path, predictions_path: Path, output_path: Path, audit_path: Path, snapshot_id: str) -> dict[str, Any]:
    acl = RuntimeACL(audit_path)
    gold_text = acl.read_asset("QA", SERVICE_ACCOUNTS["QA"], "blind_test_gold", gold_path)
    result = evaluate(read_jsonl_text(gold_text), read_jsonl(predictions_path), snapshot_id)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--audit-log", required=True, type=Path)
    parser.add_argument("--snapshot-id", required=True)
    args = parser.parse_args()
    result = evaluate_files(args.gold, args.predictions, args.output, args.audit_log, args.snapshot_id)
    print(json.dumps({"status": result["status"], "gate_decision": result["gate_decision"], "alignment": result["alignment"], "metrics": result["metrics"]}, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"PASS", "READINESS_GAP"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
