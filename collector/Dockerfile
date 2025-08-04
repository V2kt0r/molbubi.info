FROM python:3.11-slim

# Install poetry
RUN pip install poetry

# Configure poetry: don't create a virtual environment
RUN poetry config virtualenvs.create false

WORKDIR /code

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --only=main --no-root

COPY ./app ./app

CMD ["python", "-m", "app.main"]
