# Financial Exploratory Data Analysis
## Revenue & Profitability Intelligence

**Dataset:** Microsoft AdventureWorks Sales Sample
**Analysis period:** 2018–2019 (full calendar years)
**Database:** PostgreSQL
**Analytical layer:** dbt Core

---

## 1. Executive Summary

AdventureWorks shows substantially different financial
performance between Internet and Reseller channels.

Internet maintains strong estimated gross margins,
while Reseller generates much higher revenue but
relatively little gross profit.

The investigation identified three major patterns:

1. Internet sales expanded into lower-value product
   categories during 2019.
2. Reseller Bikes generated increasing gross losses
   between 2018 and 2019.
3. Sales lines with unexplained formula differences
   are strongly associated with negative gross profit.

These findings justify further investigation of
product pricing, costs and commercial policies.

---

## 2. Financial Performance

### Internet

| Metric | 2018 | 2019 |
|---|---:|---:|
| Revenue | $6,372,462.14 | $10,692,440.08 |
| Gross Profit | $2,590,257.45 | $4,443,963.94 |
| Gross Margin | 40.65% | 41.56% |
| Sales Lines | 2,733 | 28,784 |

### Reseller

| Metric | 2018 | 2019 |
|---|---:|---:|
| Revenue | $24,144,429.65 | $32,202,669.43 |
| Gross Profit | $323,401.79 | -$168,557.73 |
| Gross Margin | 1.34% | -0.52% |
| Sales Lines | 16,676 | 26,758 |

**Finding:** Higher Reseller revenue did not result
in improved estimated gross profitability.

---

## 3. Internet Product Mix

In 2018, 100% of Internet sales lines were Bikes.

In 2019, the line distribution was:

- Bikes: 21.70%
- Accessories: 62.73%
- Clothing: 15.58%

Average revenue per sales line declined from
$2,331.67 in 2018 to $371.47 in 2019.

Despite their smaller share of sales lines,
Bikes still generated 95.16% of Internet revenue
in 2019.

**Interpretation:** The changing product mix
helps explain the lower average revenue per line.

This does not demonstrate an equivalent decline
in individual product selling prices.

---

## 4. Reseller Bikes Profitability

| Metric | 2018 | 2019 |
|---|---:|---:|
| Revenue | $19,956,014.67 | $25,551,775.07 |
| Gross Profit | -$233,047.15 | -$782,382.73 |
| Gross Margin | -1.17% | -3.06% |
| Loss-Making Lines | 3,800 | 6,809 |

Bikes became a larger source of estimated gross
loss despite generating higher recorded revenue.

---

## 5. Geographic Findings

All ten recorded sales territories showed
negative aggregate gross profit for Reseller
Bikes during 2019.

Largest absolute losses in 2019:

| Territory | Gross Profit |
|---|---:|
| US Southwest | -$174,937.36 |
| Germany | -$112,456.15 |
| Australia | -$112,035.35 |
| France | -$104,300.37 |
| Canada | -$74,676.88 |

These are assigned sales territories, not
necessarily customer residential locations.

The pattern suggests a multi-territory issue,
but it does not establish a single root cause.

---

## 6. Formula Difference Investigation

A formula difference indicates that recorded
revenue differs from:

Extended Amount * (1 - Declared Discount Rate)

For Reseller Bikes:

### 2018

- Flagged lines: 296
- Formula differences: $178,175.83
- Flagged-line gross profit: -$770,803.76
- Other-line gross profit: +$537,756.61

### 2019

- Flagged lines: 881
- Formula differences: $276,065.98
- Flagged-line gross profit: -$1,007,071.61
- Other-line gross profit: +$224,688.88

**Interpretation:** Flagged lines are associated
with substantial negative gross profit.

However, the formula differences are not confirmed
contractual discounts, and their presence alone
does not prove the cause of the losses.

The actual recorded revenue must be preserved.

---

## 7. Temporal Data Quality

The analysis uses 2018 and 2019 as comparable
complete calendar years.

March 2018 has no recorded Reseller sales.

Calendar months without transactions are retained
with zero recorded revenue in the monthly analysis.

The full source also contains partial boundary
years, which should not be compared directly
with complete years without qualification.

---

## 8. Recommendations for Further Investigation

1. Review pricing and cost assumptions for
   loss-making Reseller Bike products.

2. Investigate the commercial rules behind
   recorded formula differences.

3. Compare profitability by product, territory
   and reporting period.

4. Evaluate the effect of Internet product mix
   changes on average revenue per line.

5. Build dashboard alerts for negative gross
   margins and unusual financial differences.

These are analytical recommendations rather than
confirmed operational root causes.

---

## 9. Technical Methodology

Data sources:
- PostgreSQL RAW tables
- dbt staging models
- dbt fact and dimension views

Methods:
- SQL joins and aggregations
- Common Table Expressions
- Window functions
- Complete calendar generation
- Financial reconciliation
- Python and Pandas
- Matplotlib charts

Supporting SQL:
- sql/eda/01_financial_performance.sql
- sql/eda/02_product_mix_analysis.sql
- sql/eda/03_geographic_profitability.sql

Visualization script:
- scripts/financial_eda.py

Chart outputs:
- reports/figures/annual_revenue_by_channel.png
- reports/figures/annual_gross_margin.png
- reports/figures/monthly_revenue_trend.png
- reports/figures/monthly_gross_profit.png

---

## 10. Limitations

- AdventureWorks is a fictional business dataset.
- Gross profit uses recorded product costs.
- Results do not represent net profit.
- The pricing difference mechanism is unconfirmed.
- Statistical causality has not been established.
- Geographic analysis uses assigned territories.
- The report represents the source snapshot tested.

---

## Conclusion

The investigation demonstrates that revenue growth
alone is not sufficient to evaluate business
performance.

Channel mix, product composition, cost structure
and transactional anomalies must be analyzed
together to support reliable financial decisions.
