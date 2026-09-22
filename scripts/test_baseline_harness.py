"""Small regression check for the frozen C1-01 baseline protocol."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS_PATH = ROOT / "contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/harness.py"
FIXTURE_PATH = ROOT / "contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/fixtures/C1_01_Baseline_Smoke_Input_V0.2.jsonl"


def load_harness():
    spec = importlib.util.spec_from_file_location("c1_01_baseline_harness", HARNESS_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load baseline harness")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    harness = load_harness()
    row = json.loads(FIXTURE_PATH.read_text(encoding="utf-8").splitlines()[0])
    report = harness.preflight_rows([row], "ZERO_SHOT", smoke=True)
    assert report["status"] == "PASS", report

    rework = copy.deepcopy(row)
    rework["target"] = None
    rework["metadata"]["data_eligibility"] = "REWORK_SOURCE"
    errors = harness.validate_dataset_row(rework)
    assert "REWORK_SOURCE is not eligible for model execution" in errors

    bad_rework = copy.deepcopy(rework)
    bad_rework["target"] = row["target"]
    assert "REWORK_SOURCE requires target=null" in harness.validate_dataset_row(bad_rework)

    bad_prediction = copy.deepcopy(row["target"])
    bad_prediction["match_state"] = "MATCH"
    bad_prediction["subtype"] = "NONE"
    assert "MATCH requires a non-NONE subtype" in harness.validate_prediction(bad_prediction, row["input"])
    print("C1-01 baseline harness regression OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
