
from pathlib import Path

from openpyxl import load_workbook


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "adventureworks"
    / "adventureworks_sales.xlsx"
)


def inspect_dataset() -> None:
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    print("=" * 65)
    print("ADVENTUREWORKS - INITIAL DATA PROFILING")
    print("=" * 65)

    workbook = load_workbook(
        filename=DATASET_PATH,
        read_only=True,
        data_only=True,
    )

    try:
        print(f"\nTotal worksheets: {len(workbook.sheetnames)}")

        for sheet in workbook.worksheets:
            print("\n" + "-" * 65)
            print(f"Worksheet: {sheet.title}")
            print(f"Reported rows: {sheet.max_row}")
            print(f"Reported columns: {sheet.max_column}")

            first_row = next(
                sheet.iter_rows(
                    min_row=1,
                    max_row=1,
                    values_only=True,
                ),
                (),
            )

            columns = [
                str(value) if value is not None else "<EMPTY>"
                for value in first_row
            ]

            print("First row values:")
            for index, column in enumerate(columns, start=1):
                print(f"  {index}. {column}")

    finally:
        workbook.close()

    print("\nInspection completed.")


if __name__ == "__main__":
    inspect_dataset()
