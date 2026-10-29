
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data/raw/adventureworks/adventureworks_sales.xlsx"

TOLERANCE = 0.02


def main():
    print("Loading sales and order data...")

    tables = pd.read_excel(
        DATASET,
        sheet_name=["Sales_data", "Sales Order_data"],
        engine="openpyxl",
    )

    sales = tables["Sales_data"]
    orders = tables["Sales Order_data"]

    df = sales.merge(
        orders[["SalesOrderLineKey", "Channel"]],
        on="SalesOrderLineKey",
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    print("\nJOIN VALIDATION")
    print(df["_merge"].value_counts().to_string())
    print(f"Rows after join: {len(df):,}")

    df["expected_sales"] = (
        df["Extended Amount"]
        * (1 - df["Unit Price Discount Pct"])
    )

    df["difference"] = (
        df["Sales Amount"] - df["expected_sales"]
    )

    df["flagged"] = df["difference"].abs() > TOLERANCE

    df["effective_reduction_pct"] = (
        (1 - df["Sales Amount"] / df["Extended Amount"])
        .where(df["Extended Amount"] > 0)
        * 100
    )

    flagged = df.loc[df["flagged"]].copy()

    flagged["reduction_rounded"] = (
        flagged["effective_reduction_pct"].round(2)
    )

    print("\n" + "=" * 60)
    print("DISCOUNT PATTERN ANALYSIS")
    print("=" * 60)

    print("\nFlagged sales by channel:")
    print(
        df.groupby("Channel", dropna=False)["flagged"]
        .agg(["sum", "count", "mean"])
        .to_string()
    )

    print("\nMost common effective reductions (%):")
    print(
        flagged["reduction_rounded"]
        .value_counts()
        .head(20)
        .to_string()
    )

    print("\nFinancial impact by channel:")
    print(
        flagged.groupby("Channel", dropna=False)
        .agg(
            affected_rows=("SalesOrderLineKey", "count"),
            signed_difference=("difference", "sum"),
            recorded_revenue=("Sales Amount", "sum"),
            expected_revenue=("expected_sales", "sum"),
        )
        .round(2)
        .to_string()
    )

    print("\nOverall effective reduction statistics:")
    print(
        flagged["effective_reduction_pct"]
        .describe()
        .round(4)
        .to_string()
    )

    print("\nAnalysis completed.")


if __name__ == "__main__":
    main()
