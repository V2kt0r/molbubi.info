FROM python:3.12-slim AS builder

RUN python -m pip install --upgrade pip

RUN pip install poetry
RUN poetry self add poetry-plugin-export

WORKDIR /app

# Copy migrations poetry files
COPY migrations/pyproject.toml ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.12-slim AS runtime

RUN apt-get update && \
    apt-get install -y gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

WORKDIR /app

COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy migrations service files
COPY migrations/alembic ./alembic
COPY migrations/alembic.ini ./alembic.ini
COPY migrations/models.py ./models.py
COPY migrations/config.py ./config.py
COPY migrations/run_migrations.sh ./run_migrations.sh

RUN chmod +x run_migrations.sh

CMD ["./run_migrations.sh"]