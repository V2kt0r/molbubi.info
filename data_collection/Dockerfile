FROM python:3.11.3-slim

WORKDIR /app

COPY data_collection/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY data_collection/ data_collection/
COPY shared/ shared/

CMD ["python", "-m", "data_collection.main"]
