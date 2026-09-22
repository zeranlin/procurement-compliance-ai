"""Run the canonical C1-01 V0.2.1 contract regression suite."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGRESSION_PATH = ROOT / (
    "contracts/task/c1_01_local_entry_precondition/04_baseline_protocol/"
    "harness/C1_01_Baseline_Harness_V0.2.1/regression_tests.py"
)


def main() -> int:
    return subprocess.run([sys.executable, str(REGRESSION_PATH)], check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
