FROM python:3.10-slim

WORKDIR /app

# Only install what is strictly needed for psycopg2-binary and basic compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.backend.txt .

RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.backend.txt

COPY ./backend /app/backend

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
