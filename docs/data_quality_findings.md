
# Data Quality Findings
## Revenue & Profitability Intelligence

### Finding DQ-001: Sales Amount Discrepancies

**Status:** Investigated - Business rule not confirmed
**Severity:** Medium
**Source:** AdventureWorks Sales Sample

### Summary
The financial audit identified 3,282 sales records
where the recorded Sales Amount is lower than the
amount expected from Extended Amount and the
reported Unit Price Discount Pct.

### Evidence
- Total sales records: 121,253
- Flagged records: 3,282 (2.71%)
- Affected channel: Reseller
- Affected Reseller records: 5.39%
- Internet records affected: 0
- Total absolute difference: approximately $527,507.89

### Effective Reduction Patterns
- 2%: 1,310 records
- 5%: 606 records
- 10%: 178 records
- 15%: 590 records
- 20%: 231 records
- 30%: 61 records
- 35%: 137 records
- 40%: 169 records

### Interpretation
The differences are systematic and concentrated
in the Reseller channel.

The effective reductions suggest additional
commercial pricing rules not represented by
the reported discount percentage.

The exact business explanation remains unconfirmed.

### Analytical Decision
1. Preserve original source values.
2. Use Sales Amount for recorded revenue.
3. Use Total Product Cost for estimated COGS.
4. Derive effective reduction separately.
5. Do not infer a contractual discount from
   the effective reduction.
6. Do not remove flagged records.
7. Document this limitation in financial reports.

### Other Findings
- 2,113 missing shipping date references.
- 56 missing product colors.
- No duplicate primary keys detected.
- No unmatched non-null foreign keys detected.
- No negative sales or costs detected.

### Follow-up
Validate placeholder dimension keys, investigate
missing shipping dates, and review date coverage
before final approval of the analytical model.
