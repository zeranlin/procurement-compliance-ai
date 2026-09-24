#!/usr/bin/env python3
"""Run the C1-01 QA-only evaluator readiness check.

This creates synthetic canary evidence only.  It never reads a formal Blind
Gold file, model weights, adapters, or external model services.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gate_b_regression import target_for
from isolated_evaluator import evaluate, evaluate_files
from runtime_acl import ALLOWED, SERVICE_ACCOUNTS, probe_matrix


ROOT = Path(__file__).resolve().parents[2]
TASK = "C1-01_LOCAL_ENTRY_PRECONDITION"
BASE = ROOT / "contracts/task/c1_01_local_entry_precondition"
SCHEMA = BASE / "03_dataset_schema/C1_01_Dataset_Schema_V0.2.json"
PROTOCOL = BASE / "04_baseline_protocol/protocol/C1_01_Baseline_Protocol_V0.2.1.md"
PROTOCOL_LOCK = BASE / "04_baseline_protocol/protocol/C1_01_Baseline_Protocol_V0.2.1.lock.json"
METRIC = BASE / "05_benchmark_metric_spec/C1_01_Benchmark_Metric_Spec_V0.2.md"
BLIND_RULES = BASE / "06_blind_test/C1_01_Blind_Test_Management_Rules_V0.1.md"
GOLD_BOUNDARY = BASE / "06_blind_test/C1_01_Blind_Test_Gold_Access_Boundary_V0.1.md"
TEMPLATE = BASE / "04_baseline_protocol/protocol/C1_01_Baseline_Run_Manifest_Template_V0.2.1.json"
SCHEMA_VALIDATOR = BASE / "03_dataset_schema/validate_sample.py"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_dump(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_schema_validator():
    spec = importlib.util.spec_from_file_location("c101_schema_validator", SCHEMA_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load schema validator: {SCHEMA_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_records


def canary_input(index: int, text: str, stage: str) -> dict[str, Any]:
    return {
        "requirement_id": f"REQ-CANARY-{index:03d}",
        "project_id": f"P-CANARY-{index:03d}",
        "document_id": f"DOC-CANARY-{index:03d}",
        "document_version": "SYNTHETIC-V0.2",
        "clause_id": f"CL-CANARY-{index:03d}",
        "clause_text": text,
        "business_stage": stage,
        "context": None,
        "source_location": {"page": 1, "section": "synthetic_canary"},
        "parser_quality": "PASS",
        "source_defect_prevents_judgment": False,
        "source_defect_reason": None,
    }


def make_canary() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return full V0.2 synthetic records and the temporary evaluator Gold."""
    rows: list[dict[str, Any]] = []
    gold: list[dict[str, Any]] = []
    schema_hash = sha256_file(SCHEMA)
    index = 0
    for cycle in range(1, 9):
        cases = [
            ("MATCH", "SUPPLIER_REGISTRATION_LOCATION", "投标人须为本市注册企业。", "QUALIFICATION", "TYPICAL_POSITIVE", None),
            ("MATCH", "DISTANCE_TO_PURCHASER", "投标人距采购人不得超过50公里。", "QUALIFICATION", "TYPICAL_POSITIVE", None),
            ("MATCH", "PREEXISTING_LOCAL_BRANCH", "投标人须在本市已有分支机构。", "QUALIFICATION", "TYPICAL_POSITIVE", None),
            ("MATCH", "OTHER_RELATED", "投标人须具备本地化服务能力并提交当地服务承诺。", "QUALIFICATION", "HARD_POSITIVE", None),
            ("NO_MATCH", "NONE", "采购人地址位于本市。", "QUALIFICATION", "HARD_NEGATIVE", None),
            ("NEEDS_CONTEXT", "NONE", "本地服务要求按资格条件第七项执行。", "QUALIFICATION", "MISSING_CONTEXT", None),
            ("MATCH", "SUPPLIER_REGISTRATION_LOCATION", "投标人须在本市注册。", "QUALIFICATION", "COUNTERFACTUAL_POSITIVE", f"PAIR-CANARY-{cycle:03d}"),
            ("NO_MATCH", "NONE", "投标人可在任意地区投标，中标后按需提供服务。", "CONTRACT", "COUNTERFACTUAL_HARD_NEGATIVE", f"PAIR-CANARY-{cycle:03d}"),
        ]
        for state, subtype, text, stage, case_slice, pair_id in cases:
            index += 1
            sample_id = f"S-C101-CANARY-{index:03d}"
            inp = canary_input(index, text, stage)
            leakage_group_id = pair_id or f"LG-CANARY-{index:03d}"
            row = {
                "schema_version": "0.2",
                "schema_sha256": schema_hash,
                "task_id": TASK,
                "sample_id": sample_id,
                "leakage_group_id": leakage_group_id,
                "annotation_state": "LABELED",
                "input": inp,
                "target": target_for({"input": inp}, state, subtype),
                "metadata": {
                    "case_id": f"CASE-CANARY-{index:03d}",
                    "seed_id": None,
                    "source_record_sha256": hashlib.sha256(sample_id.encode()).hexdigest(),
                    "source_kind": "SYNTHETIC",
                    "source_url": None,
                    "source_title": "C1-01 synthetic evaluator canary",
                    "source_sha256": None,
                    "is_verbatim_procurement_clause": False,
                    "source_verified_at_procurement_document_level": False,
                    "evidence_status": "UNVERIFIED",
                    "case_slice": case_slice,
                    "pair_id": pair_id,
                    "counterfactual_change": "synthetic counterfactual pair" if pair_id else None,
                    "parent_sample_id": None,
                    "review_state": "INTERNAL_REVIEWED",
                    "label_authority": "INTERNAL_SILVER",
                    "data_eligibility": "HOLD",
                    "dataset_role": "REGRESSION",
                    "source_rework_reason": None,
                    "guide_version": "C1_01_Label_Guide_V0.1",
                    "spec_version": "BR_C1_01_Business_Task_Spec_V0.1",
                },
            }
            rows.append(row)
            gold.append({
                "sample_id": sample_id,
                "input": inp,
                "target": row["target"],
                "metadata": {"case_slice": case_slice, "pair_id": pair_id},
            })
    return rows, gold


def predictions_for(gold: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "sample_id": row["sample_id"],
            "requirement_id": row["input"]["requirement_id"],
            "status": "VALID",
            "raw_output": json.dumps(row["target"], ensure_ascii=False),
            "prediction": copy.deepcopy(row["target"]),
            "validation_errors": [],
        }
        for row in gold
    ]


def contract_hashes() -> dict[str, Any]:
    paths = {
        "BusinessTaskSpec": BASE / "01_business_task_spec/BR_C1_01_Business_Task_Spec_V0.1.md",
        "LabelGuide": BASE / "01_business_task_spec/C1_01_Label_Guide_V0.1.md",
        "DatasetSchema": SCHEMA,
        "BaselineProtocol": PROTOCOL,
        "BaselineProtocolLock": PROTOCOL_LOCK,
        "BenchmarkMetricSpec": METRIC,
        "BlindTestManagement": BLIND_RULES,
        "BlindGoldAccessBoundary": GOLD_BOUNDARY,
        "RunManifestTemplate": TEMPLATE,
    }
    result: dict[str, Any] = {}
    for name, path in paths.items():
        if not path.is_file():
            result[name] = {"path": str(path), "status": "MISSING"}
            continue
        result[name] = {"path": str(path), "sha256": sha256_file(path), "status": "PASS"}
    return result


def command_output(command: list[str]) -> dict[str, Any]:
    try:
        proc = subprocess.run(command, capture_output=True, text=True, check=False, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": command, "status": "UNAVAILABLE", "error": str(exc)}
    return {
        "command": command,
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def environment_lock(output_dir: Path) -> dict[str, Any]:
    lock: dict[str, Any] = {
        "captured_at": now(),
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "platform": platform.platform(),
        "pip_freeze": command_output([sys.executable, "-m", "pip", "freeze"]),
        "evaluator_mode": "QA_ONLY_SYNTHETIC_NO_MODEL",
        "trust_remote_code": False,
        "local_files_only": True,
        "model_loaded": False,
        "adapter_loaded": False,
        "deepseek_called": False,
        "gpu_probe": command_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"]),
    }
    model_dir = Path("/data1/LLM_group/models/Qwen3.5-4B")
    model_files: list[dict[str, Any]] = []
    if model_dir.is_dir():
        for path in sorted(item for item in model_dir.rglob("*") if item.is_file()):
            model_files.append({"path": str(path), "sha256": sha256_file(path), "size": path.stat().st_size})
    lock["model"] = {"path": str(model_dir), "exists": model_dir.is_dir(), "file_count": len(model_files), "files": model_files}
    json_dump(output_dir / "environment_lock.json", lock)
    return lock


def write_policy_artifacts(output_dir: Path) -> dict[str, Any]:
    acl_report = probe_matrix(output_dir / "acl_probe_workspace", output_dir / "acl_matrix.json")
    audit_policy = {
        "policy_version": "C1_01_QA_Audit_Policy_V0.2",
        "gold_plaintext_policy": "never export; audit only metadata and result",
        "required_fields": ["timestamp", "subject_id", "role", "action", "asset", "result", "reason", "export_bytes"],
        "gold_access": {"QA": "read only blind_test_gold", "all_other_roles": "DENY"},
        "input_access": {"ALGORITHM": "read blind_test_input"},
        "aggregate_access": ["ALGORITHM", "BUSINESS", "DATA", "PM", "OPS", "QA"],
        "production_binding_status": "SHARED_ACCOUNT_ACL_BLOCKER",
        "note": "runtime_acl.py is a policy harness; production IAM binding requires deployment authority.",
    }
    json_dump(output_dir / "audit_policy.json", audit_policy)
    return {"acl": acl_report, "audit_policy": audit_policy}


def run_fault_injections(gold: list[dict[str, Any]], predictions: list[dict[str, Any]]) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    duplicate = predictions + [copy.deepcopy(predictions[0])]
    checks["duplicate_id"] = evaluate(gold, duplicate, "C1_01_SYNTHETIC_CANARY")
    missing = predictions[:-1]
    checks["missing_id"] = evaluate(gold, missing, "C1_01_SYNTHETIC_CANARY")
    unknown = copy.deepcopy(predictions)
    unknown[0]["sample_id"] = "S-C101-CANARY-UNKNOWN"
    checks["unknown_id"] = evaluate(gold, unknown, "C1_01_SYNTHETIC_CANARY")
    invalid_json = copy.deepcopy(predictions)
    invalid_json[0]["status"] = "INVALID"
    invalid_json[0]["prediction"] = None
    invalid_json[0]["raw_output"] = "{invalid-json"
    invalid_json[0]["validation_errors"] = ["INVALID_JSON"]
    invalid_result = evaluate(gold, invalid_json, "C1_01_SYNTHETIC_CANARY")
    checks["invalid_json_retained_in_denominator"] = invalid_result
    invalid_evidence = copy.deepcopy(predictions)
    invalid_evidence[0]["prediction"]["evidence_spans"][0]["text"] = "tampered evidence"
    checks["invalid_evidence"] = evaluate(gold, invalid_evidence, "C1_01_SYNTHETIC_CANARY")
    return {
        "duplicate_id": checks["duplicate_id"]["gate_decision"] == "INVALID_SUBMISSION",
        "missing_id": checks["missing_id"]["gate_decision"] == "INVALID_SUBMISSION",
        "unknown_id": checks["unknown_id"]["gate_decision"] == "INVALID_SUBMISSION",
        "invalid_json_retained": checks["invalid_json_retained_in_denominator"]["metrics"]["invalid_prediction_count"] == 1,
        "invalid_evidence_retained": checks["invalid_evidence"]["metrics"]["invalid_prediction_count"] == 1,
        "details": checks,
    }


def leakage_alignment(records: list[dict[str, Any]], gold: list[dict[str, Any]], predictions: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in records:
        groups.setdefault(row["leakage_group_id"], []).append(row)
    pair_ids = [row["metadata"]["pair_id"] for row in records if row["metadata"]["pair_id"]]
    pair_counts = {pair_id: pair_ids.count(pair_id) for pair_id in sorted(set(pair_ids))}
    alignment = evaluate(gold, predictions, "C1_01_SYNTHETIC_CANARY")["alignment"]
    invalid_shared_groups = [
        group_id
        for group_id, rows in groups.items()
        if len(rows) > 1 and not (len(rows) == 2 and rows[0]["metadata"]["pair_id"] and rows[0]["metadata"]["pair_id"] == rows[1]["metadata"]["pair_id"])
    ]
    return {
        "schema_records": len(records),
        "unique_leakage_groups": len(groups),
        "duplicate_leakage_group_count": sum(len(rows) - 1 for rows in groups.values() if len(rows) > 1),
        "invalid_shared_leakage_groups": invalid_shared_groups,
        "counterfactual_pair_counts": pair_counts,
        "pair_integrity": all(count == 2 for count in pair_counts.values()),
        "prediction_alignment": alignment,
        "status": "PASS" if not invalid_shared_groups and all(count == 2 for count in pair_counts.values()) and alignment["exact_id_alignment"] else "FAIL",
    }


def write_intake_contract(output_dir: Path) -> None:
    (output_dir / "Blind_Gold_Intake_Contract_V0.2.md").write_text(
        "# C1-01 Blind Gold Intake Contract V0.2\n\n"
        "状态：仅定义接收边界，不表示已生成或接收正式 Gold。\n\n"
        "- `blind_test_input.jsonl`：Algorithm 可见；只含模型输入投影。\n"
        "- `blind_test_gold.jsonl`：仅 QA 隔离评测服务可读；不得进入 Algorithm、Business、Data、PM、Ops 工作区。\n"
        "- Gold 接收必须记录 snapshot_id、schema/protocol/metric 哈希、文件 SHA-256、接收时间和 QA owner。\n"
        "- 接收后只输出 aggregate report、审计元数据和失败计数；禁止导出 Gold 明文。\n"
        "- 本轮使用的 64 条数据是合成 Canary，不是正式 Blind Gold，Gold 仅在临时目录短暂用于 QA 回归。\n"
        "- 生产多账号 ACL 尚未绑定时，状态保留 `SHARED_ACCOUNT_ACL_BLOCKER`。\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.run_root.mkdir(parents=True, exist_ok=True)

    hashes = contract_hashes()
    json_dump(args.output_dir / "contract_hashes.json", hashes)
    missing_contracts = [name for name, item in hashes.items() if item.get("status") != "PASS"]
    records, gold = make_canary()
    predictions = predictions_for(gold)
    schema_validation = load_schema_validator()(records, SCHEMA)
    json_dump(args.output_dir / "synthetic_schema_validation.json", {
        "schema_version": schema_validation["schema_version"],
        "schema_sha256": schema_validation["schema_sha256"],
        "record_count": schema_validation["record_count"],
        "schema_valid_count": schema_validation["schema_valid_count"],
        "cross_field_valid_count": schema_validation["cross_field_valid_count"],
        "integrity_errors": schema_validation["integrity_errors"],
        "status": "PASS" if schema_validation["schema_valid_count"] == len(records) and schema_validation["cross_field_valid_count"] == len(records) and not schema_validation["integrity_errors"] else "FAIL",
    })

    input_path = args.output_dir / "synthetic_eval_canary_input.jsonl"
    input_path.write_text("".join(json.dumps({"sample_id": row["sample_id"], "task_id": TASK, "input": row["input"]}, ensure_ascii=False, sort_keys=True) + "\n" for row in records), encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="c101-independent-evaluator-", dir=args.run_root) as temp_dir:
        temp = Path(temp_dir)
        gold_path = temp / "synthetic_canary_gold.jsonl"
        prediction_path = temp / "synthetic_canary_predictions.jsonl"
        gold_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in gold), encoding="utf-8")
        prediction_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in predictions), encoding="utf-8")
        evaluation = evaluate_files(gold_path, prediction_path, temp / "evaluation.json", temp / "access_audit.jsonl", "C1_01_SYNTHETIC_EVAL_CANARY_V0.2")
        fault = run_fault_injections(gold, predictions)
        alignment = leakage_alignment(records, gold, predictions)
        actual_metrics = dict(evaluation["metrics"])
        actual_metrics["needs_context_recall"] = actual_metrics.get("needs_context_accuracy")
        json_dump(args.output_dir / "metrics_expected_vs_actual.json", {
            "expected": {
                "sample_count": 64,
                "structured_output_valid_rate": 1.0,
                "match_recall": 1.0,
                "match_precision": 1.0,
                "match_f1": 1.0,
                "hard_negative_fpr": 0.0,
                "needs_context_recall": 1.0,
                "match_subtype_accuracy": 1.0,
                "evidence_hit_rate": 1.0,
                "counterfactual_pair_accuracy": 1.0,
            },
            "actual": actual_metrics,
            "evaluator_status": evaluation["status"],
            "gate_decision": evaluation["gate_decision"],
            "synthetic_canary_gate_status": "PASS" if all(value is True for key, value in evaluation["gate_results"].items() if key != "match_f1_vs_same_snapshot_base_model") else "FAIL",
            "match_f1_vs_same_snapshot_base_model": "N/A_SYNTHETIC_CANARY",
        })
        json_dump(args.output_dir / "fault_injection_results.json", fault)
        json_dump(args.output_dir / "leakage_alignment.json", alignment)

    policy = write_policy_artifacts(args.output_dir)
    environment = environment_lock(args.output_dir)
    write_intake_contract(args.output_dir)
    applicable_gate_results = {
        key: value
        for key, value in evaluation["gate_results"].items()
        if key != "match_f1_vs_same_snapshot_base_model"
    }
    canary_pass = all(value is True for value in applicable_gate_results.values())
    fault_pass = all(value is True for key, value in fault.items() if key != "details")
    schema_pass = schema_validation["schema_valid_count"] == len(records) and schema_validation["cross_field_valid_count"] == len(records) and not schema_validation["integrity_errors"]
    acl_pass = policy["acl"]["status"] == "PASS"
    status = "EVALUATOR_READY_AWAITING_BLIND_GOLD" if canary_pass and fault_pass and schema_pass and acl_pass and not missing_contracts else "BLOCKED"
    readiness = {
        "status": status,
        "generated_at": now(),
        "server_execution": True,
        "formal_blind_gold_read": False,
        "formal_benchmark_ready": False,
        "training_authorized": False,
        "canary": {"count": len(records), "name": "SYNTHETIC_EVAL_CANARY", "schema_validation": "PASS" if schema_pass else "FAIL"},
        "tests": {"positive_evaluation": canary_pass, "fault_injection": fault_pass, "leakage_alignment": alignment["status"] == "PASS", "acl_policy_harness": acl_pass},
        "acl_status": "SHARED_ACCOUNT_ACL_BLOCKER",
        "contract_hash_status": "BLOCKED" if missing_contracts else "PASS",
        "missing_contracts": missing_contracts,
        "required_next_step": "QA-only intake of formal Blind Gold after Data supplies a qualified snapshot; production ACL binding remains separate.",
    }
    json_dump(args.output_dir / "readiness_report.json", readiness)
    report_lines = [
        "# C1-01 Independent Evaluator Readiness Report V0.2",
        "",
        f"- Status: `{status}`",
        "- Mode: `QA_ONLY_SYNTHETIC_NO_MODEL`",
        "- Formal Blind Gold read: `false`",
        "- Formal Benchmark Ready: `false`",
        "- Training authorized: `false`",
        "",
        "## Execution Evidence",
        "",
        f"- `SYNTHETIC_EVAL_CANARY`: {len(records)} 条",
        f"- Schema V0.2 validation: `{readiness['canary']['schema_validation']}`",
        f"- Positive evaluator: `{'PASS' if canary_pass else 'FAIL'}`",
        f"- Fault injection: `{'PASS' if fault_pass else 'FAIL'}`",
        f"- Leakage/alignment: `{alignment['status']}`",
        f"- ACL policy harness: `{'PASS' if acl_pass else 'FAIL'}`",
        "",
        "## Boundary",
        "",
        "本次仅使用合成 Canary。临时 Gold 未写入报告目录、未进入 Git、未导出明文；不能据此宣称 Benchmark Ready、Gate-B PASS 或 training authorized。",
        "",
        "生产 ACL 状态：`SHARED_ACCOUNT_ACL_BLOCKER`。当前证据是策略矩阵和拒绝探针，不等同于真实多账号 IAM 已部署。",
        "",
        "## Reproducibility",
        "",
        "所有报告文件的 SHA-256 见 `output_manifest.json`；`output_manifest.sha256` 用于复核 Manifest 本身。",
    ]
    (args.output_dir / "readiness_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest: dict[str, Any] = {
        "manifest_version": "C1_01_Independent_Evaluator_Output_Manifest_V0.2",
        "generated_at": now(),
        "status": status,
        "canary_count": len(records),
        "formal_gold_exported": False,
        "files": {},
        "manifest_sha256_file": "output_manifest.sha256",
    }
    for path in sorted(args.output_dir.iterdir()):
        if path.name in {"output_manifest.json", "output_manifest.sha256"} or not path.is_file():
            continue
        manifest["files"][path.name] = {"size": path.stat().st_size, "sha256": sha256_file(path)}
    json_dump(args.output_dir / "output_manifest.json", manifest)
    (args.output_dir / "output_manifest.sha256").write_text(sha256_file(args.output_dir / "output_manifest.json") + "  output_manifest.json\n", encoding="utf-8")
    print(json.dumps({"status": status, "canary_count": len(records), "output_dir": str(args.output_dir), "manifest": str(args.output_dir / "output_manifest.json")}, ensure_ascii=False, indent=2))
    return 0 if status == "EVALUATOR_READY_AWAITING_BLIND_GOLD" else 2


if __name__ == "__main__":
    raise SystemExit(main())
