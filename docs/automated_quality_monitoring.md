# Automated Financial Quality Monitoring

## Sprint 08 - Automation and Monitoring History

## Objective

Extend the financial quality pipeline with persistent
execution history, historical comparison, and scheduled
execution on Fedora Linux.

## Architecture

systemd Timer
    |
    v
systemd Service
    |
    v
Python Unit Tests
    |
    v
dbt Build and Data Tests
    |
    v
Financial Quality Monitor
    |
    v
Report Archiving
    |
    v
Historical Comparison

## Components

- scripts/run_quality_pipeline.sh
- scripts/archive_quality_report.py
- scripts/compare_quality_history.py
- deploy/systemd/revenue-quality.service
- deploy/systemd/revenue-quality.timer

## Validated Results

- Python tests: 4 passed
- dbt operations: 59 passed
- Monitoring: 4 PASS, 3 WARN, 0 FAIL
- Historical executions: 3 verified
- systemd service: executed successfully
- systemd timer: enabled and waiting

The historical comparison detected no changes
between the two latest executions.

## Schedule

The user-level systemd timer is configured to run
daily at 09:00 local system time.

Persistent=true allows a missed scheduled run to
be triggered when the timer becomes active again.

With Linger=no, the user manager generally requires
an active user session.

The pipeline cannot execute while the computer
is powered off.

## Security

PostgreSQL credentials are stored outside Git.

The local credential file is:

~/.config/revenue-intelligence-dbt/postgres_password

The directory has permission 700 and the credential
file has permission 600.

The credential is stored in plaintext on disk and
should be protected by appropriate system security.

systemd LoadCredential supplies the credential to
the service without embedding its value in the unit.

The private dbt profile is also kept outside Git.

## Installation

The service and timer templates are included under:

deploy/systemd/

They can be installed into:

~/.config/systemd/user/

Before installing, verify the project path and private
credential location match the target environment.

Then reload the user systemd manager and enable the
timer:

    systemctl --user daemon-reload
    systemctl --user enable --now revenue-quality.timer

## Operations

Inspect the timer:

    systemctl --user list-timers revenue-quality.timer

Run the service manually:

    systemctl --user start revenue-quality.service

Inspect service logs:

    journalctl --user -u revenue-quality.service -n 50

Disable the timer:

    systemctl --user disable --now revenue-quality.timer

## Historical Reports

Archived reports are stored locally under:

reports/monitoring/history/

Each archive contains:

- quality_report.json
- quality_report.md
- metadata.json

The generated history is excluded from Git.

The latest JSON and Markdown monitoring reports
remain available as project evidence.

## Limitations

The timer is configured but its first scheduled
execution has not yet been observed.

Notifications and external alert delivery are
not implemented.

The monitoring comparison evaluates report changes;
it does not establish the causes of business anomalies.
