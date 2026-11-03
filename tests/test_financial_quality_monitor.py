"""
Automated tests for Sprint 07 financial monitoring.

All database responses are simulated.
No PostgreSQL tables are modified.
"""

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "monitor_financial_quality.py"

spec = importlib.util.spec_from_file_location(
    "financial_quality_monitor",
    SCRIPT,
)
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)


@pytest.fixture
def simulated_database(monkeypatch):
    """Provide known results without using PostgreSQL."""

    values = {
        "raw_count": 121253,
        "fact_count": 121253,
        "missing_keys": 0,
        "broken_profit": 0,
        "formula_flags": 3282,
        "loss_lines": 21829,
        "reseller_margin": 0.58,
    }

    def fake_run_scalar(connection, query):
        normalized = " ".join(query.lower().split())

        if "select count(*) from raw.sales" in normalized:
            return values["raw_count"]

        if (
            "select count(*) from dbt_dev.fact_sales"
            in normalized
        ):
            if "product_key is null" in normalized:
                return values["missing_keys"]

            if "revenue is null" in normalized:
                return values["broken_profit"]

            if "abs(formula_difference)" in normalized:
                return values["formula_flags"]

            if "gross_profit < 0" in normalized:
                return values["loss_lines"]

            return values["fact_count"]

        if "100.0 * sum(gross_profit)" in normalized:
            return values["reseller_margin"]

        raise AssertionError(
            f"Unexpected SQL query: {query}"
        )

    monkeypatch.setattr(
        monitor,
        "run_scalar",
        fake_run_scalar,
    )

    return values


def check_statuses(checks):
    return {
        item["name"]: item["status"]
        for item in checks
    }


def test_expected_financial_results(simulated_database):
    checks = monitor.collect_checks(None)

    statuses = [item["status"] for item in checks]

    assert statuses.count("PASS") == 4
    assert statuses.count("WARN") == 3
    assert statuses.count("FAIL") == 0


def test_raw_fact_mismatch_fails(simulated_database):
    simulated_database["fact_count"] = 121000

    checks = monitor.collect_checks(None)
    statuses = check_statuses(checks)

    assert (
        statuses["Raw-to-mart row reconciliation"]
        == "FAIL"
    )


def test_missing_keys_and_broken_profit_fail(
    simulated_database,
):
    simulated_database["missing_keys"] = 5
    simulated_database["broken_profit"] = 2

    checks = monitor.collect_checks(None)
    statuses = check_statuses(checks)

    assert statuses["Required analytical keys"] == "FAIL"
    assert statuses["Gross profit reconciliation"] == "FAIL"


def test_report_generation(
    simulated_database,
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        monitor,
        "OUTPUT_DIR",
        tmp_path,
    )

    checks = monitor.collect_checks(None)

    counts, json_path, md_path = (
        monitor.save_reports(checks)
    )

    assert counts == {
        "PASS": 4,
        "WARN": 3,
        "FAIL": 0,
    }

    assert json_path.is_file()
    assert md_path.is_file()

    report = json.loads(
        json_path.read_text(encoding="utf-8")
    )

    assert len(report["checks"]) == 7
    assert report["summary"] == counts

    markdown = md_path.read_text(
        encoding="utf-8"
    )

    assert "Financial Data Quality Monitoring" in markdown
    assert "WARN" in markdown
