#!/usr/bin/env python3
"""Contract-only regression for Baseline Protocol V0.2.1.

The cases use deterministic fixtures and the protocol stub only.  They do not
invoke a Base Model, run DEV Benchmark, or access Blind Gold.
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from harness import LOCK, ROOT, execute_one, score_run
from preflight_check import TASK, run_preflight


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def target_for(inp: dict[str, Any]) -> dict[str, Any]:
    clause = inp["clause_text"]
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
    return {
        "item_id": TASK,
        "requirement_id": inp["requirement_id"],
        "match_state": "MATCH",
        "subtype": "SUPPLIER_REGISTRATION_LOCATION",
        "evidence_text": clause,
        "evidence_spans": [span],
        "evidence_refs": [ref],
        "reasoning_factors": ["supplier_location_attribute", "pre_award_condition"],
        "missing_context_questions": [],
        "confidence": None,
        "human_review_required": False,
    }


def valid_row(role: str, sample_id: str) -> dict[str, Any]:
    clause = "投标人须在本市注册。"
    inp = {
        "requirement_id": f"REQ-{sample_id}",
        "project_id": "P-CONTRACT-FIXTURE",
        "document_id": f"DOC-{sample_id}",
        "document_version": "V1",
        "clause_id": f"CL-{sample_id}",
        "clause_text": clause,
        "business_stage": "QUALIFICATION",
        "context": None,
        "source_location": {"page": 1, "section": "fixture"},
        "parser_quality": "PASS",
        "source_defect_prevents_judgment": False,
        "source_defect_reason": None,
    }
    return {
        "schema_version": "0.2",
        "schema_sha256": json.loads((ROOT / "C1_01_Baseline_Protocol_V0.2.1.lock.json").read_text(encoding="utf-8"))["dependencies"]["dataset_schema"]["sha256"],
        "task_id": TASK,
        "sample_id": sample_id,
        "leakage_group_id": f"LG-{sample_id}",
        "annotation_state": "LABELED",
        "input": inp,
        "target": target_for(inp),
        "metadata": {
            "dataset_role": role,
            "data_eligibility": "BENCHMARK_CANDIDATE" if role == "BLIND_INPUT" else "TRAIN_ELIGIBLE",
            "review_state": "INTERNAL_REVIEWED",
            "source_kind": "PROCUREMENT_DOCUMENT",
            "source_verified_at_procurement_document_level": True,
            "evidence_status": "VERIFIED",
        },
    }


def result(name: str, expected: str, actual: str, detail: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"case": name, "expected": expected, "actual": actual, "pass": expected == actual, "detail": detail or {}}


def mutate_lock(lock_path: Path, field_path: tuple[str, str], value: str) -> dict[str, Any]:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    lock["dependencies"][field_path[0]][field_path[1]] = value
    return lock


def preflight_with_mutated_lock(field_path: tuple[str, str], value: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="c101-v021-lock-") as tmp:
        bundle = Path(tmp) / "bundle"
        shutil.copytree(ROOT, bundle)
        lock_path = bundle / LOCK.name
        write_json(lock_path, mutate_lock(lock_path, field_path, value))
        return run_preflight(lock_path, smoke=True)


def main() -> int:
    results: list[dict[str, Any]] = []
    base = run_preflight(LOCK, smoke=True)
    results.append(result("CASE 01 MetricSpec V0.2 + correct hash", "PASS", base["status"], {"errors": base["errors"]}))
    old_metric = preflight_with_mutated_lock(("metric_spec", "version"), "C1_01_Benchmark_Metric_Spec_V0.1")
    results.append(result("CASE 02 MetricSpec V0.1", "RUN_ABORTED", old_metric["status"], {"errors": old_metric["errors"]}))
    bad_metric_hash = preflight_with_mutated_lock(("metric_spec", "sha256"), "0" * 64)
    results.append(result("CASE 03 MetricSpec V0.2 + wrong hash", "RUN_ABORTED", bad_metric_hash["status"], {"errors": bad_metric_hash["errors"]}))
    results.append(result("CASE 04 DatasetSchema V0.2 + correct hash", "PASS", base["status"], {"errors": base["errors"]}))
    old_schema = preflight_with_mutated_lock(("dataset_schema", "version"), "C1_01_Dataset_Schema_V0.1")
    results.append(result("CASE 05 DatasetSchema V0.1", "RUN_ABORTED", old_schema["status"], {"errors": old_schema["errors"]}))

    with tempfile.TemporaryDirectory(prefix="c101-v021-contract-") as tmp:
        fixture = Path(tmp)
        train = fixture / "train.jsonl"
        dev = fixture / "dev.jsonl"
        blind = fixture / "blind_input.jsonl"
        write_jsonl(train, [valid_row("TRAIN", "S-C101-TRAIN-001")])
        write_jsonl(dev, [valid_row("DEV", "S-C101-DEV-001")])
        write_jsonl(blind, [valid_row("BLIND_INPUT", "S-C101-BLIND-001")])
        formal = run_preflight(LOCK, train=train, dev=dev, blind_input=blind)
        results.append(result("Formal contract fixture", "PASS", formal["status"], {"errors": formal["errors"]}))

        blocked_cases = [
            ("CASE 06 REWORK_SOURCE", {"data_eligibility": "REWORK_SOURCE"}),
            ("CASE 07 HOLD", {"data_eligibility": "HOLD"}),
            ("CASE 08 DISPUTED", {"review_state": "DISPUTED"}),
            ("CASE 09 PENDING_DATA_QA", {"data_eligibility": "PENDING_DATA_QA"}),
        ]
        for label, override in blocked_cases:
            row = valid_row("DEV", f"S-C101-{label.split()[-1].replace('_', '-')}-001")
            row["metadata"].update(override)
            blocked_dev = fixture / (label.replace(" ", "_") + ".jsonl")
            write_jsonl(blocked_dev, [row])
            blocked = run_preflight(LOCK, train=train, dev=blocked_dev, blind_input=blind)
            results.append(result(label, "RUN_ABORTED", blocked["status"], {"errors": blocked["errors"]}))

        rework = valid_row("REWORK_QUEUE", "S-C101-REWORK-001")
        rework["annotation_state"] = "UNAVAILABLE_SOURCE_REWORK"
        rework["target"] = None
        rework["metadata"].update(dataset_role="REWORK_QUEUE", data_eligibility="REWORK_SOURCE")
        rework["input"].update(parser_quality="UNCERTAIN", source_defect_prevents_judgment=True, source_defect_reason="source fixture is incomplete")
        adapter = [sys.executable, str(ROOT / "adapter_stub.py")]
        refused = execute_one(rework, adapter, 20, smoke=True)
        results.append(result("REWORK_SOURCE adapter boundary", "REFUSED_INPUT", refused["status"], {"validation_errors": refused["validation_errors"]}))
        for label, override in (
            ("HOLD adapter boundary", {"data_eligibility": "HOLD"}),
            ("DISPUTED adapter boundary", {"review_state": "DISPUTED"}),
            ("PENDING_DATA_QA adapter boundary", {"data_eligibility": "PENDING_DATA_QA"}),
        ):
            blocked_row = valid_row("DEV", f"S-C101-{label.split()[0]}-ADAPTER-001")
            blocked_row["metadata"].update(override)
            blocked_result = execute_one(blocked_row, adapter, 20, smoke=True)
            results.append(result(label, "REFUSED_INPUT", blocked_result["status"], {"validation_errors": blocked_result["validation_errors"]}))

        invalid_gold = valid_row("DEV", "S-C101-INVALID-001")
        gold_path = fixture / "invalid_gold.jsonl"
        pred_path = fixture / "invalid_predictions.jsonl"
        metrics_path = fixture / "invalid_metrics.json"
        write_jsonl(gold_path, [invalid_gold])
        write_jsonl(pred_path, [{
            "sample_id": invalid_gold["sample_id"],
            "requirement_id": invalid_gold["input"]["requirement_id"],
            "status": "INVALID",
            "raw_output": "{invalid-json",
            "prediction": None,
            "validation_errors": ["INVALID_JSON"],
            "latency_ms": 0.0,
        }])
        rc = score_run(SimpleNamespace(gold=gold_path, predictions=pred_path, output=metrics_path, qa_blind=False))
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        semantic_pass = (
            rc == 0
            and metrics["counts"]["invalid"] == 1
            and metrics["structured_output_valid_rate"] == 0.0
            and metrics["match_recall"] == 0.0
        )
        results.append(result("Prediction INVALID retention/denominator semantics", "PASS", "PASS" if semantic_pass else "FAIL", {
            "sample_id_preserved": pred_path.read_text(encoding="utf-8").find(invalid_gold["sample_id"]) >= 0,
            "counts": metrics["counts"],
            "structured_output_valid_rate": metrics["structured_output_valid_rate"],
            "match_recall": metrics["match_recall"],
        }))

    report = {
        "protocol": "C1_01_Baseline_Protocol_V0.2.1",
        "status": "PASS" if all(case["pass"] for case in results) else "FAIL",
        "scope": "CONTRACT_FIXTURE_ONLY",
        "model_run": False,
        "dev_benchmark": False,
        "blind_test": False,
        "results": results,
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output:
        write_json(args.output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
