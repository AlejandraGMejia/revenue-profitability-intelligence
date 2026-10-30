
"""
AdventureWorks RAW Data Loader.

Loads seven Excel worksheets into PostgreSQL using
a single transaction and validates the results.

The source workbook is never modified.
"""

from datetime import datetime, date
from decimal import Decimal
from getpass import getpass
from pathlib import Path
import os

import pandas as pd
import psycopg
from psycopg import sql


ROOT = Path(__file__).resolve().parents[1]

DATASET = (
    ROOT
    / "data"
    / "raw"
    / "adventureworks"
    / "adventureworks_sales.xlsx"
)

DB_NAME = "revenue_intelligence"
DB_USER = "revenue_app"
DB_HOST = "localhost"
DB_PORT = 5432
DB_SCHEMA = "raw"

SHEETS = {
    "Product_data": "products",
    "Customer_data": "customers",
    "Reseller_data": "resellers",
    "Date_data": "dates",
    "Sales Territory_data": "territories",
    "Sales Order_data": "orders",
    "Sales_data": "sales",
}

EXPECTED_COLUMNS = {
    "products": [
        "ProductKey", "SKU", "Product",
        "Standard Cost", "Color", "List Price",
        "Model", "Subcategory", "Category",
    ],
    "customers": [
        "CustomerKey", "Customer ID", "Customer",
        "City", "State-Province",
        "Country-Region", "Postal Code",
    ],
    "resellers": [
        "ResellerKey", "Reseller ID", "Business Type",
        "Reseller", "City", "State-Province",
        "Country-Region", "Postal Code",
    ],
    "dates": [
        "DateKey", "Date", "Fiscal Year",
        "Fiscal Quarter", "Month",
        "Full Date", "MonthKey",
    ],
    "territories": [
        "SalesTerritoryKey", "Region",
        "Country", "Group",
    ],
    "orders": [
        "Channel", "SalesOrderLineKey",
        "Sales Order", "Sales Order Line",
    ],
    "sales": [
        "SalesOrderLineKey", "ResellerKey",
        "CustomerKey", "ProductKey",
        "OrderDateKey", "DueDateKey",
        "ShipDateKey", "SalesTerritoryKey",
        "Order Quantity", "Unit Price",
        "Extended Amount", "Unit Price Discount Pct",
        "Product Standard Cost",
        "Total Product Cost", "Sales Amount",
    ],
}

DECIMAL_COLUMNS = {
    "products": {
        "Standard Cost", "List Price",
    },
    "sales": {
        "Unit Price", "Extended Amount",
        "Unit Price Discount Pct",
        "Product Standard Cost",
        "Total Product Cost", "Sales Amount",
    },
}

DATE_COLUMNS = {
    "dates": {"Date"},
}

INTEGER_COLUMNS = {
    "products": {"ProductKey"},
    "customers": {"CustomerKey"},
    "resellers": {"ResellerKey"},
    "dates": {"DateKey", "MonthKey"},
    "territories": {"SalesTerritoryKey"},
    "orders": {"SalesOrderLineKey"},
    "sales": {
        "SalesOrderLineKey", "ResellerKey",
        "CustomerKey", "ProductKey",
        "OrderDateKey", "DueDateKey",
        "ShipDateKey", "SalesTerritoryKey",
        "Order Quantity",
    },
}

DECIMAL_SCALE = Decimal("0.000001")


def normalize_value(value, column, table):
    """Convert Pandas values into PostgreSQL-compatible types."""

    if pd.isna(value):
        return None

    if column in DECIMAL_COLUMNS.get(table, set()):
        decimal_value = Decimal(str(value))

        if not decimal_value.is_finite():
            raise ValueError(
                f"Non-finite decimal in {table}.{column}"
            )

        return decimal_value.quantize(DECIMAL_SCALE)

    if column in INTEGER_COLUMNS.get(table, set()):
        number = Decimal(str(value))

        if not number.is_finite():
            raise ValueError(
                f"Non-finite integer in {table}.{column}"
            )

        if number != number.to_integral_value():
            raise ValueError(
                f"Non-integer value in {table}.{column}: {value}"
            )

        return int(number)

    if column in DATE_COLUMNS.get(table, set()):
        if isinstance(value, pd.Timestamp):
            return value.date()

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        parsed = pd.to_datetime(value, errors="raise")
        return parsed.date()

    return str(value)


def load_workbook():
    """Read and verify the original workbook."""

    if not DATASET.is_file():
        raise FileNotFoundError(
            f"Source workbook not found: {DATASET}"
        )

    print("Reading AdventureWorks workbook...")

    workbook = pd.read_excel(
        DATASET,
        sheet_name=list(SHEETS.keys()),
        engine="openpyxl",
    )

    tables = {}

    for sheet, table in SHEETS.items():
        df = workbook[sheet]

        actual = list(df.columns)
        expected = EXPECTED_COLUMNS[table]

        if actual != expected:
            raise ValueError(
                f"Column mismatch in {table}.\n"
                f"Expected: {expected}\n"
                f"Actual: {actual}"
            )

        tables[table] = df

        print(
            f"  {table}: {len(df):,} source rows"
        )

    return tables


def validate_database_structure(conn):
    """Verify the destination tables and column order."""

    print("\nValidating PostgreSQL structure...")

    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        ORDER BY ordinal_position
    """

    with conn.cursor() as cur:
        for table, expected in EXPECTED_COLUMNS.items():
            cur.execute(query, (DB_SCHEMA, table))

            actual = [
                row[0] for row in cur.fetchall()
            ]

            if actual != expected:
                raise ValueError(
                    f"PostgreSQL schema mismatch: {table}\n"
                    f"Expected: {expected}\n"
                    f"Actual: {actual}"
                )

    print("All seven destination tables match.")


def load_table(conn, table, df):
    """Bulk-copy one source table into PostgreSQL."""

    columns = EXPECTED_COLUMNS[table]

    command = sql.SQL(
        "COPY {} ({}) FROM STDIN"
    ).format(
        sql.Identifier(DB_SCHEMA, table),
        sql.SQL(", ").join(
            sql.Identifier(column)
            for column in columns
        ),
    )

    print(f"Loading {table}...")

    with conn.cursor() as cur:
        with cur.copy(command) as copy:
            for row in df.itertuples(
                index=False,
                name=None,
            ):
                values = [
                    normalize_value(value, column, table)
                    for value, column in zip(row, columns)
                ]

                copy.write_row(tuple(values))

    print(f"  Copied {len(df):,} rows.")


def source_financial_totals(df):
    """Calculate totals using the destination decimal scale."""

    columns = [
        "Sales Amount",
        "Total Product Cost",
    ]

    totals = {}

    for column in columns:
        total = Decimal("0")

        for value in df[column]:
            normalized = normalize_value(
                value, column, "sales"
            )

            if normalized is not None:
                total += normalized

        totals[column] = total

    return totals


def validate_loaded_data(conn, tables):
    """Check row counts and financial totals before commit."""

    print("\nVALIDATING POSTGRESQL DATA")
    print("=" * 60)

    with conn.cursor() as cur:
        for table, df in tables.items():
            query = sql.SQL(
                "SELECT COUNT(*) FROM {}"
            ).format(
                sql.Identifier(DB_SCHEMA, table)
            )

            cur.execute(query)
            actual_count = cur.fetchone()[0]

            expected_count = len(df)

            if actual_count != expected_count:
                raise ValueError(
                    f"Row count mismatch in {table}: "
                    f"expected {expected_count}, "
                    f"found {actual_count}"
                )

            print(
                f"{table}: {actual_count:,} rows - OK"
            )

        cur.execute(
            """
            SELECT
                SUM("Sales Amount"),
                SUM("Total Product Cost")
            FROM raw.sales
            """
        )

        db_revenue, db_cost = cur.fetchone()

    expected = source_financial_totals(tables["sales"])

    expected_revenue = expected["Sales Amount"]
    expected_cost = expected["Total Product Cost"]

    if db_revenue != expected_revenue:
        raise ValueError(
            "Revenue totals do not match.\n"
            f"Source: {expected_revenue}\n"
            f"Database: {db_revenue}"
        )

    if db_cost != expected_cost:
        raise ValueError(
            "Cost totals do not match.\n"
            f"Source: {expected_cost}\n"
            f"Database: {db_cost}"
        )

    gross_profit = db_revenue - db_cost

    print("\nFINANCIAL RECONCILIATION")
    print("=" * 60)
    print(f"Revenue: {db_revenue:,.2f}")
    print(f"Product cost: {db_cost:,.2f}")
    print(f"Estimated gross profit: {gross_profit:,.2f}")
    print("Financial reconciliation: PASSED")


def main():
    print("=" * 60)
    print("ADVENTUREWORKS - RAW DATA LOADER")
    print("=" * 60)

    tables = load_workbook()

    password = os.environ.get("PGPASSWORD")

    if not password:
        password = getpass(
            "\nPostgreSQL password for revenue_app: "
        )

    print("\nConnecting to PostgreSQL...")

    with psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=password,
        connect_timeout=10,
    ) as conn:

        # All operations below share one transaction.
        # If anything fails, PostgreSQL rolls it back.

        validate_database_structure(conn)

        print("\nPreparing repeatable RAW load...")

        with conn.cursor() as cur:
            cur.execute(
                """
                TRUNCATE TABLE
                    raw.sales,
                    raw.orders,
                    raw.products,
                    raw.customers,
                    raw.resellers,
                    raw.dates,
                    raw.territories
                """
            )

        for table, df in tables.items():
            load_table(conn, table, df)

        validate_loaded_data(conn, tables)

        # Connection context commits only if
        # the entire load finishes successfully.

    print("\n" + "=" * 60)
    print("RAW DATA LOAD COMPLETED SUCCESSFULLY")
    print("All validations passed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
