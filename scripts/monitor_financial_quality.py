"""
Revenue & Profitability Intelligence
Sprint 07 - Financial Data Quality Monitoring

Read-only monitoring of PostgreSQL/dbt analytical models.

Produces:
    reports/monitoring/latest_quality_report.json
    reports/monitoring/latest_quality_report.md

Exit codes:
    0 = All technical checks passed
    1 = At least one technical check failed
    2 = Monitoring could not complete
"""

import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from getpass import getpass
from pathlib import Path

import psycopg


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "reports" / "monitoring"


def run_scalar(connection, query):
    """Execute a read-only SQL query returning one value."""
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()

    if result is None:
        raise RuntimeError("SQL query returned no result")

    return result[0]


def add_check(checks, name, status, details, value):
    checks.append(
        {
            "name": name,
            "status": status,
            "details": details,
            "value": str(value),
        }
    )


def collect_checks(connection):
    """Run technical checks and financial observations."""
    checks = []

    raw_count = run_scalar(
        connection,
        "SELECT COUNT(*) FROM raw.sales",
    )

    fact_count = run_scalar(
        connection,
        "SELECT COUNT(*) FROM dbt_dev.fact_sales",
    )

    add_check(
        checks,
        "Raw-to-mart row reconciliation",
        "PASS" if raw_count == fact_count else "FAIL",
        "Raw sales rows must match analytical fact rows.",
        f"raw={raw_count}, fact={fact_count}",
    )

    add_check(
        checks,
        "Non-empty analytical fact",
        "PASS" if fact_count > 0 else "FAIL",
        "The financial fact model must contain records.",
        fact_count,
    )

    missing_keys = run_scalar(
        connection,
        """
        SELECT COUNT(*)
        FROM dbt_dev.fact_sales
        WHERE product_key IS NULL
           OR order_date_key IS NULL
           OR territory_key IS NULL
        """,
    )

    add_check(
        checks,
        "Required analytical keys",
        "PASS" if missing_keys == 0 else "FAIL",
        "Required product, order-date, and territory keys.",
        missing_keys,
    )

    broken_profit_rows = run_scalar(
        connection,
        """
        SELECT COUNT(*)
        FROM dbt_dev.fact_sales
        WHERE revenue IS NULL
           OR total_product_cost IS NULL
           OR gross_profit IS NULL
           OR ABS(
                revenue
                - total_product_cost
                - gross_profit
           ) > 0.02
        """,
    )

    add_check(
        checks,
        "Gross profit reconciliation",
        "PASS" if broken_profit_rows == 0 else "FAIL",
        "Each line must reconcile revenue minus product cost "
        "to gross profit, within USD 0.02.",
        broken_profit_rows,
    )

    formula_flags = run_scalar(
        connection,
        """
        SELECT COUNT(*)
        FROM dbt_dev.fact_sales
        WHERE ABS(formula_difference) > 0.02
        """,
    )

    add_check(
        checks,
        "Recorded revenue formula differences",
        "WARN" if formula_flags > 0 else "PASS",
        "Diagnostic differences require business review; "
        "they are not automatically data errors.",
        formula_flags,
    )

    loss_lines = run_scalar(
        connection,
        """
        SELECT COUNT(*)
        FROM dbt_dev.fact_sales
        WHERE gross_profit < 0
        """,
    )

    add_check(
        checks,
        "Negative gross profit lines",
        "WARN" if loss_lines > 0 else "PASS",
        "Negative gross profit is a business observation.",
        loss_lines,
    )

    reseller_margin = run_scalar(
        connection,
        """
        SELECT
            100.0 * SUM(gross_profit)
            / NULLIF(SUM(revenue), 0)
        FROM dbt_dev.fact_sales
        WHERE sales_channel = 'Reseller'
        """,
    )

    if reseller_margin is None:
        status = "WARN"
        margin_display = "N/A"
    else:
        margin_display = (
            f"{Decimal(reseller_margin):.2f}%"
        )
        status = (
            "WARN" if reseller_margin < 2 else "PASS"
        )

    add_check(
        checks,
        "Reseller gross margin observation",
        status,
        "Monitoring threshold of 2% is illustrative, "
        "not an approved business target.",
        margin_display,
    )

    return checks


def save_reports(checks):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    counts = {
        state: sum(
            check["status"] == state
            for check in checks
        )
        for state in ("PASS", "WARN", "FAIL")
    }

    report = {
        "project": "Revenue & Profitability Intelligence",
        "generated_at_utc": generated_at,
        "database": "revenue_intelligence",
        "analytical_schema": "dbt_dev",
        "summary": counts,
        "checks": checks,
    }

    json_path = (
        OUTPUT_DIR / "latest_quality_report.json"
    )
    markdown_path = (
        OUTPUT_DIR / "latest_quality_report.md"
    )

    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )

    rows = [
        "# Financial Data Quality Monitoring",
        "",
        f"Generated (UTC): {generated_at}",
        "",
        "## Summary",
        "",
        f"- PASS: {counts['PASS']}",
        f"- WARN: {counts['WARN']}",
        f"- FAIL: {counts['FAIL']}",
        "",
        "## Results",
        "",
        "| Check | Status | Value |",
        "|---|---|---|",
    ]

    for check in checks:
        rows.append(
            f"| {check['name']} "
            f"| {check['status']} "
            f"| {check['value']} |"
        )

    rows.extend([
        "",
        "## Interpretation",
        "",
        "FAIL indicates a technical data quality problem.",
        "",
        "WARN highlights an observation requiring review.",
        "",
        "Warnings are not automatically pipeline failures.",
        "",
        "All queries use read-only database access.",
    ])

    markdown_path.write_text(
        "\n".join(rows) + "\n",
        encoding="utf-8",
    )

    return counts, json_path, markdown_path


def main():
    password = os.environ.get("PGPASSWORD")

    if password is None:
        password = getpass(
            "PostgreSQL password for revenue_app: "
        )

    try:
        with psycopg.connect(
            host="127.0.0.1",
            port=5432,
            dbname="revenue_intelligence",
            user="revenue_app",
            password=password,
            connect_timeout=10,
            options="-c default_transaction_read_only=on",
        ) as connection:
            checks = collect_checks(connection)

        counts, json_path, markdown_path = (
            save_reports(checks)
        )

    except (psycopg.Error, OSError, RuntimeError) as exc:
        print(
            f"Monitoring could not complete: "
            f"{type(exc).__name__}",
            file=sys.stderr,
        )
        return 2

    print("\nFINANCIAL DATA QUALITY MONITOR")
    print("=" * 55)

    for check in checks:
        print(
            f"[{check['status']}] "
            f"{check['name']}: "
            f"{check['value']}"
        )

    print("\nSUMMARY")
    print(
        f"PASS={counts['PASS']} "
        f"WARN={counts['WARN']} "
        f"FAIL={counts['FAIL']}"
    )

    print("\nREPORTS")
    print(json_path)
    print(markdown_path)

    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
