# AdventureWorks Data Quality Report

Generated: 2026-10-29T01:09:35.533267+00:00

## Dataset Overview

- Tables: 7
- Sales rows: 121,253

## 1. Table Quality

### sales
- Rows: 121,253
- Columns: 15
- Null cells: 2,113
- Duplicate full rows: 0
- Missing values by column:
  - ShipDateKey: 2,113

### products
- Rows: 397
- Columns: 9
- Null cells: 56
- Duplicate full rows: 0
- Missing values by column:
  - Color: 56

### customers
- Rows: 18,485
- Columns: 7
- Null cells: 0
- Duplicate full rows: 0

### resellers
- Rows: 702
- Columns: 8
- Null cells: 0
- Duplicate full rows: 0

### dates
- Rows: 1,461
- Columns: 7
- Null cells: 0
- Duplicate full rows: 0

### territories
- Rows: 11
- Columns: 4
- Null cells: 0
- Duplicate full rows: 0

### orders
- Rows: 121,253
- Columns: 4
- Null cells: 0
- Duplicate full rows: 0

## 2. Primary Key Checks

- sales.SalesOrderLineKey: 0 nulls, 0 duplicates
- products.ProductKey: 0 nulls, 0 duplicates
- customers.CustomerKey: 0 nulls, 0 duplicates
- resellers.ResellerKey: 0 nulls, 0 duplicates
- dates.DateKey: 0 nulls, 0 duplicates
- territories.SalesTerritoryKey: 0 nulls, 0 duplicates
- orders.SalesOrderLineKey: 0 nulls, 0 duplicates

## 3. Referential Integrity

- ProductKey -> products.ProductKey: 0 null references, 0 unmatched non-null references
- CustomerKey -> customers.CustomerKey: 0 null references, 0 unmatched non-null references
- ResellerKey -> resellers.ResellerKey: 0 null references, 0 unmatched non-null references
- OrderDateKey -> dates.DateKey: 0 null references, 0 unmatched non-null references
- DueDateKey -> dates.DateKey: 0 null references, 0 unmatched non-null references
- ShipDateKey -> dates.DateKey: 2,113 null references, 0 unmatched non-null references
- SalesTerritoryKey -> territories.SalesTerritoryKey: 0 null references, 0 unmatched non-null references
- SalesOrderLineKey -> orders.SalesOrderLineKey: 0 null references, 0 unmatched non-null references

Note: Null customer, reseller or date references require business-rule review before classification.

## 4. Financial Quality

- Order Quantity: 0 nonnumeric values
- Unit Price: 0 nonnumeric values
- Extended Amount: 0 nonnumeric values
- Unit Price Discount Pct: 0 nonnumeric values
- Product Standard Cost: 0 nonnumeric values
- Total Product Cost: 0 nonnumeric values
- Sales Amount: 0 nonnumeric values

- Total sales amount: 109,809,274.20
- Total product cost: 97,257,907.95
- Estimated gross profit: 12,551,366.25

### Financial Validation Checks

- Nonpositive quantity: 0
- Negative unit price: 0
- Negative revenue: 0
- Negative total cost: 0
- Discount outside 0-1: 0
- Extended amount mismatch: 0
- Standard cost mismatch: 0
- Sales amount formula mismatch: 3,282

Formula mismatches are diagnostic flags, not confirmed errors. Source business rules and rounding must be validated.

## 5. Temporal Coverage

- Calendar start: 2017-07-01 00:00:00
- Calendar end: 2021-06-30 00:00:00
- Invalid date values: 0
- OrderDateKey nulls: 0
- DueDateKey nulls: 0
- ShipDateKey nulls: 2,113

## Assessment Notes

- Results are preliminary automated diagnostics.
- Null values are not automatically defects.
- Full-row duplicates and duplicate business keys differ.
- Cost-based profit is an estimate until validated.
- Investigate flagged records before remediation.
