#!/usr/bin/env python3
"""Assemble C1-01 Gate-B DEV/Blind inputs without exporting Blind Gold."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK = "C1-01_LOCAL_ENTRY_PRECONDITION"
BASE = ROOT / "contracts/task/c1_01_local_entry_precondition"
SCHEMA = BASE / "03_dataset_schema/C1_01_Dataset_Schema_V0.2.json"
PROTOCOL = BASE / "04_baseline_protocol/protocol/C1_01_Baseline_Protocol_V0.2.1.md"
METRIC = BASE / "05_benchmark_metric_spec/C1_01_Benchmark_Metric_Spec_V0.2.md"
LOCK = BASE / "04_baseline_protocol/protocol/C1_01_Baseline_Protocol_V0.2.1.lock.json"
VALIDATOR = BASE / "03_dataset_schema/validate_sample.py"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: row must be an object")
            rows.append(value)
    return rows


def load_schema_report(records: list[dict[str, Any]]) -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location("c101_schema_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load schema validator: {VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_records(records, SCHEMA)


def eligibility_reasons(row: dict[str, Any], split: str) -> list[str]:
    inp = row.get("input", {})
    meta = row.get("metadata", {})
    target = row.get("target")
    reasons: list[str] = []
    expected_eligibility = "TRAIN_ELIGIBLE" if split == "DEV" else "BENCHMARK_CANDIDATE"
    allowed_roles = {"DEV"} if split == "DEV" else {"BLIND_INPUT", "BLIND_GOLD"}
    if row.get("annotation_state") != "LABELED":
        reasons.append("annotation_state_not_LABELED")
    if target is None:
        reasons.append("target_null")
    if inp.get("parser_quality") != "PASS" or inp.get("source_defect_prevents_judgment") is not False:
        reasons.append("source_parse_not_reliable")
    if meta.get("data_eligibility") != expected_eligibility:
        reasons.append(f"data_eligibility_not_{expected_eligibility}")
    if meta.get("dataset_role") not in allowed_roles:
        reasons.append("dataset_role_not_allowed")
    if meta.get("review_state") != "INTERNAL_REVIEWED":
        reasons.append("review_state_not_INTERNAL_REVIEWED")
    if meta.get("source_kind") != "PROCUREMENT_DOCUMENT":
        reasons.append("source_kind_not_PROCUREMENT_DOCUMENT")
    if meta.get("source_verified_at_procurement_document_level") is not True:
        reasons.append("source_not_verified")
    if meta.get("evidence_status") != "VERIFIED":
        reasons.append("evidence_not_VERIFIED")
    if meta.get("review_state") == "DISPUTED":
        reasons.append("review_state_DISPUTED")
    return reasons


def public_input(row: dict[str, Any]) -> dict[str, Any]:
    """Return the model-visible projection; target and metadata never leave assembly."""
    return {
        "sample_id": row["sample_id"],
        "task_id": row["task_id"],
        "input": row["input"],
    }


def coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    states = Counter((row.get("target") or {}).get("match_state") for row in rows)
    subtypes = Counter((row.get("target") or {}).get("subtype") for row in rows if (row.get("target") or {}).get("match_state") == "MATCH")
    slices = Counter(row.get("metadata", {}).get("case_slice") for row in rows)
    pairs = Counter(row.get("metadata", {}).get("pair_id") for row in rows if row.get("metadata", {}).get("pair_id"))
    hard_negative = sum(
        row.get("metadata", {}).get("case_slice") in {
            "HARD_NEGATIVE", "OFFICIAL_ANCHOR_HARD_NEGATIVE", "COUNTERFACTUAL_HARD_NEGATIVE"
        }
        for row in rows
    )
    return {
        "match_states": dict(states),
        "match_subtypes": dict(subtypes),
        "case_slices": dict(slices),
        "counterfactual_pair_count": len(pairs),
        "hard_negative_count": hard_negative,
    }


def split_integrity(rows_by_split: dict[str, list[dict[str, Any]]]) -> list[str]:
    errors: list[str] = []
    group_roles: dict[str, set[str]] = defaultdict(set)
    pair_roles: dict[str, set[str]] = defaultdict(set)
    pair_counts: Counter[str] = Counter()
    for split, rows in rows_by_split.items():
        for row in rows:
            group_roles[row.get("leakage_group_id")].add(split)
            pair_id = row.get("metadata", {}).get("pair_id")
            if pair_id:
                pair_roles[pair_id].add(split)
                pair_counts[pair_id] += 1
    for group, roles in group_roles.items():
        if len(roles) > 1:
            errors.append(f"leakage_group_crosses_split:{group}")
    for pair_id, roles in pair_roles.items():
        if len(roles) > 1:
            errors.append(f"counterfactual_pair_crosses_split:{pair_id}")
        if pair_counts[pair_id] != 2:
            errors.append(f"counterfactual_pair_not_two_records:{pair_id}")
    return errors


def assemble(candidate_path: Path, output_dir: Path, snapshot_id: str, owner: str) -> dict[str, Any]:
    records = read_jsonl(candidate_path)
    schema_report = load_schema_report(records)
    rows_by_split = {
        "DEV": [row for row in records if not eligibility_reasons(row, "DEV")],
        "BLIND": [row for row in records if not eligibility_reasons(row, "BLIND")],
    }
    blocked_by_reason: Counter[str] = Counter()
    for row in records:
        reasons = eligibility_reasons(row, "BLIND")
        if not reasons:
            continue
        for reason in reasons:
            blocked_by_reason[reason] += 1
    integrity_errors = split_integrity(rows_by_split)
    blind_rows = rows_by_split["BLIND"]
    blind_coverage = coverage(blind_rows)
    required_subtypes = {
        "SUPPLIER_REGISTRATION_LOCATION", "DISTANCE_TO_PURCHASER",
        "PREEXISTING_LOCAL_BRANCH", "OTHER_RELATED",
    }
    missing_coverage: list[str] = []
    if len(blind_rows) < 50:
        missing_coverage.append(f"blind_test_n_lt_50:{len(blind_rows)}")
    if not {"MATCH", "NO_MATCH", "NEEDS_CONTEXT"}.issubset(blind_coverage["match_states"]):
        missing_coverage.append("match_state_coverage_incomplete")
    missing_subtypes = required_subtypes - set(blind_coverage["match_subtypes"])
    if missing_subtypes:
        missing_coverage.append("subtype_coverage_missing:" + ",".join(sorted(missing_subtypes)))
    if blind_coverage["hard_negative_count"] == 0:
        missing_coverage.append("hard_negative_coverage_missing")
    if blind_coverage["counterfactual_pair_count"] == 0:
        missing_coverage.append("counterfactual_pair_coverage_missing")
    readiness_gaps = missing_coverage + integrity_errors
    if not rows_by_split["DEV"]:
        readiness_gaps.append("dev_snapshot_has_no_eligible_record")
    if not blind_rows:
        readiness_gaps.append("blind_snapshot_has_no_eligible_record")
    benchmark_ready = not readiness_gaps and schema_report["record_count"] > 0

    output_dir.mkdir(parents=True, exist_ok=True)
    dev_path = output_dir / "dev_input.jsonl"
    blind_path = output_dir / "blind_test_input.jsonl"
    dev_path.write_text("".join(json.dumps(public_input(row), ensure_ascii=False, sort_keys=True) + "\n" for row in rows_by_split["DEV"]), encoding="utf-8")
    blind_path.write_text("".join(json.dumps(public_input(row), ensure_ascii=False, sort_keys=True) + "\n" for row in blind_rows), encoding="utf-8")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    manifest = {
        "snapshot_id": snapshot_id,
        "task_id": TASK,
        "status": "FROZEN" if benchmark_ready else "BLOCKED_READINESS_GAP",
        "benchmark_ready": benchmark_ready,
        "owner": owner,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "schema": {"version": "C1_01_Dataset_Schema_V0.2", "sha256": sha256_file(SCHEMA)},
        "protocol": {"version": "C1_01_Baseline_Protocol_V0.2.1", "sha256": sha256_file(PROTOCOL), "lock_sha256": sha256_file(LOCK)},
        "metric_spec": {"version": "C1_01_Benchmark_Metric_Spec_V0.2", "sha256": sha256_file(METRIC)},
        "source_candidate_sha256": sha256_file(candidate_path),
        "source_record_count": len(records),
        "dev_snapshot": {"sample_count": len(rows_by_split["DEV"]), "input_file": dev_path.name, "input_sha256": sha256_file(dev_path)},
        "blind_snapshot": {
            "sample_count": len(blind_rows),
            "input_file": blind_path.name,
            "input_sha256": sha256_file(blind_path),
            "gold_file": None,
            "gold_sha256": None,
        },
        "split_counts": {"DEV": len(rows_by_split["DEV"]), "BLIND_INPUT": len(blind_rows)},
        "coverage": blind_coverage,
        "leakage_check_result": "PASS" if not integrity_errors else "FAIL",
        "counterfactual_check_result": "PASS" if not any("counterfactual" in item for item in integrity_errors) else "FAIL",
        "gold_exported": False,
        "blocked_record_reasons": dict(blocked_by_reason),
        "readiness_gaps": readiness_gaps,
        "dependencies": {
            "metric_spec_lock_version": lock["dependencies"]["metric_spec"]["version"],
            "metric_spec_lock_sha256": lock["dependencies"]["metric_spec"]["sha256"],
        },
        "schema_validation": {
            "record_count": schema_report["record_count"],
            "schema_valid_count": schema_report["schema_valid_count"],
            "cross_field_valid_count": schema_report["cross_field_valid_count"],
            "integrity_errors": schema_report["integrity_errors"],
        },
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--snapshot-id", default="C1_01_BenchmarkSnapshot_GateB_Readiness_V0.1")
    parser.add_argument("--owner", default="04-测试与评测组")
    args = parser.parse_args()
    report = assemble(args.candidate_input, args.output_dir, args.snapshot_id, args.owner)
    print(json.dumps({"snapshot_id": report["snapshot_id"], "status": report["status"], "benchmark_ready": report["benchmark_ready"], "dev_count": report["dev_snapshot"]["sample_count"], "blind_count": report["blind_snapshot"]["sample_count"], "readiness_gaps": report["readiness_gaps"]}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "FROZEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
