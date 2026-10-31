"""
Revenue & Profitability Intelligence
Sprint 05 - Financial Exploratory Data Analysis

Creates financial comparisons for the complete
calendar years 2018 and 2019.

Source: PostgreSQL dbt_dev analytical models.
"""

import os
from getpass import getpass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import psycopg


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "figures"
OUTPUT.mkdir(parents=True, exist_ok=True)

ANNUAL_QUERY = """
SELECT
    d.calendar_year AS year,
    f.sales_channel AS channel,
    COUNT(*) AS sales_lines,
    SUM(f.order_quantity) AS units_sold,
    SUM(f.revenue) AS revenue,
    SUM(f.total_product_cost) AS product_cost,
    SUM(f.gross_profit) AS gross_profit,
    100 * SUM(f.gross_profit)
        / NULLIF(SUM(f.revenue), 0)
        AS gross_margin_pct
FROM dbt_dev.fact_sales AS f
JOIN dbt_dev.dim_date AS d
    ON f.order_date_key = d.date_key
WHERE d.calendar_year IN (2018, 2019)
GROUP BY
    d.calendar_year,
    f.sales_channel
ORDER BY
    d.calendar_year,
    f.sales_channel
"""

MONTHLY_QUERY = """
WITH calendar_months AS (
    SELECT generate_series(
        DATE '2018-01-01',
        DATE '2019-12-01',
        INTERVAL '1 month'
    )::date AS sales_month
),
channels AS (
    SELECT DISTINCT sales_channel
    FROM dbt_dev.fact_sales
),
monthly_sales AS (
    SELECT
        date_trunc('month', d.full_date)::date
            AS sales_month,
        f.sales_channel,
        COUNT(*) AS sales_lines,
        SUM(f.revenue) AS revenue,
        SUM(f.gross_profit) AS gross_profit
    FROM dbt_dev.fact_sales AS f
    JOIN dbt_dev.dim_date AS d
        ON f.order_date_key = d.date_key
    WHERE d.full_date >= DATE '2018-01-01'
      AND d.full_date < DATE '2020-01-01'
    GROUP BY 1, 2
)
SELECT
    c.sales_month,
    ch.sales_channel AS channel,
    COALESCE(m.sales_lines, 0) AS sales_lines,
    COALESCE(m.revenue, 0) AS revenue,
    COALESCE(m.gross_profit, 0) AS gross_profit
FROM calendar_months AS c
CROSS JOIN channels AS ch
LEFT JOIN monthly_sales AS m
    ON c.sales_month = m.sales_month
   AND ch.sales_channel = m.sales_channel
ORDER BY c.sales_month, ch.sales_channel
"""


def load_dataframe(connection, query):
    """Read an SQL result into a pandas DataFrame."""
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [
            column.name
            for column in cursor.description
        ]
    return pd.DataFrame(rows, columns=columns)


def prepare_numeric_columns(dataframe):
    """Convert PostgreSQL Decimal values for plotting."""
    for column in (
        "revenue",
        "product_cost",
        "gross_profit",
        "gross_margin_pct",
    ):
        if column in dataframe.columns:
            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="raise",
            )
    return dataframe


def save_chart(filename):
    plt.tight_layout()
    plt.savefig(
        OUTPUT / filename,
        dpi=180,
        bbox_inches="tight",
    )
    plt.close()


def chart_annual_revenue(annual):
    pivot = annual.pivot(
        index="year",
        columns="channel",
        values="revenue",
    ) / 1_000_000

    ax = pivot.plot.bar(figsize=(9, 5))
    ax.set_title("Annual Revenue by Sales Channel")
    ax.set_xlabel("Calendar Year")
    ax.set_ylabel("Revenue (USD Millions)")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Sales Channel")
    ax.grid(axis="y", alpha=0.25)

    save_chart("annual_revenue_by_channel.png")


def chart_annual_margin(annual):
    pivot = annual.pivot(
        index="year",
        columns="channel",
        values="gross_margin_pct",
    )

    ax = pivot.plot.bar(figsize=(9, 5))
    ax.axhline(0, linewidth=1)
    ax.set_title("Gross Margin by Sales Channel")
    ax.set_xlabel("Calendar Year")
    ax.set_ylabel("Gross Margin (%)")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Sales Channel")
    ax.grid(axis="y", alpha=0.25)

    save_chart("annual_gross_margin.png")


def chart_monthly_revenue(monthly):
    pivot = monthly.pivot(
        index="sales_month",
        columns="channel",
        values="revenue",
    ) / 1_000_000

    ax = pivot.plot(figsize=(11, 5), marker="o")
    ax.set_title("Monthly Revenue by Channel: 2018-2019")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (USD Millions)")
    ax.grid(alpha=0.25)
    ax.legend(title="Sales Channel")

    save_chart("monthly_revenue_trend.png")


def chart_monthly_profit(monthly):
    pivot = monthly.pivot(
        index="sales_month",
        columns="channel",
        values="gross_profit",
    ) / 1_000

    ax = pivot.plot(figsize=(11, 5), marker="o")
    ax.axhline(0, linewidth=1)
    ax.set_title(
        "Monthly Gross Profit by Channel: 2018-2019"
    )
    ax.set_xlabel("Month")
    ax.set_ylabel("Gross Profit (USD Thousands)")
    ax.grid(alpha=0.25)
    ax.legend(title="Sales Channel")

    save_chart("monthly_gross_profit.png")


def main():
    password = os.environ.get("PGPASSWORD")

    if not password:
        password = getpass(
            "PostgreSQL password for revenue_app: "
        )

    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="revenue_intelligence",
        user="revenue_app",
        password=password,
        connect_timeout=10,
        options="-c default_transaction_read_only=on",
    ) as connection:

        annual = load_dataframe(
            connection, ANNUAL_QUERY
        )

        monthly = load_dataframe(
            connection, MONTHLY_QUERY
        )

    annual = prepare_numeric_columns(annual)
    monthly = prepare_numeric_columns(monthly)

    monthly["sales_month"] = pd.to_datetime(
        monthly["sales_month"]
    )

    assert len(annual) == 4, (
        "Expected two years and two channels."
    )
    assert len(monthly) == 48, (
        "Expected 24 months and two channels."
    )

    annual.to_csv(
        OUTPUT / "annual_financial_summary.csv",
        index=False,
    )

    monthly.to_csv(
        OUTPUT / "monthly_financial_summary.csv",
        index=False,
    )

    chart_annual_revenue(annual)
    chart_annual_margin(annual)
    chart_monthly_revenue(monthly)
    chart_monthly_profit(monthly)

    print("\nFINANCIAL EDA COMPLETED")
    print("=" * 50)
    print(annual.to_string(index=False))
    print("\nMissing month-channel combinations:")
    print(
        monthly.loc[
            monthly["sales_lines"] == 0,
            ["sales_month", "channel"],
        ].to_string(index=False)
    )
    print(f"\nOutputs saved in: {OUTPUT}")
    print("Generated 4 PNG charts and 2 CSV files.")


if __name__ == "__main__":
    main()
