"""Validate the non-negotiable repository structure."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "docs/architecture",
    "docs/tutorial/README.md",
    "docs/tutorial/COURSE_ALL.md",
    "contracts/common",
    "contracts/task/c1_01_local_entry_precondition",
    "datasets/benchmark/blind_test_gold/README.md",
    "modules/procurement-data",
    "modules/procurement-policy",
    "modules/procurement-rules",
    "modules/procurement-model",
    "modules/procurement-engine",
    "modules/procurement-agent",
    "modules/procurement-benchmark",
    "modules/procurement-platform",
    "scripts/validate_contracts.py",
]


def main() -> int:
    missing = [item for item in REQUIRED if not (ROOT / item).exists()]
    if missing:
        print("Missing required paths:")
        print("\n".join(f"- {item}" for item in missing))
        return 1
    print(f"Structure OK: {len(REQUIRED)} required paths present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
