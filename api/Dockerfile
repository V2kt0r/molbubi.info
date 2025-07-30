FROM python:3.12-slim AS builder

RUN python -m pip install --upgrade pip

RUN pip install poetry
RUN poetry self add poetry-plugin-export

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.12-slim AS runtime

RUN apt-get update && \
    apt-get install -y gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

WORKDIR /code

COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
