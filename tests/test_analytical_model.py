
"""
Analytical star schema validation tests.

Project: Revenue & Profitability Intelligence
Sprint: 03 - Data Warehouse & Advanced SQL

Run:
    python -m pytest tests/test_analytical_model.py -v -s
"""

import os
from decimal import Decimal
from getpass import getpass

import psycopg
import pytest
from psycopg import sql


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "revenue_intelligence",
    "user": "revenue_app",
    "connect_timeout": 10,
}

DIMENSIONS = {
    "dim_product": ("product_key", 397),
    "dim_customer": ("customer_key", 18485),
    "dim_reseller": ("reseller_key", 702),
    "dim_date": ("date_key", 1461),
    "dim_territory": ("territory_key", 11),
}

EXPECTED_REVENUE = Decimal("109809274.20")
EXPECTED_COST = Decimal("97257907.95")
EXPECTED_PROFIT = Decimal("12551366.25")


@pytest.fixture(scope="module")
def db_connection():
    password = os.environ.get("PGPASSWORD")

    if not password:
        password = getpass(
            "\nPostgreSQL password for revenue_app: "
        )

    with psycopg.connect(
        **DB_CONFIG,
        password=password,
        autocommit=True,
    ) as connection:

        with connection.cursor() as cursor:
            cursor.execute(
                "SET default_transaction_read_only = on"
            )

        yield connection


@pytest.mark.parametrize(
    "view",
    ["fact_sales", *DIMENSIONS.keys()],
)
def test_analytical_views_exist(db_connection, view):
    """All expected analytical views must exist."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.views
            WHERE table_schema = 'marts'
              AND table_name = %s
            """,
            (view,),
        )

        actual = cursor.fetchone()[0]

    assert actual == 1, f"Missing analytical view: {view}"


@pytest.mark.parametrize(
    "view,configuration",
    list(DIMENSIONS.items()),
)
def test_dimension_integrity(
    db_connection, view, configuration
):
    """Dimension keys must be unique and complete."""

    key, expected_rows = configuration

    query = sql.SQL(
        """
        SELECT
            COUNT(*),
            COUNT(DISTINCT {}),
            COUNT(*) FILTER (WHERE {} IS NULL)
        FROM {}
        """
    ).format(
        sql.Identifier(key),
        sql.Identifier(key),
        sql.Identifier("marts", view),
    )

    with db_connection.cursor() as cursor:
        cursor.execute(query)
        rows, unique_keys, null_keys = cursor.fetchone()

    assert rows == expected_rows
    assert unique_keys == rows
    assert null_keys == 0


def test_fact_grain(db_connection):
    """One analytical fact per source sales line."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*),
                COUNT(DISTINCT sales_order_line_key)
            FROM marts.fact_sales
            """
        )

        rows, unique_keys = cursor.fetchone()

    assert rows == 121253
    assert unique_keys == rows


def test_fact_financial_reconciliation(db_connection):
    """Analytical totals must match RAW totals exactly."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                SUM(revenue),
                SUM(total_product_cost),
                SUM(gross_profit)
            FROM marts.fact_sales
            """
        )
        marts_totals = cursor.fetchone()

        cursor.execute(
            """
            SELECT
                SUM("Sales Amount"),
                SUM("Total Product Cost"),
                SUM(
                    "Sales Amount" - "Total Product Cost"
                )
            FROM raw.sales
            """
        )
        raw_totals = cursor.fetchone()

    assert marts_totals == raw_totals

    revenue, cost, profit = marts_totals

    assert round(revenue, 2) == EXPECTED_REVENUE
    assert round(cost, 2) == EXPECTED_COST
    assert round(profit, 2) == EXPECTED_PROFIT


def test_fact_dimension_relationships(db_connection):
    """Every fact must match all applicable dimensions."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM marts.fact_sales AS f
            LEFT JOIN marts.dim_product AS p
                ON f.product_key = p.product_key
            LEFT JOIN marts.dim_customer AS c
                ON f.customer_key = c.customer_key
            LEFT JOIN marts.dim_reseller AS r
                ON f.reseller_key = r.reseller_key
            LEFT JOIN marts.dim_territory AS t
                ON f.territory_key = t.territory_key
            LEFT JOIN marts.dim_date AS d
                ON f.order_date_key = d.date_key
            WHERE p.product_key IS NULL
               OR c.customer_key IS NULL
               OR r.reseller_key IS NULL
               OR t.territory_key IS NULL
               OR d.date_key IS NULL
            """
        )

        unmatched = cursor.fetchone()[0]

    assert unmatched == 0


def test_channel_placeholder_rules(db_connection):
    """Channel-specific special keys must be respected."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM marts.fact_sales
            WHERE NOT (
                (
                    sales_channel = 'Internet'
                    AND reseller_key = -1
                    AND customer_key <> -1
                )
                OR
                (
                    sales_channel = 'Reseller'
                    AND customer_key = -1
                    AND reseller_key <> -1
                )
            )
            """
        )

        invalid = cursor.fetchone()[0]

    assert invalid == 0


def test_negative_profit_classification(db_connection):
    """Negative gross profit flags must match calculations."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*) FILTER (
                    WHERE is_negative_gross_profit
                ),
                COUNT(*) FILTER (
                    WHERE is_negative_gross_profit
                    IS DISTINCT FROM (gross_profit < 0)
                )
            FROM marts.fact_sales
            """
        )

        negative_count, inconsistent = cursor.fetchone()

    assert negative_count == 21829
    assert inconsistent == 0


def test_formula_discrepancies(db_connection):
    """Known formula discrepancies must remain traceable."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*) FILTER (
                    WHERE ABS(formula_difference) > 0.02
                ),
                ROUND(
                    SUM(formula_difference) FILTER (
                        WHERE ABS(formula_difference) > 0.02
                    ), 2
                )
            FROM marts.fact_sales
            """
        )

        count, difference = cursor.fetchone()

    assert count == 3282
    assert difference == Decimal("527507.89")


def test_missing_reseller_months(db_connection):
    """Validate known months without Reseller transactions."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            WITH months AS (
                SELECT GENERATE_SERIES(
                    DATE '2017-07-01',
                    DATE '2020-06-01',
                    INTERVAL '1 month'
                )::DATE AS month_start
            ),
            observed AS (
                SELECT DISTINCT
                    DATE_TRUNC(
                        'month', d.full_date
                    )::DATE AS month_start
                FROM marts.fact_sales AS f
                JOIN marts.dim_date AS d
                    ON f.order_date_key = d.date_key
                WHERE f.sales_channel = 'Reseller'
            )
            SELECT m.month_start
            FROM months AS m
            LEFT JOIN observed AS o
                ON m.month_start = o.month_start
            WHERE o.month_start IS NULL
            ORDER BY m.month_start
            """
        )

        actual = [
            str(row[0])
            for row in cursor.fetchall()
        ]

    expected = [
        "2017-10-01",
        "2017-12-01",
        "2018-03-01",
    ]

    assert actual == expected


def test_june_2018_reseller_loss(db_connection):
    """Validate the documented monthly gross loss."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT ROUND(SUM(f.gross_profit), 2)
            FROM marts.fact_sales AS f
            JOIN marts.dim_date AS d
                ON f.order_date_key = d.date_key
            WHERE f.sales_channel = 'Reseller'
              AND d.full_date >= DATE '2018-06-01'
              AND d.full_date < DATE '2018-07-01'
            """
        )

        actual = cursor.fetchone()[0]

    assert actual == Decimal("-605204.44")


def test_reseller_bikes_loss(db_connection):
    """Validate the documented Reseller Bikes gross loss."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT ROUND(SUM(f.gross_profit), 2)
            FROM marts.fact_sales AS f
            JOIN marts.dim_product AS p
                ON f.product_key = p.product_key
            WHERE f.sales_channel = 'Reseller'
              AND p.category = 'Bikes'
            """
        )

        actual = cursor.fetchone()[0]

    assert actual == Decimal("-990699.89")
