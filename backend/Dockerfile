# ============================================
# Dockerfile: Backend (FastAPI)
# Python 3.11
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Cài thư viện hệ thống cho psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy và cài dependencies trước (tận dụng Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Khởi chạy ứng dụng
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]