FROM python:3.11.3-slim

WORKDIR /app

COPY db_migrator/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY db_migrator/ db_migrator/
COPY shared/ shared/

CMD ["python", "-m", "db_migrator.main"]
