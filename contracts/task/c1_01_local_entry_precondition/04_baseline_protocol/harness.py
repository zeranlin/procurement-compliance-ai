#!/usr/bin/env python3
"""C1-01 baseline runner and DEV scorer.

The harness deliberately uses only the Python standard library.  It owns
protocol checks, adapter isolation, prediction validation, and metric
calculation; it does not own labels or change Benchmark Metric Spec meaning.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
PROTOCOL_VERSION = "C1_01_Baseline_Protocol_V0.2"
LOCK_PATH = Path(__file__).with_name(
    "C1_01_Baseline_Protocol_V0.2.1_Dependency_Lock.json"
)
TASK_ID = "C1-01_LOCAL_ENTRY_PRECONDITION"
ALLOWED_STATES = {"MATCH", "NO_MATCH", "NEEDS_CONTEXT"}
MATCH_SUBTYPES = {
    "SUPPLIER_REGISTRATION_LOCATION",
    "DISTANCE_TO_PURCHASER",
    "PREEXISTING_LOCAL_BRANCH",
    "OTHER_RELATED",
}
FACTORS = {
    "supplier_location_attribute",
    "distance_to_purchaser",
    "preexisting_branch",
    "pre_award_condition",
    "market_entry_gate",
    "scoring_advantage",
    "post_award_service",
    "location_mention_only",
    "local_service_term_ambiguous",
    "cross_reference_missing",
    "source_parse_uncertain",
    "exception_needs_review",
}
HARD_NEGATIVE_SLICES = {
    "HARD_NEGATIVE",
    "OFFICIAL_ANCHOR_HARD_NEGATIVE",
    "COUNTERFACTUAL_HARD_NEGATIVE",
}
BLOCKED_ELIGIBILITY = {"HOLD", "REWORK_SOURCE", "PENDING_DATA_QA"}
REQUIRED_TARGET_FIELDS = {
    "item_id",
    "requirement_id",
    "match_state",
    "subtype",
    "evidence_text",
    "evidence_spans",
    "evidence_refs",
    "reasoning_factors",
    "missing_context_questions",
    "confidence",
    "human_review_required",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def safe_input_path(path: Path) -> list[str]:
    """Reject protected Gold paths before opening them."""

    parts = {part.lower() for part in path.resolve().parts}
    if "blind_test_gold" in parts:
        return ["protected blind_test_gold path is not readable by the baseline harness"]
    return []


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    errors = safe_input_path(path)
    if errors:
        return [], errors
    if not path.is_file():
        return [], [f"file not found: {path}"]
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path}:{number}: JSON row must be an object")
            continue
        rows.append(value)
    return rows, errors


def _required_object(value: Any, name: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{name} must be an object")
        return None
    return value


def _check_span(span: Any, source: str | None, errors: list[str], prefix: str) -> None:
    if not isinstance(span, dict):
        errors.append(f"{prefix} must be an object")
        return
    required = {"text", "anchor", "document_id", "document_version", "page", "section", "start_char", "end_char"}
    missing = required - span.keys()
    if missing:
        errors.append(f"{prefix} missing: {sorted(missing)}")
        return
    if span["anchor"] not in {"CLAUSE", "CONTEXT"}:
        errors.append(f"{prefix}.anchor is invalid")
    if not isinstance(span["text"], str) or not span["text"]:
        errors.append(f"{prefix}.text must be non-empty")
    start, end = span["start_char"], span["end_char"]
    if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end <= start:
        errors.append(f"{prefix} has invalid character interval")
    elif source is not None and source[start:end] != span["text"]:
        errors.append(f"{prefix}.text is not the cited source substring")
    if not isinstance(span["page"], int) or span["page"] < 1:
        errors.append(f"{prefix}.page must be a positive integer")


def validate_prediction(prediction: Any, source_input: dict[str, Any] | None = None) -> list[str]:
    """Validate the bare JSON target object used by both adapter and scorer."""

    errors: list[str] = []
    target = _required_object(prediction, "prediction", errors)
    if target is None:
        return errors
    unknown = set(target) - REQUIRED_TARGET_FIELDS
    missing = REQUIRED_TARGET_FIELDS - set(target)
    if unknown:
        errors.append(f"prediction has unknown fields: {sorted(unknown)}")
    if missing:
        errors.append(f"prediction missing fields: {sorted(missing)}")
        return errors

    if target["item_id"] != TASK_ID:
        errors.append("prediction.item_id does not match task")
    if not isinstance(target["requirement_id"], str) or not target["requirement_id"]:
        errors.append("prediction.requirement_id must be non-empty")
    if source_input and target["requirement_id"] != source_input.get("requirement_id"):
        errors.append("prediction.requirement_id does not match input")
    state = target["match_state"]
    subtype = target["subtype"]
    if state not in ALLOWED_STATES:
        errors.append("prediction.match_state is invalid")
    if subtype not in MATCH_SUBTYPES | {"NONE"}:
        errors.append("prediction.subtype is invalid")

    if not isinstance(target["evidence_spans"], list):
        errors.append("prediction.evidence_spans must be an array")
    if not isinstance(target["evidence_refs"], list):
        errors.append("prediction.evidence_refs must be an array")
    if not isinstance(target["reasoning_factors"], list) or any(
        factor not in FACTORS for factor in target["reasoning_factors"]
    ):
        errors.append("prediction.reasoning_factors contains an invalid value")
    if not isinstance(target["missing_context_questions"], list) or any(
        not isinstance(question, str) or not question for question in target["missing_context_questions"]
    ):
        errors.append("prediction.missing_context_questions must contain non-empty strings")
    if target["confidence"] is not None and (
        not isinstance(target["confidence"], (int, float)) or not 0 <= target["confidence"] <= 1
    ):
        errors.append("prediction.confidence must be null or within [0,1]")
    if not isinstance(target["human_review_required"], bool):
        errors.append("prediction.human_review_required must be boolean")

    if state == "MATCH":
        if subtype == "NONE":
            errors.append("MATCH requires a non-NONE subtype")
        if not isinstance(target["evidence_text"], str) or not target["evidence_text"]:
            errors.append("MATCH requires evidence_text")
        if not target["evidence_spans"] or not target["evidence_refs"]:
            errors.append("MATCH requires evidence_spans and evidence_refs")
        if target["missing_context_questions"]:
            errors.append("MATCH cannot contain missing_context_questions")
    elif state == "NO_MATCH":
        if subtype != "NONE":
            errors.append("NO_MATCH requires subtype=NONE")
        if target["missing_context_questions"]:
            errors.append("NO_MATCH cannot contain missing_context_questions")
    elif state == "NEEDS_CONTEXT":
        if subtype != "NONE":
            errors.append("NEEDS_CONTEXT requires subtype=NONE")
        if not target["missing_context_questions"]:
            errors.append("NEEDS_CONTEXT requires a missing_context_question")
        if target["human_review_required"] is not True:
            errors.append("NEEDS_CONTEXT requires human_review_required=true")

    source_by_context: dict[str, dict[str, Any]] = {}
    if source_input and isinstance(source_input.get("context"), list):
        source_by_context = {
            item["context_id"]: item for item in source_input["context"] if isinstance(item, dict) and "context_id" in item
        }
    spans = target["evidence_spans"] if isinstance(target["evidence_spans"], list) else []
    refs = target["evidence_refs"] if isinstance(target["evidence_refs"], list) else []
    if len(spans) != len(refs) and (spans or refs):
        errors.append("evidence_spans and evidence_refs must be one-to-one")
    for index, span in enumerate(spans):
        source: str | None = None
        source_meta: dict[str, Any] | None = None
        if isinstance(span, dict) and source_input:
            if span.get("anchor") == "CLAUSE":
                source = source_input.get("clause_text")
                source_meta = source_input.get("source_location")
            elif span.get("anchor") == "CONTEXT":
                source_meta = source_by_context.get(span.get("context_id"))
                source = source_meta.get("text") if source_meta else None
                if source_meta is None:
                    errors.append(f"prediction.evidence_spans[{index}] references unknown context_id")
        _check_span(span, source, errors, f"prediction.evidence_spans[{index}]")
        if source_meta and isinstance(span, dict):
            location = source_meta.get("source_location", source_meta)
            for field in ("page", "section"):
                if field in location and span.get(field) != location[field]:
                    errors.append(f"prediction.evidence_spans[{index}].{field} does not match source")
        if index < len(refs) and isinstance(refs[index], dict) and isinstance(span, dict):
            for field in ("document_id", "document_version", "page", "section"):
                if refs[index].get(field) != span.get(field):
                    errors.append(f"prediction.evidence_refs[{index}] does not match evidence span")
    if spans and isinstance(target["evidence_text"], str) and target["evidence_text"] not in {
        span.get("text") for span in spans if isinstance(span, dict)
    }:
        errors.append("evidence_text must equal one cited span")
    return errors


def validate_dataset_row(row: dict[str, Any], smoke: bool = False) -> list[str]:
    errors: list[str] = []
    for field in ("schema_version", "task_id", "sample_id", "leakage_group_id", "input", "metadata"):
        if field not in row:
            errors.append(f"dataset row missing {field}")
    if row.get("schema_version") != "0.1":
        errors.append("dataset schema_version must be 0.1")
    if row.get("task_id") != TASK_ID:
        errors.append("dataset task_id does not match task")
    source_input = _required_object(row.get("input"), "dataset.input", errors)
    metadata = _required_object(row.get("metadata"), "dataset.metadata", errors)
    if source_input:
        for field in ("requirement_id", "clause_text", "document_id", "document_version", "source_location", "parser_quality"):
            if field not in source_input:
                errors.append(f"dataset.input missing {field}")
    if metadata:
        for field in ("case_slice", "review_state", "data_eligibility", "dataset_role"):
            if field not in metadata:
                errors.append(f"dataset.metadata missing {field}")
        eligibility = metadata.get("data_eligibility")
        role = metadata.get("dataset_role")
        if eligibility == "REWORK_SOURCE":
            if row.get("target") is not None:
                errors.append("REWORK_SOURCE requires target=null")
            errors.append("REWORK_SOURCE is not eligible for model execution")
        if role == "BLIND_GOLD":
            errors.append("BLIND_GOLD is not an algorithm-group input")
        if not smoke and eligibility in BLOCKED_ELIGIBILITY - {"REWORK_SOURCE"}:
            errors.append(f"{eligibility} is blocked by Preflight")
    if "target" in row and row["target"] is not None and source_input:
        errors.extend(validate_prediction(row["target"], source_input))
    if row.get("target") is None and metadata and metadata.get("dataset_role") not in {"BLIND_INPUT"} and metadata.get("data_eligibility") != "REWORK_SOURCE":
        errors.append("target=null is only allowed for BLIND_INPUT or REWORK_SOURCE")
    return errors


def verify_dependency_lock() -> list[str]:
    if not LOCK_PATH.is_file():
        return [f"dependency lock not found: {LOCK_PATH}"]
    try:
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read dependency lock: {exc}"]
    errors: list[str] = []
    if lock.get("lock_version") != "C1_01_Baseline_Protocol_V0.2.1":
        errors.append("unexpected dependency lock version")
    for dependency in lock.get("dependencies", []):
        path = ROOT / dependency["path"]
        if not path.is_file():
            errors.append(f"missing dependency: {dependency['path']}")
            continue
        actual = sha256_file(path)
        if actual != dependency.get("sha256"):
            errors.append(f"sha256 mismatch: {dependency['path']}")
    return errors


def preflight_rows(
    rows: list[dict[str, Any]],
    mode: str,
    few_shot_rows: list[dict[str, Any]] | None = None,
    smoke: bool = False,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    lock_errors = verify_dependency_lock()
    checks.append({"name": "dependency_lock", "status": "FAIL" if lock_errors else "PASS", "errors": lock_errors})
    ids = [row.get("sample_id") for row in rows]
    duplicate_ids = sorted({sample_id for sample_id in ids if ids.count(sample_id) > 1})
    id_errors = [f"duplicate sample_id: {sample_id}" for sample_id in duplicate_ids]
    checks.append({"name": "unique_sample_ids", "status": "FAIL" if id_errors else "PASS", "errors": id_errors})
    row_errors = []
    for index, row in enumerate(rows, 1):
        row_errors.extend(f"row {index}: {error}" for error in validate_dataset_row(row, smoke=smoke))
        if not smoke:
            metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
            source_input = row.get("input") if isinstance(row.get("input"), dict) else {}
            if metadata.get("data_eligibility") != "BENCHMARK_CANDIDATE":
                row_errors.append(f"row {index}: data_eligibility must be BENCHMARK_CANDIDATE")
            if metadata.get("dataset_role") not in {"DEV", "BLIND_INPUT", "REGRESSION"}:
                row_errors.append(f"row {index}: dataset_role is not executable: {metadata.get('dataset_role')}")
            if source_input.get("parser_quality") != "PASS":
                row_errors.append(f"row {index}: parser_quality must be PASS")
            if metadata.get("review_state") != "INTERNAL_REVIEWED":
                row_errors.append(f"row {index}: review_state must be INTERNAL_REVIEWED")
            if metadata.get("review_state") == "DISPUTED":
                row_errors.append(f"row {index}: DISPUTED is blocked by Preflight")
    checks.append({"name": "dataset_eligibility", "status": "FAIL" if row_errors else "PASS", "errors": row_errors})

    few_errors: list[str] = []
    if mode == "FEW_SHOT":
        if not few_shot_rows:
            few_errors.append("FEW_SHOT requires --few-shot-file")
        else:
            input_groups = {row.get("leakage_group_id") for row in rows}
            train_ids: set[str] = set()
            for index, row in enumerate(few_shot_rows, 1):
                train_ids.add(row.get("sample_id"))
                few_errors.extend(f"few-shot row {index}: {error}" for error in validate_dataset_row(row))
                metadata = row.get("metadata", {})
                if metadata.get("data_eligibility") != "TRAIN_ELIGIBLE":
                    few_errors.append(f"few-shot row {index}: data_eligibility must be TRAIN_ELIGIBLE")
                if metadata.get("dataset_role") != "TRAIN":
                    few_errors.append(f"few-shot row {index}: dataset_role must be TRAIN")
                if row.get("leakage_group_id") in input_groups:
                    few_errors.append(f"few-shot row {index}: leakage_group_id overlaps evaluation input")
            if len(train_ids) != len(few_shot_rows):
                few_errors.append("few-shot sample_id values must be unique")
    checks.append({"name": "few_shot_isolation", "status": "FAIL" if few_errors else "PASS", "errors": few_errors})
    failures = [check for check in checks if check["status"] == "FAIL"]
    return {
        "preflight_version": "C1_01_Baseline_Preflight_V0.2.1",
        "protocol_version": PROTOCOL_VERSION,
        "mode": mode,
        "status": "FAIL" if failures else "PASS",
        "row_count": len(rows),
        "checks": checks,
    }


def input_projection(row: dict[str, Any]) -> dict[str, Any]:
    source = row["input"]
    return {
        "requirement_id": source["requirement_id"],
        "project_id": source.get("project_id"),
        "document_id": source["document_id"],
        "document_version": source["document_version"],
        "clause_id": source.get("clause_id"),
        "clause_text": source["clause_text"],
        "business_stage": source.get("business_stage"),
        "context": source.get("context"),
        "source_location": source["source_location"],
        "parser_quality": source["parser_quality"],
    }


def build_request(row: dict[str, Any], mode: str, examples: list[dict[str, Any]], temperature: float, seed: int) -> dict[str, Any]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "task_id": TASK_ID,
        "mode": mode,
        "instruction": "Classify the requirement and return only the target JSON object defined by output_contract.",
        "input": input_projection(row),
        "examples": examples,
        "output_contract": {
            "type": "object",
            "additionalProperties": False,
            "required": sorted(REQUIRED_TARGET_FIELDS),
        },
        "generation": {"temperature": temperature, "seed": seed},
    }


def run_adapter(command: str, request: dict[str, Any]) -> tuple[str, str, int | None, list[str]]:
    try:
        process = subprocess.run(
            shlex.split(command),
            input=json_dump(request) + "\n",
            text=True,
            capture_output=True,
            check=False,
        )
    except (OSError, ValueError) as exc:
        return "", "", None, [f"adapter launch failed: {exc}"]
    errors: list[str] = []
    if process.returncode != 0:
        errors.append(f"adapter exited with code {process.returncode}")
    return process.stdout, process.stderr, process.returncode, errors


def run_command(args: argparse.Namespace) -> int:
    rows, load_errors = load_jsonl(Path(args.input))
    few_rows: list[dict[str, Any]] | None = None
    few_errors: list[str] = []
    mode = "FEW_SHOT" if args.few_shot_file else "ZERO_SHOT"
    if args.few_shot_file:
        few_rows, few_errors = load_jsonl(Path(args.few_shot_file))
    preflight = preflight_rows(rows, mode, few_rows, smoke=args.smoke)
    preflight["load_errors"] = load_errors + few_errors
    if preflight["load_errors"]:
        preflight["status"] = "FAIL"
    if args.preflight_report:
        Path(args.preflight_report).write_text(json_dump(preflight) + "\n", encoding="utf-8")
    if preflight["status"] != "PASS":
        print(json_dump(preflight), file=sys.stderr)
        return 2

    examples = []
    if few_rows:
        examples = [{"input": input_projection(row), "output": row["target"]} for row in few_rows]
    output_lines: list[str] = []
    invalid = 0
    for row in rows:
        started = time.monotonic()
        request = build_request(row, mode, examples, args.temperature, args.seed)
        raw, _stderr, _returncode, adapter_errors = run_adapter(args.adapter_command, request)
        prediction: dict[str, Any] | None = None
        errors = list(adapter_errors)
        if not errors:
            try:
                prediction_value = json.loads(raw)
            except json.JSONDecodeError as exc:
                prediction_value = None
                errors.append(f"adapter stdout is not one JSON object: {exc.msg}")
            if prediction_value is not None:
                validation_errors = validate_prediction(prediction_value, row["input"])
                errors.extend(validation_errors)
                if not validation_errors:
                    prediction = prediction_value
        if prediction is None:
            invalid += 1
        output_lines.append(
            json_dump(
                {
                    "sample_id": row["sample_id"],
                    "prediction": prediction,
                    "raw_response_sha256": sha256_bytes(raw.encode("utf-8")),
                    "raw_response_length": len(raw),
                    "validation_errors": errors,
                    "elapsed_ms": round((time.monotonic() - started) * 1000, 3),
                }
            )
        )
    output_path = Path(args.output)
    output_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    manifest = {
        "manifest_version": "C1_01_Baseline_Run_Manifest_V0.2.1",
        "protocol_version": PROTOCOL_VERSION,
        "mode": mode,
        "input_sha256": sha256_file(Path(args.input)),
        "prediction_sha256": sha256_file(output_path),
        "few_shot_sha256": sha256_file(Path(args.few_shot_file)) if args.few_shot_file else None,
        "model_id": args.model_id,
        "model_revision": args.model_revision,
        "generation": {"temperature": args.temperature, "seed": args.seed},
        "row_count": len(rows),
        "invalid_output_count": invalid,
        "preflight_status": preflight["status"],
    }
    Path(args.manifest).write_text(json_dump(manifest) + "\n", encoding="utf-8")
    print(json_dump(manifest))
    return 0


def ratio(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def prediction_state(prediction: dict[str, Any] | None) -> str:
    return prediction.get("match_state", "INVALID") if prediction else "INVALID"


def evidence_overlap(prediction: dict[str, Any], gold: dict[str, Any]) -> bool:
    for predicted in prediction.get("evidence_spans", []):
        for expected in gold.get("evidence_spans", []):
            same_source = all(
                predicted.get(field) == expected.get(field)
                for field in ("document_id", "document_version", "page")
            )
            if same_source and max(predicted.get("start_char", 0), expected.get("start_char", 0)) < min(
                predicted.get("end_char", 0), expected.get("end_char", 0)
            ):
                return True
    return False


def score_command(args: argparse.Namespace) -> int:
    gold_rows, gold_errors = load_jsonl(Path(args.gold))
    prediction_rows, prediction_errors = load_jsonl(Path(args.predictions))
    if gold_errors or prediction_errors:
        report = {"status": "FAIL", "alignment_errors": gold_errors + prediction_errors}
        Path(args.output).write_text(json_dump(report) + "\n", encoding="utf-8")
        print(json_dump(report), file=sys.stderr)
        return 2
    gold_contract_errors: list[str] = []
    for index, row in enumerate(gold_rows, 1):
        gold_contract_errors.extend(f"gold row {index}: {error}" for error in validate_dataset_row(row))
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        if metadata.get("data_eligibility") != "BENCHMARK_CANDIDATE":
            gold_contract_errors.append(f"gold row {index}: data_eligibility must be BENCHMARK_CANDIDATE")
        if metadata.get("dataset_role") not in {"DEV", "REGRESSION"}:
            gold_contract_errors.append(f"gold row {index}: dataset_role is not scoreable: {metadata.get('dataset_role')}")
        source_input = row.get("input") if isinstance(row.get("input"), dict) else {}
        if source_input.get("parser_quality") != "PASS":
            gold_contract_errors.append(f"gold row {index}: parser_quality must be PASS")
        if metadata.get("review_state") != "INTERNAL_REVIEWED":
            gold_contract_errors.append(f"gold row {index}: review_state must be INTERNAL_REVIEWED")
    if gold_contract_errors:
        report = {"status": "FAIL", "gold_contract_errors": gold_contract_errors}
        Path(args.output).write_text(json_dump(report) + "\n", encoding="utf-8")
        print(json_dump(report), file=sys.stderr)
        return 2
    gold_by_id: dict[str, dict[str, Any]] = {}
    alignment_errors: list[str] = []
    for row in gold_rows:
        sample_id = row.get("sample_id")
        if sample_id in gold_by_id:
            alignment_errors.append(f"duplicate gold sample_id: {sample_id}")
        gold_by_id[sample_id] = row
    pred_by_id: dict[str, dict[str, Any]] = {}
    for row in prediction_rows:
        sample_id = row.get("sample_id")
        if sample_id not in gold_by_id:
            alignment_errors.append(f"unknown prediction sample_id: {sample_id}")
        elif sample_id in pred_by_id:
            alignment_errors.append(f"duplicate prediction sample_id: {sample_id}")
        pred_by_id[sample_id] = row
    missing = sorted(set(gold_by_id) - set(pred_by_id))
    alignment_errors.extend(f"missing prediction sample_id: {sample_id}" for sample_id in missing)
    if alignment_errors:
        report = {"status": "FAIL", "alignment_errors": alignment_errors}
        Path(args.output).write_text(json_dump(report) + "\n", encoding="utf-8")
        print(json_dump(report), file=sys.stderr)
        return 2

    records: list[dict[str, Any]] = []
    for sample_id, gold_row in gold_by_id.items():
        prediction_row = pred_by_id[sample_id]
        prediction = prediction_row.get("prediction")
        errors = validate_prediction(prediction, gold_row.get("input", {})) if prediction is not None else ["INVALID_OUTPUT"]
        records.append(
            {
                "sample_id": sample_id,
                "gold": gold_row["target"],
                "gold_metadata": gold_row.get("metadata", {}),
                "gold_leakage_group_id": gold_row.get("leakage_group_id"),
                "prediction": prediction if not errors else None,
                "errors": prediction_row.get("validation_errors", []) + errors,
            }
        )
    n = len(records)
    valid_records = [record for record in records if record["prediction"] is not None and not record["errors"]]
    tp_match = sum(
        record["gold"]["match_state"] == "MATCH" and prediction_state(record["prediction"]) == "MATCH"
        for record in records
    )
    predicted_match = sum(prediction_state(record["prediction"]) == "MATCH" for record in valid_records)
    gold_match = sum(record["gold"]["match_state"] == "MATCH" for record in records)
    precision = ratio(tp_match, predicted_match)
    recall = ratio(tp_match, gold_match)
    f1 = None if precision is None or recall is None or precision + recall == 0 else 2 * precision * recall / (precision + recall)
    hard_negative = [record for record in records if record["gold_metadata"].get("case_slice") in HARD_NEGATIVE_SLICES]
    needs_context = [record for record in records if record["gold"]["match_state"] == "NEEDS_CONTEXT"]
    not_needs_context = [record for record in records if record["gold"]["match_state"] != "NEEDS_CONTEXT"]
    subtype_correct = sum(
        record["gold"]["match_state"] == "MATCH"
        and prediction_state(record["prediction"]) == "MATCH"
        and record["prediction"]["subtype"] == record["gold"]["subtype"]
        for record in valid_records
    )
    evidence_correct = sum(
        record["gold"]["match_state"] == "MATCH"
        and prediction_state(record["prediction"]) == "MATCH"
        and evidence_overlap(record["prediction"], record["gold"])
        for record in valid_records
    )
    pair_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        pair_id = record["gold_metadata"].get("pair_id")
        if pair_id:
            pair_groups[pair_id].append(record)
    pair_results = []
    for pair_id, pair in pair_groups.items():
        if len(pair) != 2 or pair[0]["gold_leakage_group_id"] != pair[1]["gold_leakage_group_id"]:
            continue
        if pair[0]["gold"]["match_state"] == pair[1]["gold"]["match_state"]:
            continue
        pair_results.append(
            all(
                record["prediction"] is not None
                and prediction_state(record["prediction"]) == record["gold"]["match_state"]
                and (
                    record["gold"]["match_state"] != "MATCH"
                    or record["prediction"]["subtype"] == record["gold"]["subtype"]
                )
                for record in pair
            )
        )

    metrics = {
        "structured_output_valid_rate": ratio(len(valid_records), n),
        "match_precision": precision,
        "match_recall": recall,
        "match_f1": f1,
        "hard_negative_fpr": ratio(sum(prediction_state(record["prediction"]) == "MATCH" for record in hard_negative), len(hard_negative)),
        "needs_context_recall": ratio(sum(prediction_state(record["prediction"]) == "NEEDS_CONTEXT" for record in needs_context), len(needs_context)),
        "unnecessary_abstention_rate": ratio(sum(prediction_state(record["prediction"]) == "NEEDS_CONTEXT" for record in not_needs_context), len(not_needs_context)),
        "match_subtype_accuracy": ratio(subtype_correct, gold_match),
        "evidence_overlap_proxy_recall": ratio(evidence_correct, gold_match),
        "counterfactual_pair_accuracy": ratio(sum(pair_results), len(pair_results)),
        "evidence_hit_rate": None,
    }
    slice_metrics: dict[str, dict[str, Any]] = {}
    for slice_name in sorted({record["gold_metadata"].get("case_slice") for record in records}):
        slice_records = [record for record in records if record["gold_metadata"].get("case_slice") == slice_name]
        slice_valid = [record for record in slice_records if record["prediction"] is not None and not record["errors"]]
        slice_tp = sum(
            record["gold"]["match_state"] == "MATCH" and prediction_state(record["prediction"]) == "MATCH"
            for record in slice_records
        )
        slice_predicted = sum(prediction_state(record["prediction"]) == "MATCH" for record in slice_valid)
        slice_gold = sum(record["gold"]["match_state"] == "MATCH" for record in slice_records)
        slice_precision = ratio(slice_tp, slice_predicted)
        slice_recall = ratio(slice_tp, slice_gold)
        slice_metrics[slice_name] = {
            "sample_count": len(slice_records),
            "structured_output_valid_rate": ratio(len(slice_valid), len(slice_records)),
            "match_precision": slice_precision,
            "match_recall": slice_recall,
            "match_f1": None if slice_precision is None or slice_recall is None or slice_precision + slice_recall == 0 else 2 * slice_precision * slice_recall / (slice_precision + slice_recall),
        }
    for record in records:
        if record["gold"]["match_state"] != prediction_state(record["prediction"]):
            record["errors"].append("MATCH_STATE_MISMATCH")
        if record["gold"]["match_state"] == "MATCH" and prediction_state(record["prediction"]) == "MATCH":
            if record["gold"]["subtype"] != record["prediction"]["subtype"]:
                record["errors"].append("SUBTYPE_MISMATCH")
            if not evidence_overlap(record["prediction"], record["gold"]):
                record["errors"].append("EVIDENCE_OVERLAP_MISS")
    report = {
        "status": "PASS",
        "run_id": args.run_id,
        "protocol_version": PROTOCOL_VERSION,
        "metric_spec_version": "C1_01_Benchmark_Metric_Spec_V0.2",
        "gold_sha256": sha256_file(Path(args.gold)),
        "predictions_sha256": sha256_file(Path(args.predictions)),
        "sample_count": n,
        "overall_metrics": metrics,
        "slice_metrics": slice_metrics,
        "invalid_output_summary": {"count": n - len(valid_records)},
        "per_example_error_codes": {record["sample_id"]: sorted(set(record["errors"])) for record in records if record["errors"]},
        "counterfactual_pair_results": pair_results,
    }
    Path(args.output).write_text(json_dump(report) + "\n", encoding="utf-8")
    print(json_dump(report))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--input", required=True)
    preflight.add_argument("--few-shot-file")
    preflight.add_argument("--smoke", action="store_true")
    preflight.add_argument("--output")
    run = subparsers.add_parser("run")
    run.add_argument("--input", required=True)
    run.add_argument("--adapter-command", required=True)
    run.add_argument("--model-id", required=True)
    run.add_argument("--model-revision", required=True)
    run.add_argument("--output", required=True)
    run.add_argument("--manifest", required=True)
    run.add_argument("--few-shot-file")
    run.add_argument("--preflight-report")
    run.add_argument("--temperature", type=float, default=0.0)
    run.add_argument("--seed", type=int, default=0)
    run.add_argument("--smoke", action="store_true")
    score = subparsers.add_parser("score")
    score.add_argument("--gold", required=True)
    score.add_argument("--predictions", required=True)
    score.add_argument("--output", required=True)
    score.add_argument("--run-id", default="DEV_SCORE")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "preflight":
        rows, load_errors = load_jsonl(Path(args.input))
        few_rows, few_errors = ([], [])
        if args.few_shot_file:
            few_rows, few_errors = load_jsonl(Path(args.few_shot_file))
        mode = "FEW_SHOT" if args.few_shot_file else "ZERO_SHOT"
        report = preflight_rows(rows, mode, few_rows, smoke=args.smoke)
        report["load_errors"] = load_errors + few_errors
        if report["load_errors"]:
            report["status"] = "FAIL"
        if args.output:
            Path(args.output).write_text(json_dump(report) + "\n", encoding="utf-8")
        print(json_dump(report))
        return 0 if report["status"] == "PASS" else 2
    if args.command == "run":
        return run_command(args)
    return score_command(args)


if __name__ == "__main__":
    raise SystemExit(main())
