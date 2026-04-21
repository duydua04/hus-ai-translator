# Sử dụng image Python chuẩn
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Khắc phục lỗi không sinh file .pyc và log console
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Cài đặt các thư viện cần thiết
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . /app/

# Mở cổng 8000
EXPOSE 8000

# Khởi chạy ứng dụng
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]