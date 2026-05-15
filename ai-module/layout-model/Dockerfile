# ============================================
# Dockerfile: layout-model (AI Worker)
# Python 3.10 — Dịch file PDF qua Google Translate
# ============================================
FROM python:3.10-slim

WORKDIR /app

# Cài thư viện hệ thống cho OpenCV headless + PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copy và cài dependencies trước (tận dụng Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Copy source code
COPY . .

# Tạo thư mục tmp cho file tạm
RUN mkdir -p /app/tmp /app/cache

# Chạy worker
CMD ["python", "worker.py"]
