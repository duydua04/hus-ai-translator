# ============================================
# Dockerfile: translate_model (FastAPI AI Service)
# Python 3.10 — CTranslate2 EN↔VI model server
# ============================================
FROM python:3.10-slim

WORKDIR /app

# Copy và cài dependencies trước (tận dụng Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Tải sẵn dữ liệu NLTK trong lúc build image
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# Copy source code + models
COPY . .

# Expose port
EXPOSE 8001

# Chạy FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
