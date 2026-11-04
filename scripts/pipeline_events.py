"""
Revenue & Profitability Intelligence
Sprint 09 - Pipeline Execution Events

Records structured execution events without storing
database passwords or other credentials.

Usage:
    python scripts/pipeline_events.py record \
        --run-id example --stage dbt --status STARTED

    python scripts/pipeline_events.py summary \
        --run-id example
"""

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVENTS_DIR = ROOT / "reports" / "monitoring" / "operations"

STAGES = (
    "pytest",
    "dbt",
    "financial_monitor",
    "archive",
    "comparison",
)

STATUSES = ("STARTED", "SUCCESS", "FAILED")


def validate_run_id(run_id):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", run_id):
        raise ValueError("Invalid execution identifier.")
    return run_id


def event_path(run_id):
    validate_run_id(run_id)
    return EVENTS_DIR / f"{run_id}.jsonl"


def record_event(run_id, stage, status, exit_code=None):
    if stage not in STAGES:
        raise ValueError(f"Unknown pipeline stage: {stage}")

    if status not in STATUSES:
        raise ValueError(f"Unknown event status: {status}")

    if status == "FAILED":
        if exit_code is None or exit_code == 0:
            raise ValueError(
                "FAILED events require a nonzero exit code."
            )
    elif exit_code not in (None, 0):
        raise ValueError(
            "Only FAILED events can use nonzero exit codes."
        )

    EVENTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
        mode=0o700,
    )
    os.chmod(EVENTS_DIR, 0o700)

    event = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds"),
        "stage": stage,
        "status": status,
        "exit_code": exit_code,
    }

    path = event_path(run_id)

    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_APPEND,
        0o600,
    )

    with os.fdopen(descriptor, "a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")
        file.flush()
        os.fsync(file.fileno())

    print(f"[{status}] {stage} | run={run_id}")
    return path


def show_summary(run_id):
    path = event_path(run_id)

    if not path.is_file():
        raise FileNotFoundError(
            f"No events found for execution: {run_id}"
        )

    events = [
        json.loads(line)
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    latest = {}

    for event in events:
        latest[event["stage"]] = event

    print("\nPIPELINE EXECUTION SUMMARY")
    print("=" * 45)
    print(f"Run ID: {run_id}")

    for stage in STAGES:
        if stage not in latest:
            print(f"{stage}: NOT_STARTED")
            continue

        event = latest[stage]
        print(f"{stage}: {event['status']}")

        if event["status"] == "FAILED":
            print(
                f"  Exit code: {event['exit_code']}"
            )

    print(f"\nEvent file: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Record pipeline execution events"
    )
    commands = parser.add_subparsers(
        dest="command",
        required=True,
    )

    record = commands.add_parser("record")
    record.add_argument("--run-id", required=True)
    record.add_argument(
        "--stage",
        required=True,
        choices=STAGES,
    )
    record.add_argument(
        "--status",
        required=True,
        choices=STATUSES,
    )
    record.add_argument(
        "--exit-code",
        type=int,
        default=None,
    )

    summary = commands.add_parser("summary")
    summary.add_argument("--run-id", required=True)

    args = parser.parse_args()

    try:
        if args.command == "record":
            record_event(
                args.run_id,
                args.stage,
                args.status,
                args.exit_code,
            )
        else:
            show_summary(args.run_id)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
