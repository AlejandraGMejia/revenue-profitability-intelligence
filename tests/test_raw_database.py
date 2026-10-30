
"""
Automated PostgreSQL RAW data quality tests.

Project: Revenue & Profitability Intelligence
Framework: pytest
Database: revenue_intelligence

Run:
    python -m pytest tests/test_raw_database.py -v -s
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

EXPECTED_ROWS = {
    "products": 397,
    "customers": 18485,
    "resellers": 702,
    "dates": 1461,
    "territories": 11,
    "orders": 121253,
    "sales": 121253,
}

PRIMARY_KEYS = {
    "products": "ProductKey",
    "customers": "CustomerKey",
    "resellers": "ResellerKey",
    "dates": "DateKey",
    "territories": "SalesTerritoryKey",
    "orders": "SalesOrderLineKey",
    "sales": "SalesOrderLineKey",
}

EXPECTED_REVENUE = Decimal("109809274.20")
EXPECTED_COST = Decimal("97257907.95")
EXPECTED_PROFIT = Decimal("12551366.25")


@pytest.fixture(scope="session")
def db_connection():
    """Create one read-only connection for all tests."""

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
    "table, expected",
    list(EXPECTED_ROWS.items()),
)
def test_row_counts(db_connection, table, expected):
    """Verify exact source snapshot record counts."""

    query = sql.SQL(
        "SELECT COUNT(*) FROM {}"
    ).format(
        sql.Identifier("raw", table)
    )

    with db_connection.cursor() as cursor:
        cursor.execute(query)
        actual = cursor.fetchone()[0]

    assert actual == expected, (
        f"{table}: expected {expected}, found {actual}"
    )


@pytest.mark.parametrize(
    "table, key",
    list(PRIMARY_KEYS.items()),
)
def test_primary_key_integrity(db_connection, table, key):
    """Primary keys must be unique and non-null."""

    query = sql.SQL(
        """
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT {}) AS unique_keys,
            COUNT(*) FILTER (
                WHERE {} IS NULL
            ) AS null_keys
        FROM {}
        """
    ).format(
        sql.Identifier(key),
        sql.Identifier(key),
        sql.Identifier("raw", table),
    )

    with db_connection.cursor() as cursor:
        cursor.execute(query)
        total, unique, nulls = cursor.fetchone()

    assert nulls == 0, (
        f"{table}.{key}: found {nulls} null keys"
    )

    assert total == unique, (
        f"{table}.{key}: duplicate keys found"
    )


def test_financial_reconciliation(db_connection):
    """
    Reconcile financial totals at reporting precision.

    Source values are preserved at six decimal places.
    Financial report references use two decimal places.

    Rounding is applied after aggregation, never to
    individual sales records.
    """

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                ROUND(SUM("Sales Amount"), 2),
                ROUND(SUM("Total Product Cost"), 2),
                ROUND(
                    SUM(
                        "Sales Amount"
                        - "Total Product Cost"
                    ),
                    2
                )
            FROM raw.sales
            """
        )

        revenue, cost, profit = cursor.fetchone()

    assert revenue == EXPECTED_REVENUE, (
        f"Revenue mismatch: "
        f"expected {EXPECTED_REVENUE}, "
        f"found {revenue}"
    )

    assert cost == EXPECTED_COST, (
        f"Cost mismatch: "
        f"expected {EXPECTED_COST}, "
        f"found {cost}"
    )

    assert profit == EXPECTED_PROFIT, (
        f"Gross profit mismatch: "
        f"expected {EXPECTED_PROFIT}, "
        f"found {profit}"
    )

    assert profit == revenue - cost, (
        "Rounded gross profit does not reconcile "
        "with rounded revenue and cost."
    )


def test_sales_order_relationship(db_connection):
    """Every sales line must have a matching order line."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM raw.sales AS s
            LEFT JOIN raw.orders AS o
                ON s."SalesOrderLineKey" =
                   o."SalesOrderLineKey"
            WHERE o."SalesOrderLineKey" IS NULL
            """
        )

        missing = cursor.fetchone()[0]

    assert missing == 0, (
        f"Found {missing} unmatched sales lines"
    )


def test_sales_channel_distribution(db_connection):
    """Validate the known channel distribution."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                o."Channel",
                COUNT(*)
            FROM raw.sales AS s
            JOIN raw.orders AS o
                ON s."SalesOrderLineKey" =
                   o."SalesOrderLineKey"
            GROUP BY o."Channel"
            """
        )

        actual = dict(cursor.fetchall())

    expected = {
        "Internet": 60398,
        "Reseller": 60855,
    }

    assert actual == expected, (
        f"Channel distribution mismatch: {actual}"
    )


def test_special_customer_reseller_keys(db_connection):
    """Validate channel-specific placeholder key usage."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*) FILTER (
                    WHERE o."Channel" = 'Internet'
                      AND s."ResellerKey" = -1
                      AND s."CustomerKey" <> -1
                ),
                COUNT(*) FILTER (
                    WHERE o."Channel" = 'Reseller'
                      AND s."CustomerKey" = -1
                      AND s."ResellerKey" <> -1
                )
            FROM raw.sales AS s
            JOIN raw.orders AS o
                ON s."SalesOrderLineKey" =
                   o."SalesOrderLineKey"
            """
        )

        internet, reseller = cursor.fetchone()

    assert internet == 60398, (
        f"Internet placeholder mismatch: {internet}"
    )

    assert reseller == 60855, (
        f"Reseller placeholder mismatch: {reseller}"
    )


def test_shipping_date_nulls(db_connection):
    """Verify the documented missing shipping dates."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM raw.sales
            WHERE "ShipDateKey" IS NULL
            """
        )

        actual = cursor.fetchone()[0]

    assert actual == 2113, (
        f"Expected 2113 missing shipping dates, "
        f"found {actual}"
    )


def test_product_color_nulls(db_connection):
    """Verify the documented missing product colors."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM raw.products
            WHERE "Color" IS NULL
            """
        )

        actual = cursor.fetchone()[0]

    assert actual == 56, (
        f"Expected 56 missing product colors, "
        f"found {actual}"
    )


def test_sales_date_coverage(db_connection):
    """Verify the observed sales date range."""

    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                MIN(d."Date"),
                MAX(d."Date"),
                COUNT(*) FILTER (
                    WHERE d."Date" IS NULL
                )
            FROM raw.sales AS s
            LEFT JOIN raw.dates AS d
                ON s."OrderDateKey" = d."DateKey"
            """
        )

        first_date, last_date, missing = cursor.fetchone()

    assert str(first_date) == "2017-07-01", (
        f"Unexpected first sales date: {first_date}"
    )

    assert str(last_date) == "2020-06-15", (
        f"Unexpected last sales date: {last_date}"
    )

    assert missing == 0, (
        f"Found {missing} sales with invalid dates"
    )
