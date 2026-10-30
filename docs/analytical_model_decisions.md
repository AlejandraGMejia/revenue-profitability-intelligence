
# Analytical Model Decisions

## Revenue & Profitability Intelligence

### 1. Dataset

Source: Microsoft AdventureWorks Sales Sample

- Source tables: 7
- Sales records: 121,253
- Earliest sale: 2017-07-01
- Latest sale: 2020-06-15
- Sales channels: Internet and Reseller

### 2. Fact Table Grain

The proposed fact table is `fact_sales`.

Grain:
One record per SalesOrderLineKey.

Validation:
- Sales records: 121,253
- Unique SalesOrderLineKey values: 121,253
- Duplicate sales line keys: 0

### 3. Proposed Dimensions

- dim_product
- dim_customer
- dim_reseller
- dim_date
- dim_territory
- dim_sales_order

Dimension names and relationships are provisional
until PostgreSQL and dbt models are implemented.

### 4. Special Key Handling

Two complementary placeholder-key patterns
were identified:

- CustomerKey = -1: 60,855 records
- ResellerKey = -1: 60,398 records

These counts correspond to the Reseller and
Internet channel totals, respectively.

The channel-to-placeholder relationship must be
confirmed through row-level validation.

Placeholder keys must not be treated as
missing or invalid without business context.

### 5. Financial Metric Definitions

Revenue:
SUM(Sales Amount)

Estimated Cost of Goods Sold:
SUM(Total Product Cost)

Estimated Gross Profit:
Revenue - Estimated COGS

Estimated Gross Margin:
Estimated Gross Profit / Revenue

Average Order Value:
Revenue / COUNT(DISTINCT Sales Order)

Order identifiers and financial business rules
must be validated before final implementation.

### 6. Discount Investigation

3,282 Reseller sales lines show an unexplained
difference between recorded Sales Amount and
the amount derived from Extended Amount and
Unit Price Discount Pct.

- Affected sales lines: 2.71%
- Affected channel: Reseller
- Total signed difference: -527,507.89

Decision:
Preserve recorded revenue and report the
effective reduction separately.

The underlying business rule is not yet confirmed.

### 7. Temporal Considerations

Sales cover 2017-07-01 through 2020-06-15.

The calendar dimension extends beyond
the latest observed sales date.

2020 contains partial-year sales data.

Year-over-year comparisons must use equivalent
periods or explicitly label partial periods.

### 8. Data Quality Decisions

- Preserve original source data.
- Do not remove special dimension keys.
- Do not fabricate missing shipping dates.
- Preserve records with unexplained price reductions.
- Apply documented tests during transformations.
- Distinguish estimated gross profit from net profit.

### 9. Next Stage

Implement a PostgreSQL analytical database
and develop tested dbt transformation models.

The analytical model will support Power BI,
financial reporting, and scenario analysis.
