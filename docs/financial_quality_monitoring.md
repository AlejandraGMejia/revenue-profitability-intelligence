# Financial Data Quality & Monitoring

## Project
Revenue & Profitability Intelligence

## Sprint 07 - Integrated Quality Pipeline

### Objective

Implement a reproducible financial data quality
pipeline using Python, pytest, dbt Core and PostgreSQL.

The pipeline separates technical validation failures
from financial anomalies requiring business review.

## Architecture

Python Unit Tests
       |
       v
dbt Build and Data Tests
       |
       v
Financial Quality Monitor
       |
       v
JSON and Markdown Reports

## Components

### Python Unit Tests

File: tests/test_financial_quality_monitor.py

Four automated tests validate:

- Expected monitoring results
- Detection of RAW-to-mart row mismatches
- Detection of missing keys and incorrect profit calculations
- JSON and Markdown report generation

These tests simulate database responses and do not
modify PostgreSQL.

### dbt Validation

The dbt project contains:

- 13 analytical models
- 46 data tests
- 7 declared sources

The successful build completed 59 operations
with zero errors and zero warnings.

### Financial Quality Monitor

File: scripts/monitor_financial_quality.py

The monitor checks:

1. RAW-to-mart record reconciliation
2. Non-empty analytical fact
3. Required analytical keys
4. Gross profit reconciliation
5. Recorded revenue formula differences
6. Negative gross profit lines
7. Reseller gross margin

## Monitoring Status

PASS: Technical validation succeeded.

WARN: Financial observation requiring review.

FAIL: Technical data quality validation failed.

Financial warnings do not automatically stop
the pipeline.

The 2% Reseller margin threshold is illustrative
and is not an approved business target.

## Validated Execution Results

Python unit tests: 4 passed

dbt:
- PASS: 59
- WARN: 0
- ERROR: 0

Financial monitor:
- PASS: 4
- WARN: 3
- FAIL: 0

RAW sales rows: 121,253
Analytical fact rows: 121,253

Observed financial anomalies:
- Revenue formula differences: 3,282 lines
- Negative gross profit: 21,829 lines
- Reseller gross margin: 0.58%

These observations do not establish their
underlying business causes.

## Execution

Requirements:

- PostgreSQL running locally
- Python environment: .venv
- dbt environment: .venv-dbt
- Private dbt profile:
  ~/.config/revenue-intelligence-dbt/profiles.yml

From the project root:

    ./scripts/run_quality_pipeline.sh

The script requests the PostgreSQL password
interactively when needed.

The pipeline stops if a technical stage fails.

## Generated Reports

- reports/monitoring/latest_quality_report.json
- reports/monitoring/latest_quality_report.md

The reports represent the most recent local execution,
not continuous real-time monitoring.

## Security

Database credentials are not stored in the repository.

The dbt profile is maintained outside Git.

The monitor uses read-only SQL queries.

## Limitations

The pipeline is executed on demand.

Scheduled execution, notification delivery,
historical monitoring and alert escalation
are not implemented in this sprint.

A successful execution confirms the implemented
checks, not the absence of every possible data
quality or business issue.
