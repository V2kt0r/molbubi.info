FROM python:3.12-slim

# Install system dependencies needed for psycopg2
RUN apt-get update && \
    apt-get install -y gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Configure poetry: don't create a virtual environment
RUN poetry config virtualenvs.create false

WORKDIR /app

# Copy poetry files
COPY migrations/pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --only=main --no-root

# Copy migrations service files
COPY migrations/alembic ./alembic
COPY migrations/alembic.ini ./alembic.ini
COPY migrations/models.py ./models.py
COPY migrations/config.py ./config.py
COPY migrations/run_migrations.py ./run_migrations.py

RUN chmod +x run_migrations.py

CMD ["python", "run_migrations.py"]