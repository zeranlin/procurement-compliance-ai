"""Validate JSON contract files without requiring third-party packages."""

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failures = []
    for path in sorted((ROOT / "contracts").rglob("*.json")):
        try:
            with path.open(encoding="utf-8") as handle:
                json.load(handle)
        except Exception as exc:  # pragma: no cover - bootstrap validator
            failures.append(f"{path.relative_to(ROOT)}: {exc}")
    if failures:
        print("Invalid JSON contract files:")
        print("\n".join(f"- {item}" for item in failures))
        return 1
    print("Contract JSON syntax OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
