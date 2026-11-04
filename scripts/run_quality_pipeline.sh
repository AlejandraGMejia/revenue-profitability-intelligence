#!/usr/bin/env bash

# Revenue & Profitability Intelligence
# Sprint 08 - Automated Quality Pipeline

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

for required in \
    "$DBT" \
    "$PYTHON" \
    "$DBT_PROFILES_DIR/profiles.yml" \
    "$ROOT/scripts/monitor_financial_quality.py" \
    "$ROOT/scripts/archive_quality_report.py" \
    "$ROOT/scripts/compare_quality_history.py"
do
    if [[ ! -f "$required" ]]; then
        echo "ERROR: Missing file: $required" >&2
        exit 2
    fi
done

# Authentication priority:
# 1. Existing environment variable
# 2. systemd-managed credential
# 3. Interactive password prompt

if [[ -n "${DBT_PG_PASSWORD:-}" ]]; then
    echo "Authentication: environment"

elif [[ -n "${CREDENTIALS_DIRECTORY:-}" ]]; then
    CREDENTIAL_FILE="$CREDENTIALS_DIRECTORY/postgres_password"

    if [[ ! -f "$CREDENTIAL_FILE" ]]; then
        echo "ERROR: Missing systemd credential." >&2
        exit 2
    fi

    DBT_PG_PASSWORD="$(cat "$CREDENTIAL_FILE")"

    if [[ -z "$DBT_PG_PASSWORD" ]]; then
        echo "ERROR: Empty systemd credential." >&2
        exit 2
    fi

    echo "Authentication: systemd credential"

else
    if [[ ! -t 0 ]]; then
        echo "ERROR: No credential available." >&2
        exit 2
    fi

    read -rsp \
        "PostgreSQL password for revenue_app: " \
        DBT_PG_PASSWORD
    echo

    if [[ -z "$DBT_PG_PASSWORD" ]]; then
        echo "ERROR: Empty password." >&2
        exit 2
    fi

    echo "Authentication: interactive"
fi

export DBT_PG_PASSWORD
export PGPASSWORD="$DBT_PG_PASSWORD"

echo
echo "[1/5] Running Python unit tests..."
"$PYTHON" -m pytest \
    tests/test_financial_quality_monitor.py -q

echo
echo "[2/5] Building and testing dbt models..."
"$DBT" build \
    --project-dir "$ROOT" \
    --profiles-dir "$DBT_PROFILES_DIR"

echo
echo "[3/5] Running financial quality monitor..."
"$PYTHON" scripts/monitor_financial_quality.py

echo
echo "[4/5] Archiving monitoring results..."
"$PYTHON" scripts/archive_quality_report.py

echo
echo "[5/5] Comparing monitoring history..."
"$PYTHON" scripts/compare_quality_history.py

echo
echo "========================================"
echo " PIPELINE COMPLETED SUCCESSFULLY"
echo "========================================"
