"""
Sprint 09 - Database Recovery Tests.

All connection outcomes are simulated.
No real database connection is attempted.
"""

import importlib.util
from pathlib import Path
from unittest.mock import Mock

import psycopg


ROOT = Path(__file__).resolve().parents[1]

SCRIPT = ROOT / "scripts" / "check_database_connection.py"

spec = importlib.util.spec_from_file_location(
    "database_connection_preflight",
    SCRIPT,
)

preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


def test_success_on_first_attempt():
    connect = Mock()
    sleep = Mock()

    assert preflight.check_connection(
        connect_fn=connect,
        sleep_fn=sleep,
    )

    assert connect.call_count == 1
    sleep.assert_not_called()


def test_temporary_failure_then_recovery():
    connect = Mock(
        side_effect=[
            psycopg.OperationalError(
                "Connection temporarily unavailable"
            ),
            None,
        ]
    )

    sleep = Mock()

    assert preflight.check_connection(
        connect_fn=connect,
        sleep_fn=sleep,
    )

    assert connect.call_count == 2
    sleep.assert_called_once_with(2)


def test_retries_are_limited():
    connect = Mock(
        side_effect=psycopg.OperationalError(
            "Connection refused"
        )
    )

    sleep = Mock()

    assert not preflight.check_connection(
        connect_fn=connect,
        sleep_fn=sleep,
    )

    assert connect.call_count == 3
    assert sleep.call_count == 2


def test_missing_password_does_not_retry():
    connect = Mock(
        side_effect=ValueError(
            "No password configured"
        )
    )

    sleep = Mock()

    assert not preflight.check_connection(
        connect_fn=connect,
        sleep_fn=sleep,
    )

    assert connect.call_count == 1
    sleep.assert_not_called()


def test_non_retryable_database_error():
    connect = Mock(
        side_effect=psycopg.ProgrammingError(
            "Invalid database configuration"
        )
    )

    sleep = Mock()

    assert not preflight.check_connection(
        connect_fn=connect,
        sleep_fn=sleep,
    )

    assert connect.call_count == 1
    sleep.assert_not_called()
