#!/bin/bash
set -e

echo "Starting database migrations..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
until python -c "
from config import settings
import psycopg2
try:
    conn = psycopg2.connect(settings.database_url)
    conn.close()
    print('Database is ready!')
except:
    sys.exit(1)
" 2>/dev/null; do
    echo "Database not ready, waiting..."
    sleep 2
done

echo "Running Alembic migrations..."
alembic upgrade head

echo "Migrations completed successfully!"