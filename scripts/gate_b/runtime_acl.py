#!/usr/bin/env python3
"""Deterministic runtime ACL boundary used by Gate-B regression probes.

This is a policy harness, not a replacement for production IAM. Production
deployment must bind the same role/action matrix to real service accounts and
filesystem/object-store policy.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SERVICE_ACCOUNTS = {
    "ALGORITHM": "svc-c101-algorithm",
    "BUSINESS": "svc-c101-business",
    "DATA": "svc-c101-data",
    "PM": "svc-c101-pm",
    "OPS": "svc-c101-ops",
    "QA": "svc-c101-qa-isolated-evaluator",
}

ALLOWED = {
    ("ALGORITHM", "read", "blind_test_input"),
    ("ALGORITHM", "write", "predictions"),
    ("ALGORITHM", "read", "aggregate_report"),
    ("BUSINESS", "read", "aggregate_report"),
    ("DATA", "read", "aggregate_report"),
    ("PM", "read", "aggregate_report"),
    ("OPS", "operate", "runtime"),
    ("OPS", "read", "aggregate_report"),
    ("QA", "read", "blind_test_gold"),
    ("QA", "write", "aggregate_report"),
    ("QA", "write", "audit_log"),
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RuntimeACL:
    def __init__(self, audit_log: Path):
        self.audit_log = audit_log
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)

    def _audit(self, *, role: str, service_account: str, action: str, asset: str, result: str, reason: str) -> None:
        record = {
            "timestamp": _now(),
            "subject_id": service_account,
            "role": role,
            "action": action,
            "asset": asset,
            "result": result,
            "reason": reason,
            "export_bytes": 0,
        }
        with self.audit_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def authorize(self, role: str, service_account: str, action: str, asset: str) -> bool:
        expected_account = SERVICE_ACCOUNTS.get(role)
        if expected_account != service_account:
            self._audit(role=role, service_account=service_account, action=action, asset=asset, result="DENIED", reason="service_account_role_mismatch")
            return False
        allowed = (role, action, asset) in ALLOWED
        self._audit(role=role, service_account=service_account, action=action, asset=asset, result="ALLOWED" if allowed else "DENIED", reason="policy_match" if allowed else "policy_denied")
        return allowed

    def read_asset(self, role: str, service_account: str, asset: str, path: Path) -> str:
        if not self.authorize(role, service_account, "read", asset):
            raise PermissionError(f"{role} cannot read {asset}")
        return path.read_text(encoding="utf-8")

    def write_asset(self, role: str, service_account: str, asset: str, path: Path, content: str) -> None:
        if not self.authorize(role, service_account, "write", asset):
            raise PermissionError(f"{role} cannot write {asset}")
        path.write_text(content, encoding="utf-8")


def probe_matrix(root: Path, report_path: Path) -> dict[str, Any]:
    """Exercise both allow and deny paths without returning Gold contents."""
    root.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    gold = root / "blind_test_gold.jsonl"
    blind_input = root / "blind_test_input.jsonl"
    aggregate = root / "aggregate_report.json"
    gold.write_text('{"sample_id":"S-GOLD-001","target":{"match_state":"MATCH"}}\n', encoding="utf-8")
    blind_input.write_text('{"sample_id":"S-INPUT-001","input":{"clause_text":"示例"}}\n', encoding="utf-8")
    aggregate.write_text('{"status":"approved-aggregate-only"}\n', encoding="utf-8")
    audit = root / "access_audit.jsonl"
    acl = RuntimeACL(audit)
    checks: list[dict[str, Any]] = []

    def expect(role: str, action: str, asset: str, expected: str, account: str | None = None) -> None:
        actual = "ALLOWED" if acl.authorize(role, account or SERVICE_ACCOUNTS[role], action, asset) else "DENIED"
        checks.append({"role": role, "action": action, "asset": asset, "expected": expected, "actual": actual, "pass": actual == expected})

    expect("ALGORITHM", "read", "blind_test_input", "ALLOWED")
    expect("ALGORITHM", "read", "blind_test_gold", "DENIED")
    expect("BUSINESS", "read", "blind_test_gold", "DENIED")
    expect("DATA", "read", "blind_test_gold", "DENIED")
    expect("PM", "read", "blind_test_gold", "DENIED")
    expect("OPS", "read", "blind_test_gold", "DENIED")
    expect("QA", "read", "blind_test_gold", "ALLOWED")
    expect("ALGORITHM", "read", "aggregate_report", "ALLOWED")
    expect("OPS", "read", "blind_test_gold", "DENIED", account=SERVICE_ACCOUNTS["OPS"])
    expect("QA", "read", "blind_test_gold", "DENIED", account="svc-c101-algorithm")

    qa_content = acl.read_asset("QA", SERVICE_ACCOUNTS["QA"], "blind_test_gold", gold)
    assert "S-GOLD-001" in qa_content
    try:
        acl.read_asset("ALGORITHM", SERVICE_ACCOUNTS["ALGORITHM"], "blind_test_gold", gold)
    except PermissionError:
        pass
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("algorithm unexpectedly read blind gold")

    audit_text = audit.read_text(encoding="utf-8")
    assert "S-GOLD-001" not in audit_text
    assert all(check["pass"] for check in checks)
    report = {
        "status": "PASS",
        "policy_version": "C1_01_Blind_Test_Gold_Access_Boundary_V0.1",
        "service_accounts": {role: account for role, account in SERVICE_ACCOUNTS.items()},
        "gold_sha256_for_test_only": _sha256(gold),
        "gold_plaintext_exported": False,
        "audit_contains_gold_plaintext": False,
        "checks": checks,
        "denied_probe_count": sum(check["actual"] == "DENIED" for check in checks),
        "allowed_probe_count": sum(check["actual"] == "ALLOWED" for check in checks),
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    import argparse
    import tempfile

    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="c101-acl-probe-") as directory:
        result = probe_matrix(Path(directory), args.report)
    print(json.dumps(result, ensure_ascii=False, indent=2))
