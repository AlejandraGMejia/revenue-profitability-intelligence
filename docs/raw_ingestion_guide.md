
# RAW Data Ingestion Guide

## Revenue & Profitability Intelligence

### 1. Overview

This project implements a reproducible ELT ingestion
pipeline using Python and PostgreSQL.

The pipeline loads seven worksheets from the Microsoft
AdventureWorks Sales Sample into a dedicated RAW schema.

The source dataset remains unchanged.

### 2. Technology Stack

- Python 3.14
- PostgreSQL 18
- Pandas
- openpyxl
- Psycopg 3
- pytest
- Git

### 3. Project Architecture

AdventureWorks Excel
    |
    v
Python Data Loader
    |
    v
PostgreSQL: raw schema
    |
    v
Automated Data Quality Tests
    |
    v
dbt Transformations (next sprint)

### 4. Source Dataset

Source: Microsoft AdventureWorks Sales Sample

Expected source tables:

| Table | Expected Rows |
|---|---:|
| products | 397 |
| customers | 18,485 |
| resellers | 702 |
| dates | 1,461 |
| territories | 11 |
| orders | 121,253 |
| sales | 121,253 |
| **Total** | **263,562** |

The source workbook is stored locally at:

data/raw/adventureworks/adventureworks_sales.xlsx

Raw source files are excluded from Git.

### 5. Environment Setup

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
python -m pip install -r requirements.txt
```

### 6. PostgreSQL Setup

Start PostgreSQL:

```bash
sudo systemctl start postgresql
pg_isready
```

Provision a dedicated database and login role using
PostgreSQL administrative privileges:

```sql
CREATE ROLE revenue_app WITH LOGIN;

CREATE DATABASE revenue_intelligence
OWNER revenue_app;
```

Configure the role password interactively in psql:

```text
\password revenue_app
```

For TCP connections from localhost, configure
password-based authentication using SCRAM-SHA-256.

The exact pg_hba.conf rules depend on the local
PostgreSQL installation. Preserve unrelated rules.

Never commit database passwords.

### 7. Database Initialization

Execute the schema creation script:

```bash
psql -X -v ON_ERROR_STOP=1 \
  -h localhost \
  -U revenue_app \
  -d revenue_intelligence \
  -f sql/01_create_raw_schema.sql
```

Create the seven RAW tables:

```bash
psql -X -v ON_ERROR_STOP=1 \
  -h localhost \
  -U revenue_app \
  -d revenue_intelligence \
  -f sql/02_create_raw_tables.sql
```

### 8. Data Ingestion

Run the Python loader:

```bash
python scripts/load_raw_data.py
```

The loader:

1. Reads the original Excel workbook.
2. Validates worksheet columns.
3. Converts data into PostgreSQL-compatible types.
4. Replaces the existing RAW snapshot transactionally.
5. Loads records using PostgreSQL COPY.
6. Validates record counts.
7. Reconciles financial totals.
8. Commits only when all validations succeed.

The password is requested interactively unless
PGPASSWORD is already provided in the environment.

Important: this is a full-refresh loader.

Successful reruns replace all seven RAW tables.
It is not an incremental ingestion pipeline.

### 9. Financial Reconciliation

Expected totals at two-decimal reporting precision:

| Metric | Expected Value |
|---|---:|
| Revenue | 109,809,274.20 |
| Product Cost | 97,257,907.95 |
| Estimated Gross Profit | 12,551,366.25 |

Financial columns are stored using NUMERIC(20,6).

The reporting layer rounds aggregated values
to two decimal places.

Gross profit is based on the product costs supplied
by the sample dataset and is not audited net profit.

### 10. Automated Testing

Execute the RAW database test suite:

```bash
python -m pytest tests/test_raw_database.py -v -s
```

The current suite contains 21 test cases covering:

- Source snapshot row counts
- Primary key integrity
- Financial reconciliation
- Sales-order relationships
- Sales channel distribution
- Placeholder key patterns
- Documented missing values
- Sales date coverage

Last verified result:

21 passed

The tests are designed for the current
AdventureWorks source snapshot.

Historical row counts and expected totals must
be reviewed when the source dataset changes.

### 11. Data Quality Findings

The initial source audit identified:

- 2,113 missing shipping date references
- 56 missing product colors
- 3,282 sales amount formula discrepancies
- No duplicate primary keys
- No unmatched non-null foreign keys

The sales amount discrepancies occur exclusively
in the Reseller channel.

Their exact commercial explanation is unconfirmed.

Original recorded sales values are preserved.

Further details:

docs/data_quality_findings.md

### 12. Security and Reproducibility

- Store credentials outside version control.
- Use a dedicated database role.
- Keep raw datasets outside Git.
- Maintain dependencies in requirements.txt.
- Version SQL scripts and Python source code.
- Validate database results after ingestion.
- Do not modify original source records.

### 13. Known Limitations

- The source is a fictional sample dataset.
- The pipeline currently supports full refreshes.
- The loader targets a local PostgreSQL instance.
- Historical snapshot expectations are hardcoded
  into the current regression tests.
- The RAW schema does not enforce foreign keys.
- Business transformations are not implemented here.
- Deployment automation is outside this sprint.

### 14. Next Sprint

Sprint 03 will implement the analytical database
foundation and dimensional modeling.

Planned work includes:

- SQL analytical modeling
- Fact and dimension design
- PostgreSQL transformations
- Data model validation
- Preparation for dbt Core

The goal is to develop trustworthy financial
models that can support BI dashboards.
