"""
Sprint 09 - Pipeline Events Tests.

Tests structured event recording and failure handling.

All tests use temporary directories.
No PostgreSQL access or systemd execution is required.
"""

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "pipeline_events.py"

spec = importlib.util.spec_from_file_location(
    "pipeline_events",
    MODULE_PATH,
)

events = importlib.util.module_from_spec(spec)
spec.loader.exec_module(events)


@pytest.fixture
def isolated_events(tmp_path, monkeypatch):
    """Redirect event storage to a temporary directory."""
    monkeypatch.setattr(
        events,
        "EVENTS_DIR",
        tmp_path / "operations",
    )
    return tmp_path / "operations"


def test_successful_stage_recording(isolated_events):
    run_id = "test_success"

    events.record_event(
        run_id, "pytest", "STARTED"
    )

    events.record_event(
        run_id, "pytest", "SUCCESS"
    )

    path = isolated_events / f"{run_id}.jsonl"

    assert path.exists()

    records = [
        json.loads(line)
        for line in path.read_text().splitlines()
    ]

    assert len(records) == 2
    assert records[0]["status"] == "STARTED"
    assert records[1]["status"] == "SUCCESS"


def test_failed_stage_recording(isolated_events):
    run_id = "test_failure"

    events.record_event(
        run_id, "dbt", "STARTED"
    )

    events.record_event(
        run_id,
        "dbt",
        "FAILED",
        exit_code=1,
    )

    path = isolated_events / f"{run_id}.jsonl"

    records = [
        json.loads(line)
        for line in path.read_text().splitlines()
    ]

    assert records[-1]["status"] == "FAILED"
    assert records[-1]["exit_code"] == 1


def test_invalid_run_id_is_rejected(isolated_events):
    with pytest.raises(ValueError):
        events.record_event(
            "../invalid",
            "pytest",
            "STARTED",
        )


def test_failure_requires_nonzero_exit_code(
    isolated_events,
):
    with pytest.raises(ValueError):
        events.record_event(
            "invalid_failure",
            "dbt",
            "FAILED",
            exit_code=0,
        )


def test_summary_reports_unstarted_stages(
    isolated_events,
    capsys,
):
    run_id = "partial_execution"

    events.record_event(
        run_id,
        "pytest",
        "SUCCESS",
    )

    events.record_event(
        run_id,
        "dbt",
        "FAILED",
        exit_code=2,
    )

    events.show_summary(run_id)

    output = capsys.readouterr().out

    assert "pytest: SUCCESS" in output
    assert "dbt: FAILED" in output
    assert "Exit code: 2" in output
    assert "financial_monitor: NOT_STARTED" in output
    assert "archive: NOT_STARTED" in output
    assert "comparison: NOT_STARTED" in output
