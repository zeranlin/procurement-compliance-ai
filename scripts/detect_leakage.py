"""Fail on obvious secrets or blind-gold payloads in tracked working files."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".md", ".json", ".jsonl", ".yaml", ".yml", ".py", ".txt", ".toml"}
SECRET_PATTERNS = [
    re.compile(r"gh" + r"p_[A-Za-z0-9]{20,}"),
    re.compile(r"github" + r"_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]


def main() -> int:
    failures = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_EXTENSIONS:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if "blind_test_gold" in relative and path.name != "README.md":
            failures.append(f"blind-test payload path: {relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            failures.append(f"possible secret: {relative}")
    if failures:
        print("Sensitive-content check failed:")
        print("\n".join(f"- {item}" for item in failures))
        return 1
    print("Sensitive-content check OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
