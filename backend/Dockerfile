FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2 and postgresql clients
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./backend/requirements.txt

COPY backend/ ./backend/
COPY database/ ./database/
COPY docs/ ./docs/
COPY generated_data/ ./generated_data/
COPY alembic.ini ./

ENV PYTHONPATH=/app
ENV PORT=8001

EXPOSE 8001

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
