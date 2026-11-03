#!/usr/bin/env bash

# Revenue & Profitability Intelligence
# Sprint 07 - Integrated Financial Quality Pipeline

set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DBT="$ROOT/.venv-dbt/bin/dbt"
PYTHON="$ROOT/.venv/bin/python"

DBT_PROFILES_DIR="$HOME/.config/revenue-intelligence-dbt"

cd "$ROOT"

cleanup() {
    unset DBT_PG_PASSWORD PGPASSWORD
}

trap cleanup EXIT

echo "========================================"
echo " REVENUE FINANCIAL QUALITY PIPELINE"
echo "========================================"

# Verify dependencies before execution.
for required in \
    "$DBT" \
    "$PYTHON" \
    "$DBT_PROFILES_DIR/profiles.yml"
do
    if [[ ! -f "$required" ]]; then
        echo "ERROR: Missing required file: $required" >&2
        exit 2
    fi
done

# Prompt for the database password once.
if [[ -z "${DBT_PG_PASSWORD:-}" ]]; then
    read -rsp \
        "PostgreSQL password for revenue_app: " \
        DBT_PG_PASSWORD
    echo
fi

# Share the password with dbt and psycopg.
export DBT_PG_PASSWORD
export PGPASSWORD="$DBT_PG_PASSWORD"

echo
echo "[1/3] Running Python unit tests..."

"$PYTHON" -m pytest \
    tests/test_financial_quality_monitor.py \
    -q

echo
echo "[2/3] Building and testing dbt models..."

"$DBT" build \
    --project-dir "$ROOT" \
    --profiles-dir "$DBT_PROFILES_DIR"

echo
echo "[3/3] Running financial quality monitor..."

"$PYTHON" scripts/monitor_financial_quality.py

echo
echo "========================================"
echo " PIPELINE COMPLETED SUCCESSFULLY"
echo "========================================"

echo
echo "Generated reports:"
echo "- reports/monitoring/latest_quality_report.json"
echo "- reports/monitoring/latest_quality_report.md"
