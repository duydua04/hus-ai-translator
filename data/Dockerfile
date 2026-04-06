# 1. Dùng bản slim để nhẹ nhưng vẫn đủ dùng
FROM python:3.12-slim

# 2. Cài đặt các thư viện hệ thống cần thiết để chạy Chrome
RUN apt-get update && apt-get install -y \
    locales \
    chromium \
    chromium-driver \
    libnss3 \
    libatk-bridge2.0-0 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    --no-install-recommends && \
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

# 3. Thiết lập thư mục làm việc
WORKDIR /app

# 4. Cài đặt thư viện Python trước để tối ưu cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Sao chép toàn bộ mã nguồn
COPY . .

# 6. QUAN TRỌNG: Thiết lập PYTHONPATH để import được utils, configs
ENV PYTHONPATH=/app/src
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# 7. Chạy ứng dụng
# Chú ý: Hoa nên dùng chế độ headless (không giao diện) khi chạy trong Docker
CMD ["python","-m", "raw.crawldata"]