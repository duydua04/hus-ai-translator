# Sử dụng image Airflow gốc của bạn
FROM apache/airflow:2.8.1

# 1. Xin quyền Root để cài đặt phần mềm hệ thống
USER root

# 2. Cài đặt trình duyệt Chromium (Bản mã nguồn mở của Chrome)
RUN apt-get update \
    && apt-get install -y chromium \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Trả lại quyền cho user airflow để đảm bảo bảo mật
USER airflow

# 4. Cài luôn các thư viện Python vào đây (giúp Airflow khởi động nhanh hơn rất nhiều)
RUN pip install --no-cache-dir DrissionPage pandas s3fs python-dotenv