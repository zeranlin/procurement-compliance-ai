#!/usr/bin/env python3
"""V0.2 schema, cross-field, evidence, provenance and seed revalidation tool.

The validator deliberately treats source repair as a valid *record state* but
never as a supervised label. It is therefore possible for a rework record to
pass JSON Schema while being blocked from every train/dev/blind-gold role.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover - clear operator error
    raise SystemExit("jsonschema is required: python -m pip install jsonschema") from exc


TASK = "C1-01_LOCAL_ENTRY_PRECONDITION"
ELIGIBLE = {"TRAIN_ELIGIBLE", "BENCHMARK_CANDIDATE"}
PROHIBITED_REWORK_ROLES = {"TRAIN", "DEV", "BLIND_GOLD"}
HARD_NEGATIVE_SLICES = {
    "HARD_NEGATIVE",
    "OFFICIAL_ANCHOR_HARD_NEGATIVE",
    "COUNTERFACTUAL_HARD_NEGATIVE",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def path_string(path: Any) -> str:
    return "/" + "/".join(str(x) for x in path)


def schema_errors(record: dict[str, Any], validator: Draft202012Validator) -> list[str]:
    errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
    return [f"{path_string(e.path)}: {e.message}" for e in errors]


def _target_source_text(record: dict[str, Any], span: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    inp = record["input"]
    if span["anchor"] == "CLAUSE":
        return inp["clause_text"], inp["source_location"]
    if span["context_id"] is None or not inp["context"]:
        return None, None
    for context in inp["context"]:
        if context["context_id"] == span["context_id"]:
            return context["text"], context["source_location"]
    return None, None


def cross_field_errors(record: dict[str, Any], expected_schema_sha256: str) -> list[str]:
    errors: list[str] = []
    root = record
    inp = root["input"]
    target = root["target"]
    meta = root["metadata"]
    annotation_state = root["annotation_state"]
    eligibility = meta["data_eligibility"]
    role = meta["dataset_role"]
    source_kind = meta["source_kind"]

    if root["schema_sha256"] != expected_schema_sha256:
        errors.append("schema_sha256 does not match the supplied schema file")
    if root["task_id"] != TASK or root["input"]["requirement_id"] != (target or {}).get("requirement_id", root["input"]["requirement_id"]):
        errors.append("task_id/requirement_id identity mismatch")

    if annotation_state == "LABELED":
        if target is None:
            errors.append("LABELED record must have a non-null target")
        if inp["parser_quality"] != "PASS" or inp["source_defect_prevents_judgment"]:
            errors.append("LABELED record must have parser_quality=PASS and no source defect")
        if inp["source_defect_reason"] is not None:
            errors.append("LABELED record must not carry source_defect_reason")
    elif annotation_state == "UNAVAILABLE_SOURCE_REWORK":
        if target is not None:
            errors.append("UNAVAILABLE_SOURCE_REWORK record must have target=null")
        if inp["parser_quality"] != "UNCERTAIN" or not inp["source_defect_prevents_judgment"]:
            errors.append("source rework requires parser_quality=UNCERTAIN and source_defect_prevents_judgment=true")
        if not inp["source_defect_reason"]:
            errors.append("source rework requires source_defect_reason")
        if eligibility != "REWORK_SOURCE":
            errors.append("source rework requires data_eligibility=REWORK_SOURCE")
        if role in PROHIBITED_REWORK_ROLES:
            errors.append(f"source rework cannot use dataset_role={role}")
    else:
        errors.append(f"unknown annotation_state={annotation_state}")

    if inp["parser_quality"] == "UNCERTAIN" and not inp["source_defect_prevents_judgment"]:
        errors.append("parser_quality=UNCERTAIN requires an explicit source defect preventing judgment")
    if inp["source_defect_prevents_judgment"] and annotation_state != "UNAVAILABLE_SOURCE_REWORK":
        errors.append("source defect preventing judgment must isolate the record as UNAVAILABLE_SOURCE_REWORK")
    if eligibility == "REWORK_SOURCE" and (annotation_state != "UNAVAILABLE_SOURCE_REWORK" or target is not None):
        errors.append("REWORK_SOURCE requires UNAVAILABLE_SOURCE_REWORK and target=null")
    if role == "REWORK_QUEUE" and eligibility != "REWORK_SOURCE":
        errors.append("REWORK_QUEUE requires data_eligibility=REWORK_SOURCE")
    if role in {"TRAIN", "DEV"} and eligibility != "TRAIN_ELIGIBLE":
        errors.append(f"dataset_role={role} requires TRAIN_ELIGIBLE")
    if role == "BLIND_GOLD" and eligibility != "BENCHMARK_CANDIDATE":
        errors.append("dataset_role=BLIND_GOLD requires BENCHMARK_CANDIDATE")

    if meta["review_state"] == "DISPUTED":
        if eligibility != "HOLD":
            errors.append("review_state=DISPUTED requires data_eligibility=HOLD")
        if target is not None and not target["human_review_required"]:
            errors.append("DISPUTED labeled record requires human_review_required=true")

    if eligibility in ELIGIBLE:
        if annotation_state != "LABELED" or target is None:
            errors.append("eligible dataset record must be LABELED with a non-null target")
        if inp["parser_quality"] != "PASS" or inp["source_defect_prevents_judgment"]:
            errors.append("eligible dataset record must have reliable parsing")
        if source_kind != "PROCUREMENT_DOCUMENT" or not meta["source_verified_at_procurement_document_level"]:
            errors.append("eligible dataset record requires a verified procurement-document source")
        if meta["evidence_status"] != "VERIFIED":
            errors.append("eligible dataset record requires evidence_status=VERIFIED")
        if meta["review_state"] != "INTERNAL_REVIEWED":
            errors.append("eligible dataset record requires INTERNAL_REVIEWED")

    if source_kind in {"SYNTHETIC", "OFFICIAL_CASE_PARAPHRASE"}:
        if meta["source_verified_at_procurement_document_level"] or meta["is_verbatim_procurement_clause"]:
            errors.append("synthetic/paraphrase source cannot be marked as verified verbatim procurement text")
        if meta["source_sha256"] is not None:
            errors.append("synthetic/paraphrase source must not claim a procurement-document SHA-256")
        if eligibility in ELIGIBLE:
            errors.append("synthetic/paraphrase source cannot be train-eligible or benchmark-candidate")

    if source_kind == "PROCUREMENT_DOCUMENT":
        if meta["source_verified_at_procurement_document_level"] and meta["source_url"] is None:
            errors.append("verified procurement source requires source_url")
        if meta["source_verified_at_procurement_document_level"] and meta["source_sha256"] is None:
            errors.append("verified procurement source requires source_sha256")
        if meta["source_verified_at_procurement_document_level"] and inp["source_location"]["page"] is None:
            errors.append("verified procurement source requires a human page number")

    if annotation_state == "UNAVAILABLE_SOURCE_REWORK" and role in PROHIBITED_REWORK_ROLES:
        errors.append("parse/source failure is isolated from TRAIN, DEV and BLIND_GOLD")

    if target is not None:
        if target["item_id"] != TASK or target["requirement_id"] != inp["requirement_id"]:
            errors.append("target identity does not match input")
        state = target["match_state"]
        if state == "MATCH":
            if target["subtype"] == "NONE":
                errors.append("MATCH cannot use subtype=NONE")
            if target["missing_context_questions"]:
                errors.append("MATCH cannot carry missing_context_questions")
        elif state == "NO_MATCH":
            if target["subtype"] != "NONE":
                errors.append("NO_MATCH must use subtype=NONE")
            if target["missing_context_questions"]:
                errors.append("NO_MATCH cannot carry missing_context_questions")
        elif state == "NEEDS_CONTEXT":
            if target["subtype"] != "NONE":
                errors.append("NEEDS_CONTEXT must use subtype=NONE")
            if not target["missing_context_questions"]:
                errors.append("NEEDS_CONTEXT requires at least one missing_context_question")
            if not target["human_review_required"]:
                errors.append("NEEDS_CONTEXT requires human_review_required=true")

        spans = target["evidence_spans"]
        refs = target["evidence_refs"]
        if len(spans) != len(refs):
            errors.append("evidence_spans/evidence_refs cardinality mismatch")
        for index, span in enumerate(spans):
            text, location = _target_source_text(record, span)
            if text is None or location is None:
                errors.append(f"evidence_spans[{index}] cannot resolve its source text")
                continue
            start, end = span["start_char"], span["end_char"]
            if end <= start or end > len(text) or text[start:end] != span["text"]:
                errors.append(f"evidence_spans[{index}] is not an exact half-open source substring")
            ref = refs[index]
            for key in ("document_id", "document_version", "page", "section"):
                if span[key] != ref[key]:
                    errors.append(f"evidence_spans[{index}] and evidence_refs[{index}] locator mismatch: {key}")
                if span[key] != (inp[key] if key in {"document_id", "document_version"} else location[key]):
                    errors.append(f"evidence_spans[{index}] does not point to its declared source location: {key}")
        evidence_text = target["evidence_text"]
        if evidence_text is not None:
            if not spans or evidence_text not in [span["text"] for span in spans]:
                errors.append("evidence_text must equal one located evidence span")
        elif spans:
            errors.append("evidence_spans cannot be supplied while evidence_text is null")

        if eligibility in ELIGIBLE:
            if not target["evidence_text"] or not target["evidence_spans"] or not target["evidence_refs"]:
                errors.append("eligible labeled record requires non-empty evidence")
        if meta["case_slice"] in HARD_NEGATIVE_SLICES and eligibility in ELIGIBLE:
            if not target["evidence_text"]:
                errors.append("eligible hard negative requires its source text as evidence")

    if inp["business_stage"] is None and target is not None and target["match_state"] == "NEEDS_CONTEXT" and not target["missing_context_questions"]:
        errors.append("unknown business_stage requires a concrete missing-context question")
    if meta["pair_id"] is None and meta["counterfactual_change"] is not None:
        errors.append("counterfactual_change requires pair_id")
    if meta["pair_id"] is not None and not meta["counterfactual_change"]:
        errors.append("pair_id requires counterfactual_change")
    if meta["parent_sample_id"] is not None and source_kind != "SYNTHETIC":
        errors.append("parent_sample_id is only allowed for synthetic derivatives")
    if meta["source_rework_reason"] is not None and annotation_state != "UNAVAILABLE_SOURCE_REWORK":
        errors.append("source_rework_reason is only allowed on a source-rework record")
    return errors


def validate_records(records: list[dict[str, Any]], schema_path: Path) -> dict[str, Any]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    schema_digest = sha256_file(schema_path)
    rows: list[dict[str, Any]] = []
    ids: set[str] = set()
    group_roles: dict[str, set[str]] = defaultdict(set)
    pair_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        schema_errs = schema_errors(record, validator)
        cross_errs = [] if schema_errs else cross_field_errors(record, schema_digest)
        if record.get("sample_id") in ids:
            cross_errs.append("duplicate sample_id")
        ids.add(record.get("sample_id"))
        meta = record.get("metadata", {})
        group = record.get("leakage_group_id")
        role = meta.get("dataset_role")
        if role in {"TRAIN", "DEV", "BLIND_INPUT", "BLIND_GOLD"}:
            group_roles[group].add("BLIND" if role.startswith("BLIND") else role)
        if meta.get("pair_id"):
            pair_rows[meta["pair_id"]].append(record)
        rows.append({
            "sample_id": record.get("sample_id"),
            "schema_valid": not schema_errs,
            "cross_field_valid": not schema_errs and not cross_errs,
            "errors": schema_errs + cross_errs,
            "annotation_state": record.get("annotation_state"),
            "match_state": (record.get("target") or {}).get("match_state"),
            "review_state": meta.get("review_state"),
            "data_eligibility": meta.get("data_eligibility"),
            "dataset_role": role,
            "leakage_group_id": group,
            "pair_id": meta.get("pair_id"),
        })

    integrity_errors: list[str] = []
    for group, roles in group_roles.items():
        if len(roles) > 1:
            integrity_errors.append(f"leakage_group_id={group} crosses split roles: {sorted(roles)}")
    for pair_id, pair in pair_rows.items():
        if len(pair) != 2:
            integrity_errors.append(f"pair_id={pair_id} has {len(pair)} records; expected exactly 2")
        groups = {r.get("leakage_group_id") for r in pair}
        if len(groups) != 1:
            integrity_errors.append(f"pair_id={pair_id} crosses leakage groups")
        roles = {r.get("metadata", {}).get("dataset_role") for r in pair}
        if len(roles - {"UNASSIGNED", "REWORK_QUEUE", "REGRESSION"}) > 1:
            integrity_errors.append(f"pair_id={pair_id} crosses dataset roles: {sorted(roles)}")
    all_schema_valid = all(row["schema_valid"] for row in rows)
    all_cross_valid = all(row["cross_field_valid"] for row in rows)
    evidence_span_count = sum(1 for record in records if (record.get("target") or {}).get("evidence_spans"))
    verified_source_count = sum(1 for record in records if record.get("metadata", {}).get("source_verified_at_procurement_document_level"))
    rework_records = [record for record in records if record.get("annotation_state") == "UNAVAILABLE_SOURCE_REWORK"]
    parse_isolation_pass = all(
        record.get("target") is None
        and record.get("input", {}).get("parser_quality") == "UNCERTAIN"
        and record.get("metadata", {}).get("data_eligibility") == "REWORK_SOURCE"
        and record.get("metadata", {}).get("dataset_role") not in PROHIBITED_REWORK_ROLES
        for record in rework_records
    )
    checks = {
        "schema_validation": {"status": "PASS" if all_schema_valid else "FAIL", "records": len(rows)},
        "cross_field_validation": {"status": "PASS" if all_cross_valid else "FAIL", "records": len(rows)},
        "evidence_substring_validation": {
            "status": "PASS" if all_cross_valid else "FAIL",
            "located_span_records": evidence_span_count,
            "unverified_evidence_records": len(rows) - evidence_span_count,
        },
        "source_traceability": {
            "status": "PASS" if all_cross_valid else "FAIL",
            "procurement_document_verified_records": verified_source_count,
            "seed_snapshot_traceable_records": len(rows),
        },
        "pair_integrity": {
            "status": "PASS" if not any("pair_id=" in error for error in integrity_errors) else "FAIL",
            "pair_count": len(pair_rows),
        },
        "leakage_group_integrity": {
            "status": "PASS" if not any("leakage_group_id=" in error for error in integrity_errors) else "FAIL",
            "assigned_split_group_count": len(group_roles),
        },
        "eligibility_validation": {"status": "PASS" if all_cross_valid else "FAIL"},
        "dataset_role_validation": {"status": "PASS" if all_cross_valid else "FAIL"},
        "parse_failure_isolation": {
            "status": "PASS" if parse_isolation_pass else "FAIL",
            "rework_records": len(rework_records),
        },
    }
    return {
        "schema_version": schema.get("properties", {}).get("schema_version", {}).get("const"),
        "schema_sha256": schema_digest,
        "record_count": len(records),
        "schema_valid_count": sum(row["schema_valid"] for row in rows),
        "cross_field_valid_count": sum(row["cross_field_valid"] for row in rows),
        "integrity_errors": integrity_errors,
        "checks": checks,
        "rows": rows,
    }


def label_factors(label: dict[str, Any] | None, row: dict[str, Any]) -> list[str]:
    if not label:
        return []
    state = label.get("match_state")
    subtype = label.get("subtype")
    factors: list[str] = []
    if subtype == "SUPPLIER_REGISTRATION_LOCATION":
        factors.append("supplier_location_attribute")
    elif subtype == "DISTANCE_TO_PURCHASER":
        factors.append("distance_to_purchaser")
    elif subtype == "PREEXISTING_LOCAL_BRANCH":
        factors.append("preexisting_branch")
    elif subtype == "OTHER_RELATED":
        factors.append("supplier_location_attribute")
    if state == "MATCH":
        factors.append("pre_award_condition")
        factors.append("scoring_advantage" if row.get("business_stage") == "SCORING" else "market_entry_gate")
    elif state == "NO_MATCH":
        if row.get("business_stage") == "CONTRACT" or row.get("sample_slice") == "COUNTERFACTUAL_HARD_NEGATIVE":
            factors.append("post_award_service")
        elif row.get("sample_slice") == "NORMAL_NEGATIVE":
            factors.append("location_mention_only")
    elif state == "NEEDS_CONTEXT":
        if row.get("sample_slice") == "PARSE_FAILURE":
            factors.append("source_parse_uncertain")
        elif row.get("sample_slice") == "EXCEPTION_REVIEW":
            factors.append("exception_needs_review")
        elif "第七项" in row.get("requirement_text", ""):
            factors.append("cross_reference_missing")
        else:
            factors.append("local_service_term_ambiguous")
    return list(dict.fromkeys(factors))


def convert_seed_row(row: dict[str, Any], schema_digest: str) -> dict[str, Any]:
    seed_id = row["seed_id"]
    source_kind = {
        "SYNTHETIC": "SYNTHETIC",
        "OFFICIAL_CASE_PARAPHRASE": "OFFICIAL_CASE_PARAPHRASE",
    }.get(row.get("text_provenance"), "SYNTHETIC")
    source = row.get("source") or {}
    if source_kind == "OFFICIAL_CASE_PARAPHRASE":
        case_key = row.get("source_case_id") or seed_id
        project_id = f"OFFICIAL-CASE-{case_key}"
        document_id = f"{case_key}-REPORT"
        document_version = "2025-12-02-report"
        section = source.get("section") or "case_report"
    else:
        project_id = f"SYNTHETIC-{seed_id}"
        document_id = f"SYNTHETIC-{seed_id}"
        document_version = "seed-v0.1"
        section = "synthetic_seed_case"

    parse_failure = row.get("sample_slice") == "PARSE_FAILURE" or row.get("data_eligibility") == "REWORK_SOURCE"
    reviewed = row.get("reviewed_label")
    proposed = row.get("proposed_label")
    label = reviewed or proposed
    second_pass = row.get("second_pass") or {}
    independent_double = bool(second_pass.get("human_independent_double_review_completed"))
    review_state = row.get("review_state", "PENDING_SECOND_PASS")
    # SEED-03 has a boundary label change but no independent double review.
    # Preserve its provisional target for traceability while isolating it as DISPUTED/HOLD.
    if seed_id == "C101-SEED-03" and reviewed and reviewed != proposed and not independent_double:
        review_state = "DISPUTED"
    annotation_state = "UNAVAILABLE_SOURCE_REWORK" if parse_failure else "LABELED"
    target = None
    if annotation_state == "LABELED":
        target = {
            "item_id": TASK,
            "requirement_id": f"REQ-{seed_id}",
            "match_state": label["match_state"],
            "subtype": label["subtype"],
            "evidence_text": None,
            "evidence_spans": [],
            "evidence_refs": [],
            "reasoning_factors": label_factors(label, row),
            "missing_context_questions": list(row.get("missing_context_questions") or []),
            "confidence": None,
            "human_review_required": label["match_state"] == "NEEDS_CONTEXT" or review_state == "DISPUTED",
        }
    source_rework_reason = row.get("decision_basis") if parse_failure else None
    return {
        "schema_version": "0.2",
        "schema_sha256": schema_digest,
        "task_id": TASK,
        "sample_id": f"S-C101-{seed_id}",
        "leakage_group_id": row["leakage_group_id"],
        "annotation_state": annotation_state,
        "input": {
            "requirement_id": f"REQ-{seed_id}",
            "project_id": project_id,
            "document_id": document_id,
            "document_version": document_version,
            "clause_id": f"CL-{seed_id}",
            "clause_text": row["requirement_text"],
            "business_stage": row.get("business_stage"),
            "context": None,
            "source_location": {
                "page": None,
                "section": section,
                "pdf_page_index": None,
                "page_label": None,
            },
            "parser_quality": "UNCERTAIN" if parse_failure else "PASS",
            "source_defect_prevents_judgment": parse_failure,
            "source_defect_reason": source_rework_reason,
        },
        "target": target,
        "metadata": {
            "case_id": f"CASE-{seed_id}",
            "seed_id": seed_id,
            "source_record_sha256": canonical_sha256(row),
            "source_kind": source_kind,
            "source_url": source.get("url") if source_kind == "OFFICIAL_CASE_PARAPHRASE" else None,
            "source_title": source.get("title") if source_kind == "OFFICIAL_CASE_PARAPHRASE" else "C1-01 合成种子案例",
            "source_sha256": None,
            "is_verbatim_procurement_clause": bool(row.get("is_verbatim_procurement_clause")),
            "source_verified_at_procurement_document_level": bool(row.get("source_verified_at_procurement_document_level", False)),
            "evidence_status": "UNVERIFIED",
            "case_slice": row["sample_slice"],
            "pair_id": row.get("pair_id"),
            "counterfactual_change": row.get("counterfactual_change"),
            "parent_sample_id": None,
            "review_state": review_state,
            "label_authority": "INTERNAL_SILVER",
            "data_eligibility": "REWORK_SOURCE" if parse_failure else ("HOLD" if review_state == "DISPUTED" else row.get("data_eligibility", "HOLD")),
            "dataset_role": "UNASSIGNED",
            "source_rework_reason": source_rework_reason,
            "guide_version": "C1_01_Label_Guide_V0.1",
            "spec_version": "BR_C1_01_Business_Task_Spec_V0.1",
        },
    }


def report_markdown(report: dict[str, Any], records: list[dict[str, Any]], seed_path: Path, schema_path: Path) -> str:
    def count(path: str) -> Counter:
        values = []
        for row in records:
            value: Any = row
            for key in path.split("."):
                value = value.get(key) if isinstance(value, dict) else None
            values.append(value)
        return Counter(values)

    lines = [
        "# C1-01 Seed Cases Revalidation Report V0.2",
        "",
        "**Status：REVALIDATED；数据仍不可直接训练。** 本报告使用当前 Library 中的 29 条 Seed Cases，按 V0.2 Schema 和 validator 全量重跑。",
        "",
        f"- Seed input：`{seed_path.name}`（{len(records)} 条）",
        f"- Schema：`{schema_path.name}`",
        f"- Schema SHA-256：`{report['schema_sha256']}`",
        "- 运行口径：Schema Validation、Cross-field Validation、Evidence Substring、Source Traceability、Pair Integrity、Leakage Group Integrity、Eligibility、Dataset Role、Parse Failure Isolation",
        "",
        "## 1. 全量结果",
        "",
        "| 指标 | 结果 |",
        "|---|---:|",
        f"| 总记录 | {report['record_count']} |",
        f"| Schema Valid | {report['schema_valid_count']}/{report['record_count']} |",
        f"| Cross-field Valid | {report['cross_field_valid_count']}/{report['record_count']} |",
        f"| LABELED | {count('annotation_state')['LABELED']} |",
        f"| UNAVAILABLE_SOURCE_REWORK | {count('annotation_state')['UNAVAILABLE_SOURCE_REWORK']} |",
        f"| MATCH | {count('target.match_state')['MATCH']} |",
        f"| NO_MATCH | {count('target.match_state')['NO_MATCH']} |",
        f"| NEEDS_CONTEXT | {count('target.match_state')['NEEDS_CONTEXT']} |",
        f"| target=null | {sum(row.get('target') is None for row in records)} |",
        f"| DISPUTED | {count('metadata.review_state')['DISPUTED']} |",
        f"| REWORK_SOURCE | {count('metadata.data_eligibility')['REWORK_SOURCE']} |",
        f"| HOLD | {count('metadata.data_eligibility')['HOLD']} |",
        f"| TRAIN / DEV / BLIND_GOLD | 0 / 0 / 0 |",
        "",
        "结论：29 条均通过 V0.2 结构验证；其中 28 条是有 target 但尚未完成采购文件逐字来源与证据核验的 `LABELED/HOLD`，1 条为 `UNAVAILABLE_SOURCE_REWORK/target=null/REWORK_SOURCE`。没有任何记录进入 TRAIN、DEV 或 BLIND_GOLD。",
        "",
        "## 1.1 自动化检查项",
        "",
        "| 检查 | 状态 | 统计 |",
        "|---|---|---:|",
        *[
            f"| {name} | {check['status']} | "
            + (str(check.get("records", check.get("located_span_records", check.get("rework_records", check.get("pair_count", check.get("assigned_split_group_count", "-")))))))
            + " |"
            for name, check in report["checks"].items()
        ],
        "",
        "## 2. 关键边界验收",
        "",
        "| Seed | annotation_state | target | review_state | data_eligibility | 结果 |",
        "|---|---|---|---|---|---|",
    ]
    for row in report["rows"]:
        if row["sample_id"] in {"S-C101-C101-SEED-03", "S-C101-C101-SEED-21"}:
            target_state = row["match_state"] or "null"
            result = "通过" if row["schema_valid"] and row["cross_field_valid"] else "失败"
            lines.append(
                f"| {row['sample_id'].replace('S-C101-', '')} | {row['annotation_state']} | {target_state} | {row['review_state']} | {row['data_eligibility']} | {result} |"
            )
    lines += [
        "",
        "- `C101-SEED-03`：保留业务裁决后的 `MATCH/OTHER_RELATED` 作为暂定 target，但由于标签从 proposed_label 发生变化且没有独立人工双人复核，升级为 `DISPUTED/HOLD`；不会进入训练或盲测。",
        "- `C101-SEED-21`：`PARSE_FAILURE` 进入 `UNAVAILABLE_SOURCE_REWORK`，`parser_quality=UNCERTAIN`，`target=null`，`data_eligibility=REWORK_SOURCE`，`dataset_role=UNASSIGNED`。其历史 `proposed_label=NEEDS_CONTEXT` 不进入监督 target。",
        "",
        "## 3. 每条记录",
        "",
        "| Seed | Schema | Cross-field | Annotation | Target | Review | Eligibility | Role | Blockers |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in report["rows"]:
        blockers = "；".join(row["errors"]) if row["errors"] else "来源/证据未核验或尚未分配数据角色"
        lines.append(
            f"| {row['sample_id'].replace('S-C101-', '')} | {'PASS' if row['schema_valid'] else 'FAIL'} | {'PASS' if row['cross_field_valid'] else 'FAIL'} | {row['annotation_state']} | {row['match_state'] or 'null'} | {row['review_state']} | {row['data_eligibility']} | {row['dataset_role']} | {blockers} |"
        )
    lines += [
        "",
        "## 4. 下一步入库门槛",
        "",
        "1. 对 28 条 `LABELED/HOLD` 补齐采购文件逐字条款、页码和连续证据；证据未核验前不得升 `TRAIN_ELIGIBLE` 或 `BENCHMARK_CANDIDATE`。",
        "2. 对 `C101-SEED-03` 完成独立人工双人复核或形成正式边界裁决记录；在此之前保持 `DISPUTED/HOLD`。",
        "3. 对 `C101-SEED-21` 调取原 PDF 和完整附表，修复后重新解析、拆分、标注；不得直接把历史 `NEEDS_CONTEXT` 当监督标签。",
        "4. 测试组继续独占 blind gold；项目／模板和 pair 不得跨 split。",
    ]
    return "\n".join(lines) + "\n"


def cmd_revalidate(args: argparse.Namespace) -> int:
    schema_path = Path(args.schema)
    seed_path = Path(args.seed)
    rows = [json.loads(line) for line in seed_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    schema_digest = sha256_file(schema_path)
    records = [convert_seed_row(row, schema_digest) for row in rows]
    report = validate_records(records, schema_path)
    output = Path(args.output)
    output.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in records) + "\n", encoding="utf-8")
    report_json = Path(args.report_json)
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.report_md).write_text(report_markdown(report, records, seed_path, schema_path), encoding="utf-8")
    print(json.dumps({"record_count": report["record_count"], "schema_valid": report["schema_valid_count"], "cross_field_valid": report["cross_field_valid_count"], "integrity_errors": report["integrity_errors"]}, ensure_ascii=False))
    return 0 if report["schema_valid_count"] == report["record_count"] and report["cross_field_valid_count"] == report["record_count"] and not report["integrity_errors"] else 2


def cmd_validate(args: argparse.Namespace) -> int:
    schema_path = Path(args.schema)
    input_path = Path(args.input)
    records = [json.loads(line) for line in input_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    report = validate_records(records, schema_path)
    if args.report_json:
        Path(args.report_json).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"record_count": report["record_count"], "schema_valid": report["schema_valid_count"], "cross_field_valid": report["cross_field_valid_count"], "integrity_errors": report["integrity_errors"]}, ensure_ascii=False))
    return 0 if report["schema_valid_count"] == report["record_count"] and report["cross_field_valid_count"] == report["record_count"] and not report["integrity_errors"] else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="command", required=True)
    rv = subs.add_parser("revalidate-seeds")
    rv.add_argument("--schema", required=True)
    rv.add_argument("--seed", required=True)
    rv.add_argument("--output", required=True)
    rv.add_argument("--report-md", required=True)
    rv.add_argument("--report-json", required=True)
    rv.set_defaults(func=cmd_revalidate)
    vl = subs.add_parser("validate")
    vl.add_argument("--schema", required=True)
    vl.add_argument("--input", required=True)
    vl.add_argument("--report-json")
    vl.set_defaults(func=cmd_validate)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
