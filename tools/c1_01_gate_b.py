#!/usr/bin/env python3
"""Build the smallest reproducible C1-01 Gate-B data snapshot.

The script turns source-catalog/intake records into V0.2 Internal Silver
records. It never upgrades HOLD records and never writes blind-test gold.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


TASK = "C1-01_LOCAL_ENTRY_PRECONDITION"
SCHEMA_VERSION = "0.2"
GUIDE_VERSION = "C1_01_Label_Guide_V0.1"
SPEC_VERSION = "BR_C1_01_Business_Task_Spec_V0.1"
BUILD_TIMESTAMP = "2026-09-22T15:52:06Z"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def locator(intake: dict[str, Any]) -> dict[str, Any]:
    return {"page": intake["page"], "page_label": str(intake["page"]), "pdf_page_index": intake["page"] - 1, "section": intake["section"]}


def build_record(intake: dict[str, Any], source: dict[str, Any], schema_sha256: str) -> dict[str, Any]:
    requirement_id = f"REQ-{intake['intake_id'].removeprefix('INT-')}"
    location = locator(intake)
    text = intake["clause_text"]
    evidence_span = {
        "text": text,
        "anchor": "CLAUSE",
        "context_id": None,
        "document_id": intake["document_id"],
        "document_version": intake["document_version"],
        "page": intake["page"],
        "section": intake["section"],
        "start_char": 0,
        "end_char": len(text),
    }
    evidence_ref = {
        "document_id": intake["document_id"],
        "document_version": intake["document_version"],
        "page": intake["page"],
        "section": intake["section"],
    }
    label = intake["candidate_label"]
    target = {
        "item_id": TASK,
        "requirement_id": requirement_id,
        "match_state": label["match_state"],
        "subtype": label["subtype"],
        "evidence_text": text,
        "evidence_spans": [evidence_span],
        "evidence_refs": [evidence_ref],
        "reasoning_factors": ["post_award_service" if intake["business_stage"] == "CONTRACT" else "location_mention_only"],
        "missing_context_questions": [],
        "confidence": None,
        "human_review_required": True,
    }
    return {
        "annotation_state": "LABELED",
        "input": {
            "business_stage": intake["business_stage"],
            "clause_id": intake["clause_id"],
            "clause_text": text,
            "context": None,
            "document_id": intake["document_id"],
            "document_version": intake["document_version"],
            "parser_quality": "PASS",
            "project_id": source["procurement_project_id"],
            "requirement_id": requirement_id,
            "source_defect_prevents_judgment": False,
            "source_defect_reason": None,
            "source_location": location,
        },
        "leakage_group_id": f"LG-{source['procurement_project_id']}",
        "metadata": {
            "case_id": intake["intake_id"],
            "case_slice": intake["case_slice"],
            "counterfactual_change": None,
            "data_eligibility": "HOLD",
            "dataset_role": "UNASSIGNED",
            "evidence_status": "VERIFIED",
            "guide_version": GUIDE_VERSION,
            "is_verbatim_procurement_clause": True,
            "label_authority": "INTERNAL_SILVER",
            "pair_id": None,
            "parent_sample_id": None,
            "review_state": intake["review_state"],
            "seed_id": intake["intake_id"],
            "source_kind": "PROCUREMENT_DOCUMENT",
            "source_record_sha256": canonical_sha256(source),
            "source_rework_reason": None,
            "source_sha256": source["document_sha256"],
            "source_title": source["title"],
            "source_url": source["source_url"].split("?", 1)[0],
            "source_verified_at_procurement_document_level": True,
            "spec_version": SPEC_VERSION,
        },
        "sample_id": f"S-{intake['intake_id'].removeprefix('INT-')}",
        "schema_sha256": schema_sha256,
        "schema_version": SCHEMA_VERSION,
        "target": target,
        "task_id": TASK,
    }


def split_eligible(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["metadata"]["data_eligibility"] == "TRAIN_ELIGIBLE":
            groups[row["input"]["project_id"] + "|" + row["leakage_group_id"]].append(row)
    ordered_groups = sorted(groups.items(), key=lambda item: item[0])
    train_groups = {key for index, (key, _) in enumerate(ordered_groups) if index < max(1, round(len(ordered_groups) * 0.8))}
    train = [row for key, group in ordered_groups if key in train_groups for row in group]
    dev = [row for key, group in ordered_groups if key not in train_groups for row in group]
    return train, dev


def readiness(rows: list[dict[str, Any]], train: list[dict[str, Any]], dev: list[dict[str, Any]]) -> dict[str, Any]:
    eligibility = Counter(row["metadata"]["data_eligibility"] for row in rows)
    reviews = Counter(row["metadata"]["review_state"] for row in rows)
    return {
        "status": "PILOT_NOT_READY",
        "contract": "C1-01_LOCAL_ENTRY_PRECONDITION",
        "schema_version": SCHEMA_VERSION,
        "internal_silver_candidate_count": len(rows),
        "train_count": len(train),
        "dev_count": len(dev),
        "target": {"train_range": [300, 500], "dev_range": [80, 100]},
        "readiness_gap": {"train_shortfall_to_minimum": max(0, 300 - len(train)), "dev_shortfall_to_minimum": max(0, 80 - len(dev))},
        "eligibility_counts": dict(sorted(eligibility.items())),
        "review_state_counts": dict(sorted(reviews.items())),
        "blocked_reasons": [
            "PENDING_SECOND_PASS records require independent human double review.",
            "HOLD records are not eligible for TRAIN or DEV.",
            "Pilot has one public source and three clauses; source coverage is not representative.",
        ],
        "blind_gold_accessed": False,
        "teacher_external_transfer": False,
    }


def statistics(rows: list[dict[str, Any]], train: list[dict[str, Any]], dev: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "record_count": len(rows),
        "train_count": len(train),
        "dev_count": len(dev),
        "match_state_counts": dict(sorted(Counter(row["target"]["match_state"] for row in rows).items())),
        "source_kind_counts": dict(sorted(Counter(row["metadata"]["source_kind"] for row in rows).items())),
        "eligibility_counts": dict(sorted(Counter(row["metadata"]["data_eligibility"] for row in rows).items())),
        "review_state_counts": dict(sorted(Counter(row["metadata"]["review_state"] for row in rows).items())),
        "evidence_verified_count": sum(row["metadata"]["evidence_status"] == "VERIFIED" for row in rows),
        "source_document_verified_count": sum(row["metadata"]["source_verified_at_procurement_document_level"] for row in rows),
    }


def source_coverage(catalog_rows: list[dict[str, Any]], intake_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_source = Counter(row["source_id"] for row in intake_rows)
    return {
        "source_count": len(catalog_rows),
        "verified_source_count": sum(row["verification_status"] == "VERIFIED" for row in catalog_rows),
        "intake_clause_count": len(intake_rows),
        "source_clause_counts": dict(sorted(by_source.items())),
        "pages_covered": sorted({row["page"] for row in intake_rows}),
        "coverage_status": "PILOT_ONLY_ONE_PUBLIC_SOURCE",
        "coverage_gap": "Add independent procurement projects and positive local-entry clauses before TRAIN/DEV readiness.",
    }


def leakage_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    duplicate_keys: dict[str, list[str]] = defaultdict(list)
    groups: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        key = f"{row['metadata']['source_sha256']}:{row['input']['source_location']['page']}:{row['input']['clause_text']}"
        duplicate_keys[key].append(row["sample_id"])
        groups[row["leakage_group_id"]].append(row["sample_id"])
    return {
        "duplicate_key_count": sum(1 for sample_ids in duplicate_keys.values() if len(sample_ids) > 1),
        "duplicate_keys": {key: value for key, value in duplicate_keys.items() if len(value) > 1},
        "leakage_group_count": len(groups),
        "leakage_groups": dict(sorted(groups.items())),
        "pair_cross_split_violations": [],
    }


def build(args: argparse.Namespace) -> None:
    catalog_rows = read_jsonl(args.catalog)
    catalog = {row["source_id"]: row for row in catalog_rows}
    intake_rows = read_jsonl(args.intake)
    schema_sha256 = sha256_file(args.schema)
    rows = []
    for intake in intake_rows:
        source = catalog[intake["source_id"]]
        if intake["evidence_status"] != "VERIFIED" or intake["review_state"] != "PENDING_SECOND_PASS":
            raise ValueError(f"intake gate mismatch: {intake['intake_id']}")
        rows.append(build_record(intake, source, schema_sha256))
    train, dev = split_eligible(rows)
    write_jsonl(args.silver, rows)
    write_jsonl(args.train, train)
    write_jsonl(args.dev, dev)
    readiness_report = readiness(rows, train, dev)
    leakage = leakage_report(rows)
    args.readiness.parent.mkdir(parents=True, exist_ok=True)
    args.readiness.write_text(json.dumps(readiness_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.leakage.write_text(json.dumps(leakage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    stats = statistics(rows, train, dev)
    coverage = source_coverage(catalog_rows, intake_rows)
    args.statistics.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.source_coverage.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "manifest_version": "C1_01_GATE_B_DATA_READINESS_V0.1",
        "generated_at": args.generated_at,
        "schema": {"path": str(args.schema), "sha256": schema_sha256, "version": SCHEMA_VERSION},
        "files": {},
        "split_policy": "eligible records only; group by project_id+leakage_group_id before deterministic 80/20 split",
        "access_boundary": {"blind_test_gold": "NOT_READ", "raw_procurement_files": "EXTERNAL_ONLY", "teacher_external_transfer": False},
        "readiness": readiness_report,
        "statistics": {"path": str(args.statistics), "sha256": sha256_file(args.statistics), "bytes": args.statistics.stat().st_size},
        "source_coverage": {"path": str(args.source_coverage), "sha256": sha256_file(args.source_coverage), "bytes": args.source_coverage.stat().st_size},
    }
    for name, path in {
        "source_catalog": args.catalog,
        "case_intake": args.intake,
        "internal_silver": args.silver,
        "train": args.train,
        "dev": args.dev,
        "readiness_report": args.readiness,
        "leakage_report": args.leakage,
        "statistics_report": args.statistics,
        "source_coverage_report": args.source_coverage,
    }.items():
        manifest["files"][name] = {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("build", choices=["build"])
    parser.add_argument("--schema", type=Path, default=root / "contracts/task/c1_01_local_entry_precondition/03_dataset_schema/C1_01_Dataset_Schema_V0.2.json")
    parser.add_argument("--catalog", type=Path, default=root / "datasets/source_catalog/C1_01_Source_Catalog_V0.1.jsonl")
    parser.add_argument("--intake", type=Path, default=root / "datasets/staging/C1_01_Case_Intake_V0.1.jsonl")
    parser.add_argument("--silver", type=Path, default=root / "datasets/curated/C1_01_Internal_Silver_CasePack_V0.1.jsonl")
    parser.add_argument("--train", type=Path, default=root / "datasets/benchmark/train/C1_01_TRAIN_Pilot_V0.1.jsonl")
    parser.add_argument("--dev", type=Path, default=root / "datasets/benchmark/dev/C1_01_DEV_Pilot_V0.1.jsonl")
    parser.add_argument("--readiness", type=Path, default=root / "datasets/reports/C1_01_Gate_B_Readiness_V0.1.json")
    parser.add_argument("--leakage", type=Path, default=root / "datasets/reports/C1_01_Gate_B_Leakage_Report_V0.1.json")
    parser.add_argument("--statistics", type=Path, default=root / "datasets/reports/C1_01_Gate_B_Statistics_V0.1.json")
    parser.add_argument("--source-coverage", type=Path, default=root / "datasets/reports/C1_01_Gate_B_Source_Coverage_V0.1.json")
    parser.add_argument("--manifest", type=Path, default=root / "datasets/manifests/C1_01_Gate_B_Manifest_V0.1.json")
    parser.add_argument("--generated-at", default=BUILD_TIMESTAMP)
    args = parser.parse_args()
    build(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
