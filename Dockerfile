# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Install system libs for psycopg2
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:api", "--host", "0.0.0.0", "--port", "8000"]
