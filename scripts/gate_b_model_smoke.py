#!/usr/bin/env python3
"""Run a local-only, synthetic Gate-B model readiness smoke."""
from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/harness/C1_01_Baseline_Harness_V0.2.1"
LOCK = BASE / "C1_01_Baseline_Protocol_V0.2.1.lock.json"
HARNESS = BASE / "harness.py"
ADAPTER = BASE / "adapter_stub.py"
ARTIFACT = ROOT / "configs/gate_b/C1_01_Gate_B_Model_Artifact_Manifest_V0.1.json"
RUNTIME = ROOT / "configs/gate_b/C1_01_Gate_B_Runtime_Dependency_Lock_V0.1.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def synthetic_request(requirement_id: str, clause_text: str, section: str = "TECHNICAL") -> dict[str, Any]:
    return {
        "task_id": "C1-01_LOCAL_ENTRY_PRECONDITION",
        "input": {
            "document_id": "DOC-SYNTHETIC-001",
            "document_version": "v0",
            "requirement_id": requirement_id,
            "clause_text": clause_text,
            "source_location": {"page": 1, "section": section},
            "context": [],
        },
    }


def run_adapter(request: dict[str, Any], validate_prediction) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(ADAPTER)],
        input=json.dumps(request, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return {"status": "INVALID", "errors": [completed.stderr.strip() or "adapter_failed"]}
    try:
        prediction = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return {"status": "INVALID", "errors": [f"invalid_json:{exc.msg}"]}
    errors = validate_prediction(prediction, request["input"])
    return {"status": "VALID" if not errors else "INVALID", "errors": errors, "prediction": prediction}


def environment_probe(expected: dict[str, Any]) -> dict[str, Any]:
    observed = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": {},
    }
    for package in expected.get("installed", {}):
        try:
            observed["packages"][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            observed["packages"][package] = None
    return observed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
    preflight = load_module(BASE / "preflight_check.py", "c101_gate_b_preflight")
    validator = preflight.validate_prediction
    cases = [
        ("MATCH", synthetic_request("REQ-MATCH", "投标人须在本市注册。")),
        ("NEEDS_CONTEXT", synthetic_request("REQ-CONTEXT", "供应商应具备本地化服务能力。")),
        ("NO_MATCH", synthetic_request("REQ-NO", "中标后建立满足两小时响应的服务机制。", "CONTRACT")),
    ]
    synthetic_results = []
    for expected_state, request in cases:
        result = run_adapter(request, validator)
        actual = (result.get("prediction") or {}).get("match_state")
        synthetic_results.append({
            "expected": expected_state,
            "actual": actual,
            "status": result["status"],
            "pass": result["status"] == "VALID" and actual == expected_state,
            "errors": result["errors"],
        })

    preflight_result = preflight.run_preflight(LOCK, smoke=True)
    command = [sys.executable, str(HARNESS), "smoke", "--manifest", str(LOCK), "--adapter-command", f"{sys.executable} {ADAPTER}"]
    harness_run = subprocess.run(command, text=True, capture_output=True, check=False)
    try:
        harness_result = json.loads(harness_run.stdout)
    except json.JSONDecodeError:
        harness_result = {"status": "INVALID_REPORT", "stdout": harness_run.stdout[-1000:]}

    synthetic_pass = all(item["pass"] for item in synthetic_results)
    harness_pass = harness_run.returncode == 0 and harness_result.get("status") == "PASS"
    readiness_status = artifact["status"]
    report = {
        "report_version": "C1_01_GATE_B_MODEL_SMOKE_V0.1",
        "status": "SMOKE_PASS_READINESS_BLOCKED" if synthetic_pass and harness_pass and preflight_result["status"] == "PASS" else "SMOKE_FAIL",
        "readiness_status": readiness_status,
        "external_calls": {"model_download": False, "dependency_install": False, "teacher_api": False},
        "environment": environment_probe(runtime),
        "preflight": {"status": preflight_result["status"], "checks": preflight_result.get("checks", {})},
        "synthetic_adapter": synthetic_results,
        "official_harness_smoke": harness_result,
        "formal_runs": {"benchmark": False, "fine_tune": False, "blind_test": False},
    }
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if report["status"] == "SMOKE_PASS_READINESS_BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
