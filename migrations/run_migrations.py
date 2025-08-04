#!/usr/bin/env python3
"""
Database migrations runner using Alembic.
Replaces the shell script with a proper Python implementation.
"""
import time
import sys
import subprocess
import psycopg2
from config import settings


def wait_for_database(max_retries: int = 30, retry_interval: int = 2) -> None:
    """Wait for the database to be ready for connections."""
    print("Waiting for database to be ready...")
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(settings.database_url)
            conn.close()
            print("Database is ready!")
            return
        except psycopg2.OperationalError:
            print(f"Database not ready, waiting... (attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_interval)
    
    print("ERROR: Database did not become ready within the timeout period")
    sys.exit(1)


def run_migrations() -> None:
    """Run Alembic migrations to upgrade to the latest version."""
    print("Running Alembic migrations...")
    
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True
        )
        print("Migrations completed successfully!")
        if result.stdout:
            print("Migration output:")
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Migration failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        sys.exit(1)


def main() -> None:
    """Main migration runner function."""
    print("Starting database migrations...")
    
    # Wait for database to be ready
    wait_for_database()
    
    # Run migrations
    run_migrations()
    
    print("Migration process completed successfully!")


if __name__ == "__main__":
    main()