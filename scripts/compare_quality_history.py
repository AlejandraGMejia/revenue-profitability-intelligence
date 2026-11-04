"""
Sprint 08 - Historical Financial Quality Comparison.

Compares the two latest distinct monitoring executions.
Reads archived JSON files without modifying PostgreSQL.
"""

import json
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "reports" / "monitoring" / "history"


def parse_timestamp(value):
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def load_history():
    records = []

    if not HISTORY.is_dir():
        return records

    for path in sorted(HISTORY.glob("*/quality_report.json")):
        report = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(report, dict):
            raise ValueError(f"Invalid report: {path}")

        timestamp = report.get("generated_at_utc")
        summary = report.get("summary")
        checks = report.get("checks")

        if (
            not isinstance(timestamp, str)
            or not isinstance(summary, dict)
            or not isinstance(checks, list)
        ):
            raise ValueError(f"Incomplete report: {path}")

        if any(
            not isinstance(summary.get(key), int)
            for key in ("PASS", "WARN", "FAIL")
        ):
            raise ValueError(f"Invalid summary: {path}")

        records.append({
            "timestamp": timestamp,
            "datetime": parse_timestamp(timestamp),
            "summary": summary,
            "checks": checks,
            "path": path,
        })

    # Avoid counting repeated archives of one report
    # as separate monitoring executions.
    unique = {}

    for record in records:
        unique[record["timestamp"]] = record

    return sorted(
        unique.values(),
        key=lambda item: item["datetime"],
    )


def numeric_value(value):
    text = str(value).strip().replace(",", "")

    if text.endswith("%"):
        text = text[:-1]

    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def compare_checks(previous, current):
    previous_checks = {
        item["name"]: item
        for item in previous["checks"]
    }

    current_checks = {
        item["name"]: item
        for item in current["checks"]
    }

    print("\nCHECK-LEVEL CHANGES")
    print("-" * 60)

    changes = 0

    for name in sorted(
        set(previous_checks) | set(current_checks)
    ):
        old = previous_checks.get(name)
        new = current_checks.get(name)

        if old is None:
            print(f"NEW CHECK: {name}")
            changes += 1
            continue

        if new is None:
            print(f"REMOVED CHECK: {name}")
            changes += 1
            continue

        old_value = old["value"]
        new_value = new["value"]
        old_status = old["status"]
        new_status = new["status"]

        if (
            old_value == new_value
            and old_status == new_status
        ):
            continue

        changes += 1
        print(f"\n{name}")
        print(f"  Status: {old_status} -> {new_status}")
        print(f"  Value:  {old_value} -> {new_value}")

        old_number = numeric_value(old_value)
        new_number = numeric_value(new_value)

        if old_number is not None and new_number is not None:
            delta = new_number - old_number
            print(f"  Numeric difference: {delta:+}")

    if changes == 0:
        print("No changes detected between these reports.")


def main():
    try:
        history = load_history()
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
    ) as exc:
        print(
            f"Unable to read monitoring history: {exc}",
            file=sys.stderr,
        )
        return 2

    print("FINANCIAL QUALITY HISTORY")
    print("=" * 60)
    print(f"Distinct monitoring executions: {len(history)}")

    if not history:
        print("No archived reports are available.")
        return 0

    latest = history[-1]

    print(f"Latest execution: {latest['timestamp']}")
    print(
        "Latest summary: "
        f"PASS={latest['summary']['PASS']} "
        f"WARN={latest['summary']['WARN']} "
        f"FAIL={latest['summary']['FAIL']}"
    )

    if len(history) < 2:
        print("\nBASELINE ESTABLISHED")
        print(
            "A second distinct pipeline execution is "
            "required for historical comparison."
        )
        return 0

    previous = history[-2]

    print("\nPREVIOUS VS CURRENT")
    print("-" * 60)
    print(f"Previous: {previous['timestamp']}")
    print(f"Current:  {latest['timestamp']}")

    for status in ("PASS", "WARN", "FAIL"):
        before = previous["summary"][status]
        after = latest["summary"][status]

        print(
            f"{status}: {before} -> {after} "
            f"(difference {after - before:+})"
        )

    compare_checks(previous, latest)

    if latest["summary"]["FAIL"] > 0:
        print("\nALERT: Technical failures detected.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
