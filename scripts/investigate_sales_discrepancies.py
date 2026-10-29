
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

DATASET = (
    ROOT
    / "data/raw/adventureworks/adventureworks_sales.xlsx"
)

REPORTS = ROOT / "reports"
TOLERANCE = 0.02


def main():
    if not DATASET.is_file():
        raise FileNotFoundError(DATASET)

    print("Loading sales data...")

    df = pd.read_excel(
        DATASET,
        sheet_name="Sales_data",
        engine="openpyxl",
    )

    required = [
        "SalesOrderLineKey",
        "Order Quantity",
        "Unit Price",
        "Extended Amount",
        "Unit Price Discount Pct",
        "Sales Amount",
    ]

    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    for column in required:
        df[column] = pd.to_numeric(
            df[column],
            errors="raise",
        )

    df["expected_sales"] = (
        df["Extended Amount"]
        * (1 - df["Unit Price Discount Pct"])
    )

    df["difference"] = (
        df["Sales Amount"] - df["expected_sales"]
    )

    df["absolute_difference"] = df["difference"].abs()

    discrepancies = df.loc[
        df["absolute_difference"] > TOLERANCE
    ].copy()

    print("\n" + "=" * 60)
    print("SALES DISCREPANCY INVESTIGATION")
    print("=" * 60)

    print(f"Total rows: {len(df):,}")
    print(f"Flagged rows: {len(discrepancies):,}")

    print(
        "Flagged percentage: "
        f"{len(discrepancies) / len(df) * 100:.2f}%"
    )

    print("\nDifference statistics:")
    print(discrepancies["difference"].describe().to_string())

    print("\nAbsolute difference statistics:")
    print(
        discrepancies["absolute_difference"]
        .describe()
        .to_string()
    )

    print("\nDiscount rates among flagged rows:")
    print(
        discrepancies["Unit Price Discount Pct"]
        .value_counts(dropna=False)
        .head(15)
        .to_string()
    )

    print("\nDifference direction:")
    print(
        "Positive:",
        int((discrepancies["difference"] > 0).sum()),
    )
    print(
        "Negative:",
        int((discrepancies["difference"] < 0).sum()),
    )

    print("\nTotal signed difference:")
    print(f"{discrepancies['difference'].sum():,.2f}")

    print("\nTotal absolute difference:")
    print(
        f"{discrepancies['absolute_difference'].sum():,.2f}"
    )

    print("\nLargest discrepancies:")

    columns = [
        "SalesOrderLineKey",
        "Order Quantity",
        "Unit Price",
        "Extended Amount",
        "Unit Price Discount Pct",
        "Sales Amount",
        "expected_sales",
        "difference",
    ]

    top = discrepancies.nlargest(
        10, "absolute_difference"
    )

    print(top[columns].to_string(index=False))

    REPORTS.mkdir(parents=True, exist_ok=True)

    output = REPORTS / "sales_discrepancies.csv"

    discrepancies[columns + ["absolute_difference"]].to_csv(
        output,
        index=False,
    )

    print(f"\nDetailed report: {output}")
    print("Investigation completed.")


if __name__ == "__main__":
    main()
