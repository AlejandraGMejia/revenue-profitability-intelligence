#!/usr/bin/env bash

# Revenue & Profitability Intelligence
# Sprint 09 - Reliable Financial Quality Pipeline

set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DBT="$ROOT/.venv-dbt/bin/dbt"
PYTHON="$ROOT/.venv/bin/python"
DBT_PROFILES_DIR="$HOME/.config/revenue-intelligence-dbt"

RUN_ID="run_$(date -u +%Y%m%dT%H%M%S%NZ)_$$"

cd "$ROOT"

cleanup() {
    unset DBT_PG_PASSWORD PGPASSWORD
}

trap cleanup EXIT

record_event() {
    "$PYTHON" scripts/pipeline_events.py record \
        --run-id "$RUN_ID" \
        "$@"
}

show_summary() {
    "$PYTHON" scripts/pipeline_events.py summary \
        --run-id "$RUN_ID"
}

run_stage() {
    local stage="$1"
    local description="$2"
    local result

    shift 2

    echo
    echo "========================================"
    echo "$description"
    echo "========================================"

    record_event \
        --stage "$stage" \
        --status STARTED

    if "$@"; then
        record_event \
            --stage "$stage" \
            --status SUCCESS
    else
        result=$?

        echo "ERROR: Stage '$stage' failed."
        echo "Exit code: $result"

        record_event \
            --stage "$stage" \
            --status FAILED \
            --exit-code "$result" || true

        show_summary || true

        return "$result"
    fi
}

build_dbt() {
    echo "Checking PostgreSQL connectivity..."

    # Only connectivity receives bounded retries.
    # A failed dbt build is not automatically retried.
    if ! "$PYTHON" scripts/check_database_connection.py; then
        echo "ERROR: PostgreSQL preflight failed." >&2
        return 1
    fi

    echo "PostgreSQL preflight passed."
    echo "Building and testing dbt models..."

    "$DBT" build \
        --project-dir "$ROOT" \
        --profiles-dir "$DBT_PROFILES_DIR"
}

echo "========================================"
echo " REVENUE FINANCIAL QUALITY PIPELINE"
echo "========================================"
echo "Execution ID: $RUN_ID"

for required in \
    "$DBT" \
    "$PYTHON" \
    "$DBT_PROFILES_DIR/profiles.yml" \
    "$ROOT/scripts/pipeline_events.py" \
    "$ROOT/scripts/check_database_connection.py" \
    "$ROOT/scripts/monitor_financial_quality.py" \
    "$ROOT/scripts/archive_quality_report.py" \
    "$ROOT/scripts/compare_quality_history.py"
do
    if [[ ! -f "$required" ]]; then
        echo "ERROR: Missing file: $required" >&2
        exit 2
    fi
done

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

run_stage \
    pytest \
    "[1/5] Running all Python unit tests" \
    "$PYTHON" -m pytest \
    tests/test_financial_quality_monitor.py \
    tests/test_pipeline_events.py \
    tests/test_database_connection.py \
    -q

run_stage \
    dbt \
    "[2/5] PostgreSQL preflight and dbt build" \
    build_dbt

run_stage \
    financial_monitor \
    "[3/5] Running financial quality monitor" \
    "$PYTHON" scripts/monitor_financial_quality.py

run_stage \
    archive \
    "[4/5] Archiving monitoring results" \
    "$PYTHON" scripts/archive_quality_report.py

run_stage \
    comparison \
    "[5/5] Comparing monitoring history" \
    "$PYTHON" scripts/compare_quality_history.py

echo
echo "========================================"
echo " PIPELINE COMPLETED SUCCESSFULLY"
echo "========================================"

show_summary
