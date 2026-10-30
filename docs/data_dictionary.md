# AdventureWorks Data Dictionary

## Source

Microsoft AdventureWorks Sales Sample.

Data types are inferred by Pandas during ingestion.
Database types will be defined separately.

## sales

Rows: 121,253

| Column | Inferred Type | Nulls | Role |
|---|---|---:|---|
| SalesOrderLineKey | int64 | 0 | Primary key |
| ResellerKey | int64 | 0 | Foreign key -> resellers.ResellerKey |
| CustomerKey | int64 | 0 | Foreign key -> customers.CustomerKey |
| ProductKey | int64 | 0 | Foreign key -> products.ProductKey |
| OrderDateKey | int64 | 0 | Foreign key -> dates.DateKey |
| DueDateKey | int64 | 0 | Foreign key -> dates.DateKey |
| ShipDateKey | float64 | 2,113 | Foreign key -> dates.DateKey |
| SalesTerritoryKey | int64 | 0 | Foreign key -> territories.SalesTerritoryKey |
| Order Quantity | int64 | 0 | Attribute / Measure |
| Unit Price | float64 | 0 | Attribute / Measure |
| Extended Amount | float64 | 0 | Attribute / Measure |
| Unit Price Discount Pct | int64 | 0 | Attribute / Measure |
| Product Standard Cost | float64 | 0 | Attribute / Measure |
| Total Product Cost | float64 | 0 | Attribute / Measure |
| Sales Amount | float64 | 0 | Attribute / Measure |

## products

Rows: 397

| Column | Inferred Type | Nulls | Role |
|---|---|---:|---|
| ProductKey | int64 | 0 | Primary key |
| SKU | str | 0 | Attribute / Measure |
| Product | str | 0 | Attribute / Measure |
| Standard Cost | float64 | 0 | Attribute / Measure |
| Color | str | 56 | Attribute / Measure |
| List Price | float64 | 0 | Attribute / Measure |
| Model | str | 0 | Attribute / Measure |
| Subcategory | str | 0 | Attribute / Measure |
| Category | str | 0 | Attribute / Measure |

## customers

Rows: 18,485

| Column | Inferred Type | Nulls | Role |
|---|---|---:|---|
| CustomerKey | int64 | 0 | Primary key |
| Customer ID | str | 0 | Attribute / Measure |
| Customer | str | 0 | Attribute / Measure |
| City | str | 0 | Attribute / Measure |
| State-Province | str | 0 | Attribute / Measure |
| Country-Region | str | 0 | Attribute / Measure |
| Postal Code | str | 0 | Attribute / Measure |

## resellers

Rows: 702

| Column | Inferred Type | Nulls | Role |
|---|---|---:|---|
| ResellerKey | int64 | 0 | Primary key |
| Reseller ID | str | 0 | Attribute / Measure |
| Business Type | str | 0 | Attribute / Measure |
| Reseller | str | 0 | Attribute / Measure |
| City | str | 0 | Attribute / Measure |
| State-Province | str | 0 | Attribute / Measure |
| Country-Region | str | 0 | Attribute / Measure |
| Postal Code | str | 0 | Attribute / Measure |

## dates

Rows: 1,461

| Column | Inferred Type | Nulls | Role |
|---|---|---:|---|
| DateKey | int64 | 0 | Primary key |
| Date | datetime64[us] | 0 | Attribute / Measure |
| Fiscal Year | str | 0 | Attribute / Measure |
| Fiscal Quarter | str | 0 | Attribute / Measure |
| Month | str | 0 | Attribute / Measure |
| Full Date | str | 0 | Attribute / Measure |
| MonthKey | int64 | 0 | Attribute / Measure |

## territories

Rows: 11

| Column | Inferred Type | Nulls | Role |
|---|---|---:|---|
| SalesTerritoryKey | int64 | 0 | Primary key |
| Region | str | 0 | Attribute / Measure |
| Country | str | 0 | Attribute / Measure |
| Group | str | 0 | Attribute / Measure |

## orders

Rows: 121,253

| Column | Inferred Type | Nulls | Role |
|---|---|---:|---|
| Channel | str | 0 | Attribute / Measure |
| SalesOrderLineKey | int64 | 0 | Primary key |
| Sales Order | str | 0 | Attribute / Measure |
| Sales Order Line | str | 0 | Attribute / Measure |
