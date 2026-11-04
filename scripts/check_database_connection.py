"""
Sprint 09 - PostgreSQL Connection Preflight.

Checks database connectivity with bounded retries.
Does not modify database records.
"""

import os
import sys
import time

import psycopg


MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2

# Connection failures and PostgreSQL startup state.
TRANSIENT_CODES = {"57P03"}


def is_transient(error):
    code = getattr(error, "sqlstate", None)

    if code is None:
        return isinstance(error, psycopg.OperationalError)

    return (
        code.startswith("08")
        or code in TRANSIENT_CODES
    )


def connect_once():
    password = (
        os.environ.get("PGPASSWORD")
        or os.environ.get("DBT_PG_PASSWORD")
    )

    if not password:
        raise ValueError(
            "No PostgreSQL password available."
        )

    with psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="revenue_intelligence",
        user="revenue_app",
        password=password,
        connect_timeout=3,
        options="-c default_transaction_read_only=on",
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

            if result is None or result[0] != 1:
                raise RuntimeError(
                    "Unexpected database response."
                )


def check_connection(
    connect_fn=connect_once,
    sleep_fn=time.sleep,
    attempts=MAX_ATTEMPTS,
):
    if attempts < 1:
        raise ValueError(
            "At least one attempt is required."
        )

    for attempt in range(1, attempts + 1):
        print(
            f"Database connection check: "
            f"attempt {attempt}/{attempts}",
            flush=True,
        )

        try:
            connect_fn()
            print("Database connection: OK")
            return True

        except psycopg.Error as exc:
            if not is_transient(exc):
                print(
                    "Database error is not retryable.",
                    file=sys.stderr,
                )
                return False

            if attempt == attempts:
                print(
                    "Database unavailable after "
                    "maximum attempts.",
                    file=sys.stderr,
                )
                return False

            print("Temporary connection error. Retrying.")
            sleep_fn(RETRY_DELAY_SECONDS)

        except (ValueError, RuntimeError) as exc:
            print(
                f"Connection preflight failed: "
                f"{type(exc).__name__}",
                file=sys.stderr,
            )
            return False

    return False


def main():
    return 0 if check_connection() else 1


if __name__ == "__main__":
    sys.exit(main())
