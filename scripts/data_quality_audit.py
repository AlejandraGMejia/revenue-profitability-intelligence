
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data/raw/adventureworks/adventureworks_sales.xlsx"
REPORT = ROOT / "reports/data_quality_report.md"

SHEETS = {
    "Sales_data": "sales",
    "Product_data": "products",
    "Customer_data": "customers",
    "Reseller_data": "resellers",
    "Date_data": "dates",
    "Sales Territory_data": "territories",
    "Sales Order_data": "orders",
}

RELATIONSHIPS = [
    ("ProductKey", "products", "ProductKey"),
    ("CustomerKey", "customers", "CustomerKey"),
    ("ResellerKey", "resellers", "ResellerKey"),
    ("OrderDateKey", "dates", "DateKey"),
    ("DueDateKey", "dates", "DateKey"),
    ("ShipDateKey", "dates", "DateKey"),
    ("SalesTerritoryKey", "territories", "SalesTerritoryKey"),
    ("SalesOrderLineKey", "orders", "SalesOrderLineKey"),
]


def load_data():
    if not DATASET.is_file():
        raise FileNotFoundError(f"Dataset not found: {DATASET}")

    print("Loading AdventureWorks dataset...")

    workbook = pd.read_excel(
        DATASET,
        sheet_name=list(SHEETS),
        engine="openpyxl",
    )

    return {
        SHEETS[name]: dataframe
        for name, dataframe in workbook.items()
    }


def audit_tables(tables, results):
    results.append("## 1. Table Quality")
    results.append("")

    for name, df in tables.items():
        rows = len(df)
        nulls = int(df.isna().sum().sum())
        duplicates = int(df.duplicated().sum())

        results.append(f"### {name}")
        results.append(f"- Rows: {rows:,}")
        results.append(f"- Columns: {len(df.columns)}")
        results.append(f"- Null cells: {nulls:,}")
        results.append(f"- Duplicate full rows: {duplicates:,}")

        missing = df.isna().sum()
        missing = missing[missing > 0].sort_values(
            ascending=False
        )

        if not missing.empty:
            results.append("- Missing values by column:")

            for column, count in missing.items():
                results.append(
                    f"  - {column}: {int(count):,}"
                )

        results.append("")


def audit_keys(tables, results):
    results.append("## 2. Primary Key Checks")
    results.append("")

    keys = {
        "sales": "SalesOrderLineKey",
        "products": "ProductKey",
        "customers": "CustomerKey",
        "resellers": "ResellerKey",
        "dates": "DateKey",
        "territories": "SalesTerritoryKey",
        "orders": "SalesOrderLineKey",
    }

    for table, key in keys.items():
        df = tables[table]

        if key not in df.columns:
            results.append(
                f"- {table}.{key}: COLUMN MISSING"
            )
            continue

        missing = int(df[key].isna().sum())
        duplicates = int(
            df[key].dropna().duplicated().sum()
        )

        results.append(
            f"- {table}.{key}: "
            f"{missing:,} nulls, "
            f"{duplicates:,} duplicates"
        )

    results.append("")


def audit_relationships(tables, results):
    results.append("## 3. Referential Integrity")
    results.append("")

    sales = tables["sales"]

    for source_key, target_table, target_key in RELATIONSHIPS:
        if (
            source_key not in sales.columns
            or target_key not in tables[target_table].columns
        ):
            results.append(
                f"- {source_key}: COLUMN MISSING"
            )
            continue

        source = sales[source_key]
        valid_keys = (
            tables[target_table][target_key].dropna()
        )

        missing = int(source.isna().sum())

        unmatched = int(
            (~source.dropna().isin(valid_keys)).sum()
        )

        results.append(
            f"- {source_key} -> "
            f"{target_table}.{target_key}: "
            f"{missing:,} null references, "
            f"{unmatched:,} unmatched non-null references"
        )

    results.append("")
    results.append(
        "Note: Null customer, reseller or date references "
        "require business-rule review before classification."
    )
    results.append("")


def audit_financials(tables, results):
    results.append("## 4. Financial Quality")
    results.append("")

    sales = tables["sales"]

    numeric_columns = [
        "Order Quantity",
        "Unit Price",
        "Extended Amount",
        "Unit Price Discount Pct",
        "Product Standard Cost",
        "Total Product Cost",
        "Sales Amount",
    ]

    values = {}

    for column in numeric_columns:
        if column not in sales.columns:
            results.append(
                f"- Missing column: {column}"
            )
            return

        values[column] = pd.to_numeric(
            sales[column],
            errors="coerce",
        )

        invalid = int(
            (
                sales[column].notna()
                & values[column].isna()
            ).sum()
        )

        results.append(
            f"- {column}: {invalid:,} nonnumeric values"
        )

    quantity = values["Order Quantity"]
    price = values["Unit Price"]
    extended = values["Extended Amount"]
    discount = values["Unit Price Discount Pct"]
    standard_cost = values["Product Standard Cost"]
    total_cost = values["Total Product Cost"]
    revenue = values["Sales Amount"]

    results.append("")
    results.append(
        f"- Total sales amount: {revenue.sum():,.2f}"
    )
    results.append(
        f"- Total product cost: {total_cost.sum():,.2f}"
    )
    results.append(
        f"- Estimated gross profit: "
        f"{(revenue - total_cost).sum():,.2f}"
    )

    checks = {
        "Nonpositive quantity": quantity.le(0),
        "Negative unit price": price.lt(0),
        "Negative revenue": revenue.lt(0),
        "Negative total cost": total_cost.lt(0),
        "Discount outside 0-1": (
            discount.lt(0) | discount.gt(1)
        ),
        "Extended amount mismatch": (
            (extended - quantity * price)
            .abs()
            .gt(0.02)
        ),
        "Standard cost mismatch": (
            (total_cost - quantity * standard_cost)
            .abs()
            .gt(0.02)
        ),
        "Sales amount formula mismatch": (
            (
                revenue
                - extended * (1 - discount)
            )
            .abs()
            .gt(0.02)
        ),
    }

    results.append("")
    results.append("### Financial Validation Checks")
    results.append("")

    for name, mask in checks.items():
        count = int(mask.fillna(False).sum())
        results.append(f"- {name}: {count:,}")

    results.append("")
    results.append(
        "Formula mismatches are diagnostic flags, "
        "not confirmed errors. Source business rules "
        "and rounding must be validated."
    )
    results.append("")


def audit_dates(tables, results):
    results.append("## 5. Temporal Coverage")
    results.append("")

    dates = tables["dates"]

    if "Date" in dates.columns:
        parsed = pd.to_datetime(
            dates["Date"],
            errors="coerce",
        )

        results.append(
            f"- Calendar start: {parsed.min()}"
        )
        results.append(
            f"- Calendar end: {parsed.max()}"
        )
        results.append(
            f"- Invalid date values: "
            f"{int(dates['Date'].notna().sum() - parsed.notna().sum()):,}"
        )

    sales = tables["sales"]

    for column in [
        "OrderDateKey",
        "DueDateKey",
        "ShipDateKey",
    ]:
        if column in sales.columns:
            results.append(
                f"- {column} nulls: "
                f"{int(sales[column].isna().sum()):,}"
            )

    results.append("")


def main():
    tables = load_data()

    results = [
        "# AdventureWorks Data Quality Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Dataset Overview",
        "",
        f"- Tables: {len(tables)}",
        f"- Sales rows: {len(tables['sales']):,}",
        "",
    ]

    audit_tables(tables, results)
    audit_keys(tables, results)
    audit_relationships(tables, results)
    audit_financials(tables, results)
    audit_dates(tables, results)

    results.extend([
        "## Assessment Notes",
        "",
        "- Results are preliminary automated diagnostics.",
        "- Null values are not automatically defects.",
        "- Full-row duplicates and duplicate business keys differ.",
        "- Cost-based profit is an estimate until validated.",
        "- Investigate flagged records before remediation.",
    ])

    REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_content = "\n".join(results).rstrip() + "\n"

    REPORT.write_text(
        report_content,
        encoding="utf-8",
    )

    print("\nDATA QUALITY AUDIT COMPLETED")
    print(f"Tables analyzed: {len(tables)}")
    print(
        f"Sales rows analyzed: {len(tables['sales']):,}"
    )
    print(f"Report generated: {REPORT}")


if __name__ == "__main__":
    main()
