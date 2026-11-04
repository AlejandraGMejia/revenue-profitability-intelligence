"""
Sprint 08 - Financial Quality Monitoring History.

Archives a validated monitoring report without
overwriting previous archived executions.

The latest report files remain unchanged.
"""

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REPORTS = ROOT / "reports" / "monitoring"

SOURCE_JSON = REPORTS / "latest_quality_report.json"
SOURCE_MD = REPORTS / "latest_quality_report.md"

HISTORY = REPORTS / "history"


def archive_report():
    if not SOURCE_JSON.is_file():
        raise FileNotFoundError(
            f"Missing monitoring report: {SOURCE_JSON}"
        )

    if not SOURCE_MD.is_file():
        raise FileNotFoundError(
            f"Missing monitoring report: {SOURCE_MD}"
        )

    report = json.loads(
        SOURCE_JSON.read_text(encoding="utf-8")
    )

    required = {
        "project",
        "generated_at_utc",
        "summary",
        "checks",
    }

    if not required.issubset(report):
        raise ValueError(
            "Monitoring JSON is missing required fields."
        )

    summary = report["summary"]

    if not isinstance(report["checks"], list):
        raise ValueError("Checks must be a list.")

    if any(
        not isinstance(summary.get(status), int)
        for status in ("PASS", "WARN", "FAIL")
    ):
        raise ValueError(
            "Invalid monitoring summary."
        )

    calculated = {
        status: sum(
            check.get("status") == status
            for check in report["checks"]
        )
        for status in ("PASS", "WARN", "FAIL")
    }

    if calculated != {
        status: summary[status]
        for status in calculated
    }:
        raise ValueError(
            "Summary counts do not match report checks."
        )

    HISTORY.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%S%fZ")

    execution_id = (
        f"{timestamp}_{uuid.uuid4().hex[:8]}"
    )

    destination = HISTORY / execution_id
    destination.mkdir(mode=0o755)

    json_path = destination / "quality_report.json"
    md_path = destination / "quality_report.md"

    json_path.write_bytes(SOURCE_JSON.read_bytes())
    md_path.write_bytes(SOURCE_MD.read_bytes())

    metadata = {
        "execution_id": execution_id,
        "archived_at_utc": datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds"),
        "source_generated_at_utc": report[
            "generated_at_utc"
        ],
        "summary": summary,
    }

    (destination / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    print("FINANCIAL QUALITY REPORT ARCHIVED")
    print("=" * 45)
    print(f"Execution ID: {execution_id}")
    print(f"PASS: {summary['PASS']}")
    print(f"WARN: {summary['WARN']}")
    print(f"FAIL: {summary['FAIL']}")
    print(f"Archive location: {destination}")


def main():
    try:
        archive_report()
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        TypeError,
        AttributeError,
    ) as exc:
        print(
            f"Archiving failed: {exc}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
