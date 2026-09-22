#!/usr/bin/env python3
"""Frozen C1-01 Baseline Protocol V0.2.1 runner and scorer.

The runner performs the preflight gate before starting an adapter. It never
repairs, drops, or silently retries an invalid model response.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shlex
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from preflight_check import (
    PROTOCOL,
    TARGET_KEYS,
    TASK,
    _exact_source,
    read_jsonl,
    run_preflight,
    validate_prediction,
)


ROOT = Path(__file__).resolve().parent
LOCK = ROOT / "C1_01_Baseline_Protocol_V0.2.1.lock.json"
OUTPUT_SCHEMA = ROOT / "C1_01_Model_Output_Schema_V0.2.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def project_input(row: dict[str, Any]) -> dict[str, Any]:
    """Allowlisted input projection. Target and metadata never reach a model."""
    source = row["input"]
    fields = (
        "requirement_id", "project_id", "document_id", "document_version",
        "clause_id", "clause_text", "business_stage", "context",
        "source_location", "parser_quality", "source_defect_prevents_judgment",
        "source_defect_reason",
    )
    return {field: source[field] for field in fields}


def strict_parse(raw: str) -> tuple[Any | None, list[str]]:
    """Parse exactly one JSON value, with no Markdown fence or prose repair."""
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, [f"INVALID_JSON: {exc.msg}"]
    if not isinstance(value, dict):
        return None, ["INVALID_OUTPUT: top-level JSON must be an object"]
    return value, []


def run_adapter(command: list[str], request: dict[str, Any], timeout_seconds: int) -> tuple[str, Any | None, list[str], float]:
    started = time.monotonic()
    try:
        done = subprocess.run(
            command,
            input=json.dumps(request, ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "", None, ["ADAPTER_TIMEOUT"], (time.monotonic() - started) * 1000
    except OSError as exc:
        return "", None, [f"ADAPTER_EXEC_ERROR: {exc}"], (time.monotonic() - started) * 1000
    if done.returncode:
        return done.stdout, None, [f"ADAPTER_EXIT_{done.returncode}: {done.stderr[:300]}"], (time.monotonic() - started) * 1000
    value, errors = strict_parse(done.stdout)
    return done.stdout, value, errors, (time.monotonic() - started) * 1000


def model_request(inp: dict[str, Any], mode: str = "zero_shot", examples: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "protocol_version": "0.2.1",
        "task_id": TASK,
        "mode": mode,
        "instruction": (
            "Return ONLY one JSON object matching output_contract. "
            "Classify the C1-01 candidate requirement; do not decide legality, guilt, or punishment. "
            "Use exact source spans with Python Unicode half-open offsets. "
            "Do not output Markdown, prose, a wrapper object, or chain of thought."
        ),
        "input": inp,
        "examples": examples or [],
        "output_contract": json.loads(OUTPUT_SCHEMA.read_text(encoding="utf-8")),
        "generation": {"temperature": 0.0, "seed": 42},
    }


def execute_one(row: dict[str, Any], command: list[str], timeout_seconds: int, *, smoke: bool = False, examples: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Execute one input. Assembly-invalid rows are refused before adapter call."""
    annotation_state = row.get("annotation_state")
    metadata = row.get("metadata", {})
    blocked_reason = None
    if annotation_state == "UNAVAILABLE_SOURCE_REWORK" or metadata.get("data_eligibility") == "REWORK_SOURCE":
        blocked_reason = "REWORK_SOURCE"
    elif metadata.get("data_eligibility") in {"HOLD", "PENDING_DATA_QA"}:
        blocked_reason = metadata["data_eligibility"]
    elif metadata.get("review_state") == "DISPUTED":
        blocked_reason = "DISPUTED"
    elif metadata.get("dataset_role") == "BLIND_GOLD":
        blocked_reason = "BLIND_GOLD"
    if blocked_reason:
        return {
            "sample_id": row.get("sample_id"),
            "requirement_id": row.get("input", {}).get("requirement_id"),
            "status": "REFUSED_INPUT",
            "raw_output": None,
            "prediction": None,
            "validation_errors": [f"{blocked_reason} is not a model input"],
            "latency_ms": 0.0,
        }
    inp = project_input(row)
    raw, prediction, errors, latency = run_adapter(command, model_request(inp, "few_shot" if examples else "zero_shot", examples), timeout_seconds)
    if not errors:
        errors = validate_prediction(prediction, inp)
    return {
        "sample_id": row.get("sample_id"),
        "requirement_id": inp.get("requirement_id"),
        "status": "VALID" if not errors else "INVALID",
        "raw_output": raw,
        "prediction": prediction if isinstance(prediction, dict) else None,
        "validation_errors": errors,
        "latency_ms": round(latency, 1),
    }


def formal_run(args: argparse.Namespace) -> int:
    preflight = run_preflight(args.manifest, train=args.train, dev=args.dev, blind_input=args.blind_input, smoke=False)
    if preflight["status"] != "PASS":
        report = {"protocol": PROTOCOL, "status": "RUN_ABORTED", "preflight": preflight, "predictions_started": False}
        if args.run_manifest:
            write_json(args.run_manifest, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2

    dev_rows = read_jsonl(Path(args.dev))
    examples: list[dict[str, Any]] = []
    if args.few_shot:
        train_rows = read_jsonl(Path(args.few_shot))
        for row in train_rows:
            examples.append({"input": project_input(row), "target": row["target"]})
    command = shlex.split(args.adapter_command)
    if not command:
        raise ValueError("adapter command is empty")
    predictions = [execute_one(row, command, args.timeout_seconds, examples=examples) for row in dev_rows]
    Path(args.output).write_text(
        "".join(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n" for value in predictions),
        encoding="utf-8",
    )
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    run_record = {
        "protocol": PROTOCOL,
        "protocol_sha256": sha256_file(ROOT / "C1_01_Baseline_Protocol_V0.2.1.md"),
        "protocol_lock_sha256": sha256_file(LOCK),
        "status": "PREDICTIONS_WRITTEN",
        "preflight": preflight,
        "predictions_started": True,
        "input_role": "DEV",
        "model_id": args.model_id,
        "model_revision": args.model_revision,
        "adapter_command": command,
        "mode": "few_shot" if examples else "zero_shot",
        "few_shot_count": len(examples),
        "schema_version": lock["dependencies"]["dataset_schema"]["version"],
        "schema_hash": lock["dependencies"]["dataset_schema"]["sha256"],
        "spec_version": lock["dependencies"]["business_spec"]["version"],
        "spec_hash": lock["dependencies"]["business_spec"]["sha256"],
        "label_guide_version": lock["dependencies"]["label_guide"]["version"],
        "label_guide_hash": lock["dependencies"]["label_guide"]["sha256"],
        "metric_spec_version": lock["dependencies"]["metric_spec"]["version"],
        "metric_spec_hash": lock["dependencies"]["metric_spec"]["sha256"],
        "blind_test_rule_version": lock["dependencies"]["blind_test_rules"]["version"],
        "blind_test_rule_hash": lock["dependencies"]["blind_test_rules"]["sha256"],
        "blind_gold_boundary_version": lock["dependencies"]["blind_gold_boundary"]["version"],
        "blind_gold_boundary_hash": lock["dependencies"]["blind_gold_boundary"]["sha256"],
        "input_sha256": sha256_file(Path(args.dev)),
        "predictions_sha256": sha256_file(Path(args.output)),
        "valid_prediction_count": sum(row["status"] == "VALID" for row in predictions),
        "invalid_prediction_count": sum(row["status"] == "INVALID" for row in predictions),
    }
    if args.run_manifest:
        write_json(args.run_manifest, run_record)
    print(json.dumps({"status": run_record["status"], "count": len(predictions), "valid": run_record["valid_prediction_count"], "invalid": run_record["invalid_prediction_count"]}, ensure_ascii=False))
    return 0


def _smoke_input(requirement_id: str, clause: str, stage: str = "QUALIFICATION") -> dict[str, Any]:
    return {
        "schema_version": "0.2",
        "schema_sha256": "smoke",
        "task_id": TASK,
        "sample_id": f"S-C101-SMOKE-{requirement_id}",
        "leakage_group_id": f"LG-SMOKE-{requirement_id}",
        "annotation_state": "LABELED",
        "input": {
            "requirement_id": requirement_id,
            "project_id": "P-SMOKE",
            "document_id": "DOC-SMOKE",
            "document_version": "V1",
            "clause_id": f"CL-{requirement_id}",
            "clause_text": clause,
            "business_stage": stage,
            "context": None,
            "source_location": {"page": 1, "section": "smoke"},
            "parser_quality": "PASS",
            "source_defect_prevents_judgment": False,
            "source_defect_reason": None,
        },
        "target": {"placeholder": True},
        "metadata": {
            "dataset_role": "DEV",
            "data_eligibility": "TRAIN_ELIGIBLE",
            "review_state": "INTERNAL_REVIEWED",
            "source_kind": "PROCUREMENT_DOCUMENT",
            "source_verified_at_procurement_document_level": True,
            "evidence_status": "VERIFIED",
        },
    }


def _smoke_rework() -> dict[str, Any]:
    row = _smoke_input("REQ-REWORK", "供应商地址距采购人不超过[OCR缺失]，按附表评分。")
    row["annotation_state"] = "UNAVAILABLE_SOURCE_REWORK"
    row["target"] = None
    row["metadata"].update(dataset_role="REWORK_QUEUE", data_eligibility="REWORK_SOURCE")
    row["input"].update(parser_quality="UNCERTAIN", source_defect_prevents_judgment=True, source_defect_reason="OCR threshold and table are missing")
    return row


def smoke_run(args: argparse.Namespace) -> int:
    preflight = run_preflight(args.manifest, smoke=True)
    if preflight["status"] != "PASS":
        print(json.dumps({"status": "SMOKE_ABORTED", "preflight": preflight}, ensure_ascii=False, indent=2))
        return 2
    command = shlex.split(args.adapter_command)
    cases = [
        ("MATCH", _smoke_input("REQ-MATCH", "投标人须在本市注册。")),
        ("NO_MATCH", _smoke_input("REQ-NO", "中标后建立满足两小时响应的服务机制。", "CONTRACT")),
        ("NEEDS_CONTEXT", _smoke_input("REQ-CONTEXT", "供应商应具备本地化服务能力。", "TECHNICAL")),
    ]
    results = []
    for expected, row in cases:
        result = execute_one(row, command, args.timeout_seconds, smoke=True)
        actual = (result.get("prediction") or {}).get("match_state")
        results.append({"case": expected, "pass": result["status"] == "VALID" and actual == expected, "status": result["status"], "actual": actual, "errors": result["validation_errors"]})
    refused = execute_one(_smoke_rework(), command, args.timeout_seconds, smoke=True)
    results.append({"case": "REWORK_SOURCE", "pass": refused["status"] == "REFUSED_INPUT", "status": refused["status"], "errors": refused["validation_errors"]})
    invalid = execute_one(_smoke_input("REQ-INVALID", "__INVALID_JSON__"), command, args.timeout_seconds, smoke=True)
    results.append({"case": "INVALID_JSON", "pass": invalid["status"] == "INVALID" and any(x.startswith("INVALID_JSON") for x in invalid["validation_errors"]), "status": invalid["status"], "errors": invalid["validation_errors"]})

    # A changed dependency hash and a changed dependency version must abort preflight.
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="c101-preflight-") as tmp:
        tmp_path = Path(tmp)
        copied_root = tmp_path / "bundle"
        import shutil
        shutil.copytree(ROOT, copied_root)
        bad_hash = json.loads((copied_root / LOCK.name).read_text(encoding="utf-8"))
        bad_hash["dependencies"]["dataset_schema"]["sha256"] = "0" * 64
        (copied_root / LOCK.name).write_text(json.dumps(bad_hash), encoding="utf-8")
        hash_report = run_preflight(copied_root / LOCK.name, smoke=True)
        results.append({"case": "Schema hash mismatch", "pass": hash_report["status"] == "RUN_ABORTED", "status": hash_report["status"], "errors": hash_report["errors"]})
        bad_version = json.loads((copied_root / LOCK.name).read_text(encoding="utf-8"))
        bad_version["dependencies"]["dataset_schema"]["sha256"] = lock["dependencies"]["dataset_schema"]["sha256"]
        bad_version["dependencies"]["dataset_schema"]["version"] = "C1_01_Dataset_Schema_V9.9"
        (copied_root / LOCK.name).write_text(json.dumps(bad_version), encoding="utf-8")
        version_report = run_preflight(copied_root / LOCK.name, smoke=True)
        results.append({"case": "Version hash mismatch", "pass": version_report["status"] == "RUN_ABORTED", "status": version_report["status"], "errors": version_report["errors"]})
    report = {"protocol": PROTOCOL, "status": "PASS" if all(x["pass"] for x in results) else "FAIL", "results": results}
    if args.output:
        write_json(args.output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


def score_run(args: argparse.Namespace) -> int:
    gold_rows = read_jsonl(Path(args.gold))
    prediction_rows = read_jsonl(Path(args.predictions))
    gold = {row["sample_id"]: row for row in gold_rows}
    predicted = {row["sample_id"]: row for row in prediction_rows}
    if set(gold) != set(predicted):
        missing, extra = sorted(set(gold) - set(predicted)), sorted(set(predicted) - set(gold))
        raise ValueError(f"prediction/gold ID mismatch; missing={missing}, extra={extra}")
    if any(row.get("metadata", {}).get("dataset_role") == "BLIND_GOLD" for row in gold_rows) and not args.qa_blind:
        raise ValueError("BLIND_GOLD scoring requires the test-team-only --qa-blind environment")
    counts = Counter(total=len(gold_rows))
    pairs: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    details = []
    for sample_id, gold_row in gold.items():
        truth = gold_row.get("target")
        pred_row = predicted[sample_id]
        pred = pred_row.get("prediction") if pred_row.get("status") == "VALID" else None
        errors = [] if pred is not None else list(pred_row.get("validation_errors") or ["INVALID prediction"])
        if pred is not None:
            errors.extend(validate_prediction(pred, gold_row["input"]))
        state = pred.get("match_state") if pred is not None and not errors else "INVALID"
        gold_state = truth["match_state"]
        counts["valid"] += not errors
        counts["invalid"] += bool(errors)
        counts["gold_MATCH"] += gold_state == "MATCH"
        counts["gold_NEEDS_CONTEXT"] += gold_state == "NEEDS_CONTEXT"
        counts["tp"] += state == "MATCH" and gold_state == "MATCH"
        counts["fp"] += state == "MATCH" and gold_state != "MATCH"
        counts["fn"] += state != "MATCH" and gold_state == "MATCH"
        counts["needs_context_correct"] += state == "NEEDS_CONTEXT" and gold_state == "NEEDS_CONTEXT"
        slice_name = gold_row.get("metadata", {}).get("case_slice", "UNSPECIFIED")
        hard = gold_state == "NO_MATCH" and slice_name in {"HARD_NEGATIVE", "OFFICIAL_ANCHOR_HARD_NEGATIVE", "COUNTERFACTUAL_HARD_NEGATIVE"}
        counts["hard_negative_total"] += hard
        counts["hard_negative_fp"] += hard and state == "MATCH"
        overlap = False
        if pred is not None and not errors and gold_state == "MATCH" and state == "MATCH":
            for a in pred.get("evidence_spans", []):
                for b in truth.get("evidence_spans", []):
                    if a.get("anchor") == b.get("anchor") and a.get("context_id") == b.get("context_id") and max(a.get("start_char", 0), b.get("start_char", 0)) < min(a.get("end_char", 0), b.get("end_char", 0)):
                        overlap = True
            counts["evidence_overlap_hit"] += overlap
        pair_id = gold_row.get("metadata", {}).get("pair_id")
        if pair_id:
            pairs[pair_id].append((gold_state, state, gold_row.get("leakage_group_id")))
        details.append({"sample_id": sample_id, "gold_state": gold_state, "pred_state": state, "valid": not errors, "errors": errors, "evidence_overlap_hit": overlap})
    def ratio(n: int, d: int) -> float | None:
        return n / d if d else None
    precision = ratio(counts["tp"], counts["tp"] + counts["fp"])
    recall = ratio(counts["tp"], counts["gold_MATCH"])
    f1 = 2 * precision * recall / (precision + recall) if precision is not None and recall is not None and precision + recall else None
    complete_pairs = [v for v in pairs.values() if len(v) == 2 and v[0][2] == v[1][2] and v[0][0] != v[1][0]]
    correct_pairs = sum(a[0] == a[1] and b[0] == b[1] for a, b in (pair for pair in complete_pairs))
    metrics = {
        "protocol": PROTOCOL,
        "status": "QA_BLIND_INTERNAL_SILVER" if args.qa_blind else "DEV_INTERNAL_SILVER",
        "counts": dict(counts),
        "match_precision": precision,
        "match_recall": recall,
        "match_f1": f1,
        "hard_negative_fpr": ratio(counts["hard_negative_fp"], counts["hard_negative_total"]),
        "needs_context_recall": ratio(counts["needs_context_correct"], counts["gold_NEEDS_CONTEXT"]),
        "structured_output_valid_rate": ratio(counts["valid"], counts["total"]),
        "evidence_overlap_proxy_recall": ratio(counts["evidence_overlap_hit"], counts["gold_MATCH"]),
        "counterfactual_pair_accuracy": ratio(correct_pairs, len(complete_pairs)),
        "details": details,
        "gold_sha256": sha256_file(Path(args.gold)),
        "predictions_sha256": sha256_file(Path(args.predictions)),
    }
    write_json(args.output, metrics)
    print(json.dumps({key: metrics[key] for key in ("status", "match_precision", "match_recall", "structured_output_valid_rate")}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--manifest", required=True, type=Path)
    run.add_argument("--train", required=True, type=Path)
    run.add_argument("--dev", required=True, type=Path)
    run.add_argument("--blind-input", required=True, type=Path)
    run.add_argument("--adapter-command", required=True)
    run.add_argument("--model-id", required=True)
    run.add_argument("--model-revision", required=True)
    run.add_argument("--output", required=True, type=Path)
    run.add_argument("--run-manifest", type=Path)
    run.add_argument("--few-shot", type=Path)
    run.add_argument("--timeout-seconds", type=int, default=60)
    smoke = sub.add_parser("smoke")
    smoke.add_argument("--manifest", required=True, type=Path)
    smoke.add_argument("--adapter-command", required=True)
    smoke.add_argument("--output", type=Path)
    smoke.add_argument("--timeout-seconds", type=int, default=20)
    score = sub.add_parser("score")
    score.add_argument("--gold", required=True, type=Path)
    score.add_argument("--predictions", required=True, type=Path)
    score.add_argument("--output", required=True, type=Path)
    score.add_argument("--qa-blind", action="store_true", help="test-team isolated environment only")
    args = parser.parse_args()
    try:
        if args.command == "run":
            return formal_run(args)
        if args.command == "smoke":
            return smoke_run(args)
        return score_run(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
