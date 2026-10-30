
# Dimensional Model Guide
## Revenue & Profitability Intelligence

### 1. Objective

Build a financial analytical model that supports
revenue, product cost, gross profitability,
channel performance, and business reporting.

### 2. Architecture

Source: Microsoft AdventureWorks Sales Sample

Database: revenue_intelligence

Layers:
- raw: original ingested source records
- marts: analytical SQL views

The marts layer contains five dimensions
and one sales fact view.

### 3. Fact Model

Model: marts.fact_sales

Grain:
One record per SalesOrderLineKey.

Validated fact rows: 121,253

Core measures:
- revenue
- total_product_cost
- gross_profit
- order_quantity
- formula_difference
- effective_reduction_rate

The fact view also contains sales channel,
order identifiers, date keys, and dimension keys.

### 4. Dimensions

- dim_product: product attributes and categories
- dim_customer: customer attributes
- dim_reseller: distributor attributes
- dim_date: calendar and fiscal attributes
- dim_territory: geographical sales attributes

Source placeholder keys are preserved.

Internet sales use ResellerKey = -1.
Reseller sales use CustomerKey = -1.

### 5. Financial Definitions

Revenue:
SUM(revenue)

Estimated Product Cost:
SUM(total_product_cost)

Estimated Gross Profit:
SUM(gross_profit)

Estimated Gross Margin:
SUM(gross_profit) / NULLIF(SUM(revenue), 0)

Gross profit is not equivalent to net profit.

Reported financial totals are rounded after
aggregation, not at individual line level.

### 6. Validated Results

Total recorded revenue:
109,809,274.20

Total product cost:
97,257,907.95

Estimated gross profit:
12,551,366.25

Sales lines with negative gross profit:
21,829

### 7. Business Findings

Internet gross margin: 41.15%

Reseller gross margin: 0.58%

Reseller Bikes estimated gross profit:
-990,699.89

Reseller June 2018 gross profit:
-605,204.44

Three months contain no Reseller sales:
- October 2017
- December 2017
- March 2018

There are 3,282 sales formula discrepancies
concentrated in the Reseller channel.

These discrepancies are diagnostic findings.
Their exact underlying business rule remains
unconfirmed.

### 8. Temporal Considerations

Observed sales:
2017-07-01 through 2020-06-15

June 2020 is a partial month.

Monthly reporting should include calendar
periods with no transactions.

Month-over-month calculations must distinguish
missing months from consecutive calendar months.

### 9. SQL Techniques

The project demonstrates:
- Common Table Expressions (CTEs)
- INNER JOIN and LEFT JOIN
- Conditional aggregation with FILTER
- Window functions
- LAG
- RANK
- ROW_NUMBER
- Cumulative totals
- Financial reconciliation
- Dimensional integrity validation

### 10. Automated Testing

RAW layer:
21 previously passed tests.

Analytical layer:
20 passed tests.

Analytical tests validate:
- View existence
- Dimension uniqueness
- Fact grain
- Financial reconciliation
- Referential integrity
- Channel placeholder rules
- Financial anomaly classification
- Historical reporting patterns

Tests are tied to the current source snapshot.
Expected values must be reviewed if source
data changes.

### 11. Limitations

- AdventureWorks is a fictional sample business.
- Product costs are used for estimated gross profit.
- Commercial price reductions remain unexplained.
- The analytical models are currently SQL views.
- The current SQL model is not yet managed by dbt.
- No production deployment is claimed.

### 12. Next Sprint

Sprint 04: Analytics Engineering with dbt Core.

Planned work:
- dbt project initialization
- Source definitions
- Staging transformations
- Fact and dimension models
- Schema and relationship tests
- Model documentation and lineage
- Financial reconciliation
