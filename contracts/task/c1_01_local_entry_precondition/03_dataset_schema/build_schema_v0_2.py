#!/usr/bin/env python3
"""Build the incompatible V0.2 Dataset Schema without overwriting V0.1."""
import json
from pathlib import Path

TASK = "C1-01_LOCAL_ENTRY_PRECONDITION"
OUT = Path(__file__).with_name("C1_01_Dataset_Schema_V0.2.json")

STATES = ["MATCH", "NO_MATCH", "NEEDS_CONTEXT"]
SUBTYPES = [
    "SUPPLIER_REGISTRATION_LOCATION",
    "DISTANCE_TO_PURCHASER",
    "PREEXISTING_LOCAL_BRANCH",
    "OTHER_RELATED",
    "NONE",
]
FACTORS = [
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
]
SLICES = [
    "OFFICIAL_ANCHOR_POSITIVE",
    "OFFICIAL_ANCHOR_HARD_NEGATIVE",
    "OFFICIAL_ANCHOR_HARD_POSITIVE",
    "OFFICIAL_ANCHOR_OTHER_ITEM",
    "TYPICAL_POSITIVE",
    "HARD_POSITIVE",
    "NORMAL_NEGATIVE",
    "HARD_NEGATIVE",
    "OTHER_ITEM_NEGATIVE",
    "MISSING_CONTEXT",
    "PARSE_FAILURE",
    "EXCEPTION_REVIEW",
    "COUNTERFACTUAL_POSITIVE",
    "COUNTERFACTUAL_HARD_NEGATIVE",
]


def obj(required, properties):
    return {
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": properties,
    }


string = {"type": "string", "minLength": 1}
nullable_string = {"type": ["string", "null"]}
nullable_page = {"type": ["integer", "null"], "minimum": 1}
stage = {"enum": ["QUALIFICATION", "SCORING", "TECHNICAL", "CONTRACT", None]}

location = obj(
    ["page", "section"],
    {
        "page": nullable_page,
        "section": string,
        "pdf_page_index": {"type": ["integer", "null"], "minimum": 0},
        "page_label": nullable_string,
    },
)
ref = obj(
    ["document_id", "document_version", "page", "section"],
    {
        "document_id": string,
        "document_version": string,
        "page": nullable_page,
        "section": string,
    },
)
span = obj(
    [
        "text",
        "anchor",
        "context_id",
        "document_id",
        "document_version",
        "page",
        "section",
        "start_char",
        "end_char",
    ],
    {
        "text": string,
        "anchor": {"enum": ["CLAUSE", "CONTEXT"]},
        "context_id": nullable_string,
        "document_id": string,
        "document_version": string,
        "page": nullable_page,
        "section": string,
        "start_char": {"type": "integer", "minimum": 0},
        "end_char": {"type": "integer", "minimum": 1},
    },
)
context_item = obj(
    ["context_id", "text", "document_id", "document_version", "source_location"],
    {
        "context_id": string,
        "text": string,
        "document_id": string,
        "document_version": string,
        "source_location": location,
    },
)

target = obj(
    [
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
    ],
    {
        "item_id": {"const": TASK},
        "requirement_id": string,
        "match_state": {"enum": STATES},
        "subtype": {"enum": SUBTYPES},
        "evidence_text": {"oneOf": [{"type": "null"}, string]},
        "evidence_spans": {"type": "array", "items": span},
        "evidence_refs": {"type": "array", "items": ref},
        "reasoning_factors": {
            "type": "array",
            "uniqueItems": True,
            "items": {"enum": FACTORS},
        },
        "missing_context_questions": {
            "type": "array",
            "uniqueItems": True,
            "items": string,
        },
        "confidence": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        "human_review_required": {"type": "boolean"},
    },
)

input_obj = obj(
    [
        "requirement_id",
        "project_id",
        "document_id",
        "document_version",
        "clause_id",
        "clause_text",
        "business_stage",
        "context",
        "source_location",
        "parser_quality",
        "source_defect_prevents_judgment",
        "source_defect_reason",
    ],
    {
        "requirement_id": string,
        "project_id": string,
        "document_id": string,
        "document_version": string,
        "clause_id": string,
        "clause_text": string,
        "business_stage": stage,
        "context": {
            "oneOf": [
                {"type": "null"},
                {"type": "array", "minItems": 1, "items": context_item},
            ]
        },
        "source_location": location,
        "parser_quality": {"enum": ["PASS", "UNCERTAIN"]},
        "source_defect_prevents_judgment": {"type": "boolean"},
        "source_defect_reason": nullable_string,
    },
)

metadata = obj(
    [
        "case_id",
        "seed_id",
        "source_record_sha256",
        "source_kind",
        "source_url",
        "source_title",
        "source_sha256",
        "is_verbatim_procurement_clause",
        "source_verified_at_procurement_document_level",
        "evidence_status",
        "case_slice",
        "pair_id",
        "counterfactual_change",
        "parent_sample_id",
        "review_state",
        "label_authority",
        "data_eligibility",
        "dataset_role",
        "source_rework_reason",
        "guide_version",
        "spec_version",
    ],
    {
        "case_id": string,
        "seed_id": nullable_string,
        "source_record_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
        "source_kind": {
            "enum": ["PROCUREMENT_DOCUMENT", "OFFICIAL_CASE_PARAPHRASE", "SYNTHETIC"]
        },
        "source_url": {
            "oneOf": [
                {"type": "null"},
                {"type": "string", "format": "uri", "pattern": "^https://"},
            ]
        },
        "source_title": nullable_string,
        "source_sha256": {
            "oneOf": [
                {"type": "null"},
                {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            ]
        },
        "is_verbatim_procurement_clause": {"type": "boolean"},
        "source_verified_at_procurement_document_level": {"type": "boolean"},
        "evidence_status": {"enum": ["UNVERIFIED", "VERIFIED"]},
        "case_slice": {"enum": SLICES},
        "pair_id": nullable_string,
        "counterfactual_change": nullable_string,
        "parent_sample_id": nullable_string,
        "review_state": {
            "enum": ["PENDING_SECOND_PASS", "DISPUTED", "INTERNAL_REVIEWED"]
        },
        "label_authority": {"const": "INTERNAL_SILVER"},
        "data_eligibility": {
            "enum": [
                "HOLD",
                "REWORK_SOURCE",
                "PENDING_DATA_QA",
                "TRAIN_ELIGIBLE",
                "BENCHMARK_CANDIDATE",
            ]
        },
        "dataset_role": {
            "enum": [
                "UNASSIGNED",
                "REWORK_QUEUE",
                "TRAIN",
                "DEV",
                "BLIND_INPUT",
                "BLIND_GOLD",
                "REGRESSION",
            ]
        },
        "source_rework_reason": nullable_string,
        "guide_version": {"const": "C1_01_Label_Guide_V0.1"},
        "spec_version": {"const": "BR_C1_01_Business_Task_Spec_V0.1"},
    },
)

schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:procurementlm:c1-01:dataset-schema:0.2",
    "title": "C1-01 Requirement dataset contract, Dataset Schema V0.2",
    "description": (
        "Breaking change from V0.1. One row is one Requirement. "
        "LABELED rows have a target; UNAVAILABLE_SOURCE_REWORK rows have target=null. "
        "Cross-record checks and exact evidence/source checks live in validate_sample.py."
    ),
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "schema_sha256",
        "task_id",
        "sample_id",
        "leakage_group_id",
        "annotation_state",
        "input",
        "target",
        "metadata",
    ],
    "properties": {
        "schema_version": {"const": "0.2"},
        "schema_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
        "task_id": {"const": TASK},
        "sample_id": {"type": "string", "pattern": "^S-C101-[A-Za-z0-9._-]+$"},
        "leakage_group_id": string,
        "annotation_state": {
            "enum": ["LABELED", "UNAVAILABLE_SOURCE_REWORK"]
        },
        "input": input_obj,
        "target": {"oneOf": [target, {"type": "null"}]},
        "metadata": metadata,
    },
    "allOf": [
        {
            "if": {"properties": {"annotation_state": {"const": "LABELED"}}},
            "then": {
                "properties": {
                    "input": {
                        "properties": {
                            "parser_quality": {"const": "PASS"},
                            "source_defect_prevents_judgment": {"const": False},
                            "source_defect_reason": {"const": None},
                        }
                    },
                    "target": {"not": {"type": "null"}},
                }
            },
        },
        {
            "if": {
                "properties": {
                    "annotation_state": {"const": "UNAVAILABLE_SOURCE_REWORK"}
                }
            },
            "then": {
                "properties": {
                    "target": {"const": None},
                    "input": {
                        "properties": {
                            "parser_quality": {"const": "UNCERTAIN"},
                            "source_defect_prevents_judgment": {"const": True},
                            "source_defect_reason": {"type": "string", "minLength": 1},
                        }
                    },
                    "metadata": {
                        "properties": {
                            "data_eligibility": {"const": "REWORK_SOURCE"},
                            "dataset_role": {"enum": ["UNASSIGNED", "REWORK_QUEUE"]},
                            "source_rework_reason": {"type": "string", "minLength": 1},
                        }
                    },
                }
            },
        },
        {
            "if": {
                "properties": {
                    "input": {
                        "properties": {
                            "source_defect_prevents_judgment": {"const": True}
                        }
                    }
                }
            },
            "then": {
                "properties": {
                    "annotation_state": {"const": "UNAVAILABLE_SOURCE_REWORK"},
                    "input": {"properties": {"parser_quality": {"const": "UNCERTAIN"}}},
                    "metadata": {"properties": {"data_eligibility": {"enum": ["REWORK_SOURCE", "HOLD"]}}},
                }
            },
        },
        {
            "if": {
                "properties": {
                    "input": {"properties": {"parser_quality": {"const": "UNCERTAIN"}}}
                }
            },
            "then": {
                "properties": {
                    "annotation_state": {"const": "UNAVAILABLE_SOURCE_REWORK"},
                    "input": {"properties": {"source_defect_prevents_judgment": {"const": True}}},
                }
            },
        },
        {
            "if": {
                "properties": {
                    "metadata": {"properties": {"review_state": {"const": "DISPUTED"}}}
                }
            },
            "then": {
                "properties": {
                    "metadata": {"properties": {"data_eligibility": {"const": "HOLD"}}},
                    "target": {"oneOf": [{"type": "null"}, {"properties": {"human_review_required": {"const": True}}}]},
                }
            },
        },
        {
            "if": {
                "properties": {
                    "metadata": {"properties": {"data_eligibility": {"const": "REWORK_SOURCE"}}}
                }
            },
            "then": {
                "properties": {
                    "annotation_state": {"const": "UNAVAILABLE_SOURCE_REWORK"},
                    "target": {"const": None},
                }
            },
        },
        {
            "if": {
                "properties": {
                    "metadata": {
                        "properties": {
                            "data_eligibility": {"enum": ["TRAIN_ELIGIBLE", "BENCHMARK_CANDIDATE"]}
                        }
                    }
                }
            },
            "then": {
                "properties": {
                    "annotation_state": {"const": "LABELED"},
                    "target": {"not": {"type": "null"}},
                    "input": {
                        "properties": {
                            "parser_quality": {"const": "PASS"},
                            "source_defect_prevents_judgment": {"const": False},
                        }
                    },
                    "metadata": {
                        "properties": {
                            "source_kind": {"const": "PROCUREMENT_DOCUMENT"},
                            "source_verified_at_procurement_document_level": {"const": True},
                            "evidence_status": {"const": "VERIFIED"},
                            "review_state": {"const": "INTERNAL_REVIEWED"},
                        }
                    },
                }
            },
        },
        {
            "if": {
                "properties": {
                    "metadata": {"properties": {"source_kind": {"enum": ["SYNTHETIC", "OFFICIAL_CASE_PARAPHRASE"]}}}
                }
            },
            "then": {
                "properties": {
                    "metadata": {
                        "properties": {
                            "source_verified_at_procurement_document_level": {"const": False},
                            "is_verbatim_procurement_clause": {"const": False},
                            "source_sha256": {"const": None},
                            "data_eligibility": {"enum": ["HOLD", "PENDING_DATA_QA", "REWORK_SOURCE"]},
                        }
                    }
                }
            },
        },
        {
            "if": {
                "properties": {
                    "metadata": {"properties": {"dataset_role": {"enum": ["TRAIN", "DEV"]}}}
                }
            },
            "then": {"properties": {"metadata": {"properties": {"data_eligibility": {"const": "TRAIN_ELIGIBLE"}}}}},
        },
        {
            "if": {
                "properties": {
                    "metadata": {"properties": {"dataset_role": {"const": "BLIND_GOLD"}}}
                }
            },
            "then": {"properties": {"metadata": {"properties": {"data_eligibility": {"const": "BENCHMARK_CANDIDATE"}}}}},
        },
        {
            "if": {
                "properties": {
                    "metadata": {"properties": {"dataset_role": {"const": "REWORK_QUEUE"}}}
                }
            },
            "then": {"properties": {"metadata": {"properties": {"data_eligibility": {"const": "REWORK_SOURCE"}}}}},
        },
        {
            "if": {"properties": {"target": {"properties": {"match_state": {"const": "MATCH"}}}}},
            "then": {
                "properties": {
                    "target": {
                        "properties": {
                            "subtype": {"enum": SUBTYPES[:-1]},
                            "missing_context_questions": {"maxItems": 0},
                        }
                    }
                }
            },
        },
        {
            "if": {"properties": {"target": {"properties": {"match_state": {"const": "NO_MATCH"}}}}},
            "then": {
                "properties": {
                    "target": {
                        "properties": {
                            "subtype": {"const": "NONE"},
                            "missing_context_questions": {"maxItems": 0},
                        }
                    }
                }
            },
        },
        {
            "if": {"properties": {"target": {"properties": {"match_state": {"const": "NEEDS_CONTEXT"}}}}},
            "then": {
                "properties": {
                    "target": {
                        "properties": {
                            "subtype": {"const": "NONE"},
                            "missing_context_questions": {"minItems": 1},
                            "human_review_required": {"const": True},
                        }
                    }
                }
            },
        },
        {
            "if": {
                "properties": {
                    "metadata": {"properties": {"case_slice": {"const": "PARSE_FAILURE"}}}
                }
            },
            "then": {
                "properties": {
                    "annotation_state": {"const": "UNAVAILABLE_SOURCE_REWORK"},
                    "input": {"properties": {"parser_quality": {"const": "UNCERTAIN"}}},
                    "target": {"const": None},
                }
            },
        },
    ],
}

OUT.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(OUT)
