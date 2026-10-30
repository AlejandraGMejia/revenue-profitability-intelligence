# AdventureWorks Final Dataset Validation

Generated: 2026-10-30T21:08:55.702545+00:00

## Dataset Overview

- Tables: 7
- Sales rows: 121,253

## Special Key Validation

Checks for null, zero and negative-one values.
These values require business interpretation.

| Column | Null | Zero | Minus One |
|---|---:|---:|---:|
| SalesOrderLineKey | 0 | 0 | 0 |
| ProductKey | 0 | 0 | 0 |
| CustomerKey | 0 | 0 | 60,855 |
| ResellerKey | 0 | 0 | 60,398 |
| OrderDateKey | 0 | 0 | 0 |
| DueDateKey | 0 | 0 | 0 |
| ShipDateKey | 2,113 | 0 | 0 |
| SalesTerritoryKey | 0 | 0 | 0 |

## Sales Date Coverage

- Earliest sale: 2017-07-01 00:00:00
- Latest sale: 2020-06-15 00:00:00
- Unmapped or invalid sale dates: 0

### Sales Rows by Year

- 2017: 5,339
- 2018: 19,409
- 2019: 55,542
- 2020: 40,963

## Sales Grain Validation

- Sales rows: 121,253
- Unique sales line keys: 121,253
- Duplicate sales line keys: 0
- Unmatched order lines: 0

### Sales Channel Distribution

- Reseller: 60,855
- Internet: 60,398

### Proposed Fact Table Grain

One record per SalesOrderLineKey.

## Validation Notes

- Special keys require source-level interpretation.
- The sales grain is evaluated using line keys.
- Date coverage is based on actual sales.
- This report complements the quality audit.
- Financial business rules remain documented.
