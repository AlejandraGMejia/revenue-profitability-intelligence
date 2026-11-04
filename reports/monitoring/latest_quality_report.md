# Financial Data Quality Monitoring

Generated (UTC): 2026-11-04T00:34:01+00:00

## Summary

- PASS: 4
- WARN: 3
- FAIL: 0

## Results

| Check | Status | Value |
|---|---|---|
| Raw-to-mart row reconciliation | PASS | raw=121253, fact=121253 |
| Non-empty analytical fact | PASS | 121253 |
| Required analytical keys | PASS | 0 |
| Gross profit reconciliation | PASS | 0 |
| Recorded revenue formula differences | WARN | 3282 |
| Negative gross profit lines | WARN | 21829 |
| Reseller gross margin observation | WARN | 0.58% |

## Interpretation

FAIL indicates a technical data quality problem.

WARN highlights an observation requiring review.

Warnings are not automatically pipeline failures.

All queries use read-only database access.
