# Financial Quality Pipeline - Operations Runbook

## Project

Revenue & Profitability Intelligence

## Sprint 09 - Reliability & Recovery

## Purpose

Document how to diagnose pipeline failures,
review operational events, and recover safely.

## Pipeline Architecture

The pipeline performs five stages:

1. Python unit tests
2. PostgreSQL preflight and dbt build
3. Financial quality monitoring
4. Monitoring report archiving
5. Historical comparison

Each stage records STARTED, SUCCESS, or FAILED.

Execution events are stored locally in:

    reports/monitoring/operations/

## Validated Results

- Python unit tests: 14 passed
- dbt: 13 models and 46 data tests
- Financial monitor: 4 PASS, 3 WARN, 0 FAIL
- Historical monitoring: 6 executions recognized
- systemd service: successful execution
- systemd timer: active

A simulated dbt failure was also recorded correctly.

## Database Connection Recovery

Before dbt build, the pipeline checks PostgreSQL
connectivity using:

    scripts/check_database_connection.py

The preflight executes a read-only SELECT 1 query.

Retry policy:

- Maximum attempts: 3
- Delay between attempts: 2 seconds
- Transient connection errors may be retried
- Authentication errors with a non-retryable SQLSTATE
  stop the preflight
- Failed dbt data tests are never automatically retried

The recovery mechanism was tested using simulated
connections and a successful live connection.

A real database outage was not induced.

## Failure Classification

### Python Test Failure

Inspect pytest output and correct the failing code.

Do not retry blindly.

### dbt Test Failure

Investigate source data, model logic, relationships,
or financial reconciliation.

Do not disable data quality tests to force success.

### PostgreSQL Connection Failure

Check PostgreSQL:

    systemctl is-active postgresql

Inspect the service logs and private connection
configuration.

Never print or commit passwords.

The preflight already provides limited retries
for transient connection errors.

### Financial Monitor Failure

Investigate the failing SQL query, model availability,
or reconciliation check.

Business WARN observations do not automatically
indicate a technical failure.

### Archiving Failure

Preserve the latest reports and investigate
filesystem permissions or available disk space.

### Historical Comparison Failure

Inspect archived reports and validate JSON structure
and timestamps.

Do not delete historical evidence without a backup.

## Operational Commands

Check the service:

    systemctl --user show revenue-quality.service \
      -p Result -p ExecMainStatus

Review recent logs:

    journalctl --user -u revenue-quality.service \
      -n 100 --no-pager

Review the timer:

    systemctl --user list-timers \
      revenue-quality.timer --all

Run manually:

    systemctl --user start revenue-quality.service

Disable scheduling:

    systemctl --user disable --now revenue-quality.timer

## Manual Recovery Procedure

1. Identify the failed pipeline stage.
2. Inspect the corresponding systemd logs.
3. Review the structured execution events.
4. Diagnose and correct the underlying problem.
5. Re-run the relevant automated tests.
6. Restart the service after correcting the issue.
7. Verify that the stages finish successfully.

## Security

PostgreSQL credentials are stored outside Git.

systemd LoadCredential provides the private
credential during unattended execution.

Operational events and historical reports
are excluded from version control.

## Limitations

- No automatic email or external notifications.
- Retries are limited to the connection preflight.
- No automatic retry of dbt builds or data quality tests.
- Historical monitoring is stored locally.
- The user timer depends on user-manager availability.
- Full disaster recovery has not been tested.
- The first scheduled timer-triggered run is still
  pending independent verification.

The project uses the fictional AdventureWorks dataset.
