
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

DATASET = (
    ROOT
    / "data"
    / "raw"
    / "adventureworks"
    / "adventureworks_sales.xlsx"
)

DOCS = ROOT / "docs"
REPORTS = ROOT / "reports"

SHEETS = {
    "Sales_data": "sales",
    "Product_data": "products",
    "Customer_data": "customers",
    "Reseller_data": "resellers",
    "Date_data": "dates",
    "Sales Territory_data": "territories",
    "Sales Order_data": "orders",
}

PRIMARY_KEYS = {
    "sales": "SalesOrderLineKey",
    "products": "ProductKey",
    "customers": "CustomerKey",
    "resellers": "ResellerKey",
    "dates": "DateKey",
    "territories": "SalesTerritoryKey",
    "orders": "SalesOrderLineKey",
}

FOREIGN_KEYS = {
    "sales": {
        "SalesOrderLineKey": "orders.SalesOrderLineKey",
        "ProductKey": "products.ProductKey",
        "CustomerKey": "customers.CustomerKey",
        "ResellerKey": "resellers.ResellerKey",
        "OrderDateKey": "dates.DateKey",
        "DueDateKey": "dates.DateKey",
        "ShipDateKey": "dates.DateKey",
        "SalesTerritoryKey": "territories.SalesTerritoryKey",
    }
}

SPECIAL_VALUES = [-1, 0]


def load_data():
    if not DATASET.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET}"
        )

    print("Loading AdventureWorks...")

    workbook = pd.read_excel(
        DATASET,
        sheet_name=list(SHEETS.keys()),
        engine="openpyxl",
    )

    return {
        SHEETS[sheet]: dataframe
        for sheet, dataframe in workbook.items()
    }


def get_column_role(table_name, column):
    if PRIMARY_KEYS.get(table_name) == column:
        return "Primary key"

    reference = FOREIGN_KEYS.get(
        table_name, {}
    ).get(column)

    if reference:
        return f"Foreign key -> {reference}"

    return "Attribute / Measure"


def generate_dictionary(tables):
    lines = [
        "# AdventureWorks Data Dictionary",
        "",
        "## Source",
        "",
        "Microsoft AdventureWorks Sales Sample.",
        "",
        "Data types are inferred by Pandas during ingestion.",
        "Database types will be defined separately.",
        "",
    ]

    for table_name, df in tables.items():
        lines.extend([
            f"## {table_name}",
            "",
            f"Rows: {len(df):,}",
            "",
            "| Column | Inferred Type | Nulls | Role |",
            "|---|---|---:|---|",
        ])

        for column in df.columns:
            dtype = str(df[column].dtype)
            null_count = int(df[column].isna().sum())
            role = get_column_role(table_name, column)

            lines.append(
                f"| {column} | {dtype} | "
                f"{null_count:,} | {role} |"
            )

        lines.append("")

    DOCS.mkdir(parents=True, exist_ok=True)

    output = DOCS / "data_dictionary.md"

    output.write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
    )

    return output


def validate_special_keys(tables):
    sales = tables["sales"]

    lines = [
        "## Special Key Validation",
        "",
        "Checks for null, zero and negative-one values.",
        "These values require business interpretation.",
        "",
        "| Column | Null | Zero | Minus One |",
        "|---|---:|---:|---:|",
    ]

    for column in FOREIGN_KEYS["sales"]:
        if column not in sales.columns:
            continue

        values = pd.to_numeric(
            sales[column],
            errors="coerce",
        )

        nulls = int(sales[column].isna().sum())
        zeros = int(values.eq(0).sum())
        minus_ones = int(values.eq(-1).sum())

        lines.append(
            f"| {column} | {nulls:,} | "
            f"{zeros:,} | {minus_ones:,} |"
        )

    lines.append("")

    return lines


def validate_dates(tables):
    sales = tables["sales"]
    calendar = tables["dates"]

    date_lookup = calendar[
        ["DateKey", "Date"]
    ].copy()

    date_lookup["Date"] = pd.to_datetime(
        date_lookup["Date"],
        errors="coerce",
    )

    combined = sales[
        ["OrderDateKey"]
    ].merge(
        date_lookup,
        left_on="OrderDateKey",
        right_on="DateKey",
        how="left",
        validate="many_to_one",
    )

    dates = combined["Date"]

    lines = [
        "## Sales Date Coverage",
        "",
        f"- Earliest sale: {dates.min()}",
        f"- Latest sale: {dates.max()}",
        f"- Unmapped or invalid sale dates: "
        f"{int(dates.isna().sum()):,}",
        "",
        "### Sales Rows by Year",
        "",
    ]

    year_counts = (
        dates.dt.year
        .value_counts(dropna=False)
        .sort_index()
    )

    for year, count in year_counts.items():
        label = (
            "Missing"
            if pd.isna(year)
            else str(int(year))
        )

        lines.append(
            f"- {label}: {int(count):,}"
        )

    lines.append("")

    return lines


def validate_grain(tables):
    sales = tables["sales"]
    orders = tables["orders"]

    key = "SalesOrderLineKey"

    unique_lines = sales[key].nunique()
    duplicate_lines = int(
        sales[key].duplicated().sum()
    )

    joined = sales[[key]].merge(
        orders[[key, "Channel"]],
        on=key,
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    unmatched = int(
        joined["_merge"].ne("both").sum()
    )

    lines = [
        "## Sales Grain Validation",
        "",
        f"- Sales rows: {len(sales):,}",
        f"- Unique sales line keys: {unique_lines:,}",
        f"- Duplicate sales line keys: {duplicate_lines:,}",
        f"- Unmatched order lines: {unmatched:,}",
        "",
        "### Sales Channel Distribution",
        "",
    ]

    counts = (
        joined["Channel"]
        .value_counts(dropna=False)
    )

    for channel, count in counts.items():
        lines.append(
            f"- {channel}: {int(count):,}"
        )

    lines.extend([
        "",
        "### Proposed Fact Table Grain",
        "",
        "One record per SalesOrderLineKey.",
        "",
    ])

    return lines


def main():
    tables = load_data()

    print("Generating data dictionary...")

    dictionary_path = generate_dictionary(tables)

    report = [
        "# AdventureWorks Final Dataset Validation",
        "",
        "Generated: "
        f"{datetime.now(timezone.utc).isoformat()}",
        "",
        "## Dataset Overview",
        "",
        f"- Tables: {len(tables)}",
        f"- Sales rows: {len(tables['sales']):,}",
        "",
    ]

    report.extend(validate_special_keys(tables))
    report.extend(validate_dates(tables))
    report.extend(validate_grain(tables))

    report.extend([
        "## Validation Notes",
        "",
        "- Special keys require source-level interpretation.",
        "- The sales grain is evaluated using line keys.",
        "- Date coverage is based on actual sales.",
        "- This report complements the quality audit.",
        "- Financial business rules remain documented.",
    ])

    REPORTS.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = (
        REPORTS / "final_dataset_validation.md"
    )

    report_path.write_text(
        "\n".join(report).rstrip() + "\n",
        encoding="utf-8",
    )

    print("\nVALIDATION COMPLETED")
    print(f"Tables validated: {len(tables)}")
    print(f"Data dictionary: {dictionary_path}")
    print(f"Validation report: {report_path}")


if __name__ == "__main__":
    main()
