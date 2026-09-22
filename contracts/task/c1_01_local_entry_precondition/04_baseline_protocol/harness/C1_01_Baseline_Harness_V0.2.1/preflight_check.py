#!/usr/bin/env python3
"""C1-01 Baseline Protocol V0.2.1 preflight gate.

The gate runs before any formal Base Model invocation. It treats a source
rework row as an invalid dataset candidate, while an invalid model prediction
is retained by the Harness and counted by the scorer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


TASK = "C1-01_LOCAL_ENTRY_PRECONDITION"
PROTOCOL = "C1_01_Baseline_Protocol_V0.2.1"
OUTPUT_SCHEMA_NAME = "C1_01_Model_Output_Schema_V0.2.json"
TARGET_KEYS = {
    "item_id", "requirement_id", "match_state", "subtype", "evidence_text",
    "evidence_spans", "evidence_refs", "reasoning_factors",
    "missing_context_questions", "confidence", "human_review_required",
}
STATES = {"MATCH", "NO_MATCH", "NEEDS_CONTEXT"}
SUBTYPES = {
    "SUPPLIER_REGISTRATION_LOCATION", "DISTANCE_TO_PURCHASER",
    "PREEXISTING_LOCAL_BRANCH", "OTHER_RELATED", "NONE",
}
FACTORS = {
    "supplier_location_attribute", "distance_to_purchaser", "preexisting_branch",
    "pre_award_condition", "market_entry_gate", "scoring_advantage",
    "post_award_service", "location_mention_only", "local_service_term_ambiguous",
    "cross_reference_missing", "source_parse_uncertain", "exception_needs_review",
}
ROLES = {"TRAIN", "DEV", "BLIND_INPUT"}
ELIGIBLE = {"TRAIN_ELIGIBLE", "BENCHMARK_CANDIDATE"}
FROZEN_VERSIONS = {
    "business_spec": "BR_C1_01_Business_Task_Spec_V0.1",
    "label_guide": "C1_01_Label_Guide_V0.1",
    "dataset_schema": "C1_01_Dataset_Schema_V0.2",
    "metric_spec": "C1_01_Benchmark_Metric_Spec_V0.2",
    "blind_test_rules": "C1_01_Blind_Test_Management_Rules_V0.1",
    "blind_gold_boundary": "C1_01_Blind_Test_Gold_Access_Boundary_V0.1",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: dataset row must be an object")
            result.append(value)
    return result


def _type_number(value: Any) -> bool:
    return type(value) in (int, float) and not isinstance(value, bool) and math.isfinite(value)


def _exact_source(span: dict[str, Any], inp: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None, str | None, str | None]:
    anchor = span.get("anchor")
    if anchor == "CLAUSE":
        if span.get("context_id") is not None:
            return None, None, None, None
        return inp.get("clause_text"), inp.get("source_location"), inp.get("document_id"), inp.get("document_version")
    if anchor == "CONTEXT":
        context_id = span.get("context_id")
        for item in inp.get("context") or []:
            if item.get("context_id") == context_id:
                return item.get("text"), item.get("source_location"), item.get("document_id"), item.get("document_version")
    return None, None, None, None


def validate_prediction(prediction: Any, inp: dict[str, Any], *, require_evidence: bool = False) -> list[str]:
    """Validate a bare prediction object against the frozen output contract."""
    errors: list[str] = []
    if not isinstance(prediction, dict):
        return ["prediction must be one JSON object"]
    if set(prediction) != TARGET_KEYS:
        errors.append("prediction keys are not exactly the frozen output keys")
    if prediction.get("item_id") != TASK:
        errors.append("item_id mismatch")
    if prediction.get("requirement_id") != inp.get("requirement_id"):
        errors.append("requirement_id mismatch")
    state = prediction.get("match_state")
    subtype = prediction.get("subtype")
    if state not in STATES:
        errors.append("invalid match_state")
    if subtype not in SUBTYPES:
        errors.append("invalid subtype")
    if state == "MATCH" and subtype == "NONE":
        errors.append("MATCH requires a non-NONE subtype")
    if state in {"NO_MATCH", "NEEDS_CONTEXT"} and subtype != "NONE":
        errors.append(f"{state} requires subtype=NONE")

    spans = prediction.get("evidence_spans")
    refs = prediction.get("evidence_refs")
    if not isinstance(spans, list):
        errors.append("evidence_spans must be an array")
        spans = []
    if not isinstance(refs, list):
        errors.append("evidence_refs must be an array")
        refs = []
    if len(spans) != len(refs):
        errors.append("evidence_spans/evidence_refs cardinality mismatch")
    for index, span in enumerate(spans):
        if not isinstance(span, dict):
            errors.append(f"evidence_spans[{index}] must be an object")
            continue
        span_required = {"text", "anchor", "context_id", "document_id", "document_version", "page", "section", "start_char", "end_char"}
        if set(span) != span_required:
            errors.append(f"evidence_spans[{index}] fields differ from schema")
            continue
        source, location, document_id, document_version = _exact_source(span, inp)
        start, end = span.get("start_char"), span.get("end_char")
        if source is None or location is None or not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= len(source) or source[start:end] != span.get("text"):
            errors.append(f"evidence_spans[{index}] is not an exact half-open source substring")
        else:
            for key, expected in (("document_id", document_id), ("document_version", document_version), ("page", location.get("page")), ("section", location.get("section"))):
                if span.get(key) != expected:
                    errors.append(f"evidence_spans[{index}] locator mismatch: {key}")
    for index, ref in enumerate(refs):
        if not isinstance(ref, dict) or set(ref) != {"document_id", "document_version", "page", "section"}:
            errors.append(f"evidence_refs[{index}] fields differ from schema")
    for span, ref in zip(spans, refs):
        if isinstance(span, dict) and isinstance(ref, dict) and any(span.get(k) != ref.get(k) for k in ("document_id", "document_version", "page", "section")):
            errors.append("evidence span/reference locator mismatch")

    evidence_text = prediction.get("evidence_text")
    if evidence_text is not None and (not isinstance(evidence_text, str) or not evidence_text):
        errors.append("evidence_text must be null or a non-empty string")
    if evidence_text is not None and evidence_text not in [x.get("text") for x in spans if isinstance(x, dict)]:
        errors.append("evidence_text must equal one located span")
    if evidence_text is None and spans:
        errors.append("evidence_text cannot be null when evidence spans are present")

    factors = prediction.get("reasoning_factors")
    if not isinstance(factors, list) or len(factors) != len(set(factors)) or any(x not in FACTORS for x in factors):
        errors.append("reasoning_factors contains invalid or duplicate values")
    questions = prediction.get("missing_context_questions")
    if not isinstance(questions, list) or len(questions) != len(set(questions)) or any(not isinstance(x, str) or not x for x in questions):
        errors.append("missing_context_questions contains invalid or duplicate values")
        questions = []
    confidence = prediction.get("confidence")
    if confidence is not None and (not _type_number(confidence) or not 0 <= confidence <= 1):
        errors.append("confidence must be null or a finite number in [0,1]")
    if type(prediction.get("human_review_required")) is not bool:
        errors.append("human_review_required must be boolean")
    if state == "MATCH" and questions:
        errors.append("MATCH cannot have missing_context_questions")
    if state == "NEEDS_CONTEXT" and (not questions or prediction.get("human_review_required") is not True):
        errors.append("NEEDS_CONTEXT requires a question and human_review_required=true")
    if require_evidence and (not evidence_text or not spans or not refs):
        errors.append("eligible dataset record requires non-empty evidence")
    return errors


def _row_errors(row: dict[str, Any], expected_role: str, expected_schema_hash: str) -> list[str]:
    errors: list[str] = []
    required_top = {"schema_version", "schema_sha256", "task_id", "sample_id", "leakage_group_id", "annotation_state", "input", "target", "metadata"}
    if set(row) != required_top:
        errors.append("top-level fields differ from Dataset Schema V0.2")
    if row.get("schema_version") != "0.2" or row.get("schema_sha256") != expected_schema_hash:
        errors.append("dataset schema version/hash mismatch")
    if row.get("task_id") != TASK:
        errors.append("task_id mismatch")
    if not isinstance(row.get("sample_id"), str) or not re.fullmatch(r"S-C101-[A-Za-z0-9._-]+", row.get("sample_id", "")):
        errors.append("invalid sample_id")
    if not isinstance(row.get("leakage_group_id"), str) or not row.get("leakage_group_id"):
        errors.append("missing leakage_group_id")
    inp = row.get("input")
    meta = row.get("metadata")
    if not isinstance(inp, dict) or not isinstance(meta, dict):
        return errors + ["input and metadata must be objects"]
    if row.get("annotation_state") != "LABELED":
        errors.append("annotation_state is not LABELED")
    if row.get("target") is None:
        errors.append("target=null is not a model-eligible input")
    if meta.get("data_eligibility") in {"REWORK_SOURCE", "HOLD", "PENDING_DATA_QA"}:
        errors.append(f"data_eligibility={meta.get('data_eligibility')} is blocked")
    if meta.get("review_state") == "DISPUTED":
        errors.append("review_state=DISPUTED is blocked")
    if meta.get("review_state") != "INTERNAL_REVIEWED":
        errors.append("record must be INTERNAL_REVIEWED")
    if meta.get("dataset_role") != expected_role:
        errors.append(f"expected dataset_role={expected_role}")
    expected_eligibility = "TRAIN_ELIGIBLE" if expected_role in {"TRAIN", "DEV"} else "BENCHMARK_CANDIDATE"
    if meta.get("data_eligibility") != expected_eligibility:
        errors.append(f"expected data_eligibility={expected_eligibility}")
    if inp.get("parser_quality") != "PASS" or inp.get("source_defect_prevents_judgment") is not False:
        errors.append("input has an unresolved source defect")
    if meta.get("source_kind") != "PROCUREMENT_DOCUMENT" or meta.get("source_verified_at_procurement_document_level") is not True or meta.get("evidence_status") != "VERIFIED":
        errors.append("source/evidence is not verified procurement-document data")
    target_errors = validate_prediction(row.get("target"), inp, require_evidence=True)
    errors.extend("target: " + error for error in target_errors)
    return errors


def _read_role(path: Path, role: str, expected_schema_hash: str) -> tuple[list[dict[str, Any]], list[str]]:
    try:
        records = read_jsonl(path)
    except (OSError, ValueError) as exc:
        return [], [str(exc)]
    if not records:
        return records, [f"{path}: empty dataset"]
    errors: list[str] = []
    ids: set[str] = set()
    for row in records:
        sample_id = row.get("sample_id")
        if sample_id in ids:
            errors.append(f"{path}: duplicate sample_id={sample_id}")
        ids.add(sample_id)
        errors.extend(f"{path}:{sample_id}: {error}" for error in _row_errors(row, role, expected_schema_hash))
    return records, errors


def run_preflight(manifest_path: str | Path, *, train: str | Path | None = None, dev: str | Path | None = None, blind_input: str | Path | None = None, smoke: bool = False) -> dict[str, Any]:
    manifest_path = Path(manifest_path).resolve()
    errors: list[str] = []
    checks: dict[str, str] = {}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"protocol": PROTOCOL, "status": "RUN_ABORTED", "errors": [f"manifest unreadable: {exc}"], "checks": {}}
    if manifest.get("protocol") != PROTOCOL or manifest.get("status") != "FROZEN":
        errors.append("protocol manifest is not the frozen C1_01_Baseline_Protocol_V0.2.1")
    base = manifest_path.parent
    deps = manifest.get("dependencies")
    if not isinstance(deps, dict):
        errors.append("manifest.dependencies missing")
        deps = {}
    expected: dict[str, str] = {}
    for name, item in deps.items():
        if not isinstance(item, dict) or not item.get("path") or not item.get("version") or not item.get("sha256"):
            errors.append(f"dependency lock incomplete: {name}")
            continue
        if name in FROZEN_VERSIONS and item.get("version") != FROZEN_VERSIONS[name]:
            errors.append(f"dependency version mismatch: {name}")
        path = (base / item["path"]).resolve()
        if not path.is_file():
            errors.append(f"dependency missing: {name}: {path}")
            continue
        actual = sha256_file(path)
        expected[name] = actual
        if actual != item["sha256"]:
            errors.append(f"dependency hash mismatch: {name}")
        if path.suffix in {".md", ".txt"} and "FROZEN" not in path.read_text(encoding="utf-8"):
            errors.append(f"dependency status is not FROZEN: {name}")
        checks[name] = "PASS" if actual == item["sha256"] else "FAIL"
    required_names = {"business_spec", "label_guide", "dataset_schema", "metric_spec"}
    missing = required_names - set(deps)
    if missing:
        errors.append("required dependency locks missing: " + ", ".join(sorted(missing)))
    schema_item = deps.get("dataset_schema", {})
    schema_path = (base / schema_item.get("path", "")).resolve()
    expected_schema_hash = schema_item.get("sha256")
    if schema_path.is_file():
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            if schema.get("$id") != "urn:procurementlm:c1-01:dataset-schema:0.2":
                errors.append("dataset schema is not V0.2")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"dataset schema unreadable: {exc}")
    output_item = manifest.get("output_schema", {})
    output_path = (base / output_item.get("path", OUTPUT_SCHEMA_NAME)).resolve()
    if not output_path.is_file():
        errors.append("model output schema missing")
    elif sha256_file(output_path) != output_item.get("sha256"):
        errors.append("model output schema hash mismatch")

    rows_by_role: dict[str, list[dict[str, Any]]] = {}
    if smoke:
        checks["dataset_candidate"] = "SKIPPED_SMOKE"
    else:
        paths = {"TRAIN": train, "DEV": dev, "BLIND_INPUT": blind_input}
        if any(value is None for value in paths.values()):
            errors.append("formal preflight requires train, dev, and blind_input paths to prove split isolation")
        for role, raw_path in paths.items():
            if raw_path is None:
                continue
            path = Path(raw_path).resolve()
            records, row_errors = _read_role(path, role, expected_schema_hash)
            rows_by_role[role] = records
            errors.extend(row_errors)
            checks[role] = "PASS" if not row_errors else "FAIL"
        groups: dict[str, set[str]] = defaultdict(set)
        pairs: dict[str, set[str]] = defaultdict(set)
        for role, records in rows_by_role.items():
            for row in records:
                groups[row.get("leakage_group_id")].add(role)
                pair = row.get("metadata", {}).get("pair_id")
                if pair:
                    pairs[pair].add(role)
        for group, roles in groups.items():
            if len(roles) > 1:
                errors.append(f"train/dev/blind leakage: leakage_group_id={group} in {sorted(roles)}")
        for pair, roles in pairs.items():
            if len(roles) > 1:
                errors.append(f"counterfactual pair crosses split: pair_id={pair} in {sorted(roles)}")
        checks["train_dev_leakage"] = "PASS" if not any("leakage" in error for error in errors) else "FAIL"
        checks["no_rework_hold_disputed_blind_gold"] = "PASS" if not any(any(x in error for x in ("target=null", "REWORK_SOURCE", "HOLD", "DISPUTED", "BLIND_GOLD")) for error in errors) else "FAIL"

    status = "PASS" if not errors else "RUN_ABORTED"
    return {
        "protocol": PROTOCOL,
        "status": status,
        "manifest": str(manifest_path),
        "checks": checks,
        "errors": errors,
        "dependency_hashes_observed": expected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--train", type=Path)
    parser.add_argument("--dev", type=Path)
    parser.add_argument("--blind-input", type=Path)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = run_preflight(args.manifest, train=args.train, dev=args.dev, blind_input=args.blind_input, smoke=args.smoke)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
