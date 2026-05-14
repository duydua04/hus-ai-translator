# Đường dẫn: layout-model/worker.py
import os
import json
import time
import requests
import redis
import traceback
from minio import Minio
from dotenv import load_dotenv

# Import Pipeline ổn định của bạn
from pipeline import DocumentTranslationPipeline

# ==========================================
# 1. CẤU HÌNH HẠ TẦNG TỪ .env
# ==========================================
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
QUEUE_NAME = os.getenv("TRANSLATION_FILE_QUEUE", "translation_tasks_queue")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9004")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "admin123")
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"
BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "transminer-uploads")

BACKEND_WEBHOOK_URL = os.getenv("BACKEND_WEBHOOK_URL", "http://localhost:8000/api/webhook/translation-done")

# Khởi tạo Client hạ tầng
redis_client = redis.from_url(REDIS_URL, decode_responses=True)
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)


def process_file_task(task_data: dict):
    """ Xử lý 1 yêu cầu dịch PDF """
    client_id = task_data.get("client_id")
    translation_id = task_data.get("translation_id")
    file_path = task_data.get("file_path")

    channel = f"sse_{client_id}"

    os.makedirs("./tmp", exist_ok=True)
    local_input = f"./tmp/{translation_id}_in.pdf"
    local_output = f"./tmp/{translation_id}_out.pdf"

    # Hàm gọi SSE trực tiếp lên Redis
    def sse_callback(data: dict):
        redis_client.publish(channel, json.dumps(data, ensure_ascii=False))

    try:
        print(f"\n[>>>] Bắt đầu dịch (Google) cho Client: {client_id}")
        sse_callback({"status": "processing", "progress": 5, "message": "Đang lấy tài liệu từ MinIO..."})

        # 1. TẢI FILE TỪ MINIO
        object_name = file_path.replace(f"{BUCKET_NAME}/", "", 1) if file_path.startswith(
            f"{BUCKET_NAME}/") else file_path
        minio_client.fget_object(BUCKET_NAME, object_name, local_input)

        # 2. KHỞI TẠO PIPELINE CỦA BẠN (Dùng Google Translate)
        print("[-] Khởi chạy DocumentTranslationPipeline (service='google')...")
        pipeline = DocumentTranslationPipeline(
            service="google",  # Ép cứng dùng Google Translator theo yêu cầu
            lang_in="en",
            lang_out="vi",
            use_cache=True  # Giữ nguyên hệ thống cache thông minh của bạn
        )

        # 3. CHẠY DỊCH & BẮN SSE
        result = pipeline.translate(
            input_pdf=local_input,
            output_pdf=local_output,
            progress_callback=sse_callback
        )

        if result.get("status") == "success":
            sse_callback({"status": "processing", "progress": 95, "message": "Đang lưu file kết quả lên MinIO..."})

            # 4. UPLOAD LÊN MINIO
            output_obj_name = object_name.replace(".pdf", "_translated.pdf")
            minio_client.fput_object(BUCKET_NAME, output_obj_name, local_output)
            result_path = f"{BUCKET_NAME}/{output_obj_name}"

            print(f"[-] Dịch xong! File: {result_path}")
            sse_callback({"status": "finalizing", "progress": 98, "message": "Đang lưu kết quả vào hệ thống..."})

            requests.post(BACKEND_WEBHOOK_URL, json={
                "translation_id": translation_id,
                "client_id": client_id,
                "status": "success",
                "result_path": result_path
            }, timeout=10)
        else:
            # Nếu pipeline.translate() trả về lỗi
            raise Exception(result.get("error", "Lỗi Pipeline không xác định"))

    except Exception as e:
        print(f"\n[!!!] Lỗi khi xử lý task {translation_id}: {e}")
        traceback.print_exc()

        sse_callback({"status": "error", "progress": 0, "message": f"Lỗi xử lý tài liệu: {str(e)}"})
        try:
            requests.post(BACKEND_WEBHOOK_URL, json={
                "translation_id": translation_id,
                "client_id": client_id,
                "status": "failed",
                "error_message": str(e)
            }, timeout=5)
        except:
            pass

    finally:
        # 6. DỌN RÁC
        if os.path.exists(local_input): os.remove(local_input)
        if os.path.exists(local_output): os.remove(local_output)
        print(f"[<<<] Hoàn tất luồng xử lý: {translation_id}")


def start_worker():
    print("==================================================")
    print("WORKER (GOOGLE TRANSLATE) SẴN SÀNG")
    print(f"Lắng nghe Redis Queue: {QUEUE_NAME}")
    print("==================================================")

    while True:
        try:
            # Đứng đợi file từ Backend gởi qua
            _, msg_data = redis_client.brpop(QUEUE_NAME)
            process_file_task(json.loads(msg_data))
        except json.JSONDecodeError:
            print("[X] Dữ liệu trong Queue không đúng chuẩn JSON.")
        except redis.ConnectionError:
            print("[X] Mất kết nối Redis. Thử lại sau 5 giây...")
            time.sleep(5)
        except Exception as e:
            print(f"[X] Lỗi Worker Loop: {e}")
            time.sleep(2)


if __name__ == "__main__":
    start_worker()