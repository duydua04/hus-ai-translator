# 🧪 Bộ Test — HUS AI Translator

Tài liệu kiểm thử tự động và thủ công cho **HUS AI Translator** — ứng dụng web dịch tài liệu học thuật, backend xây dựng bằng FastAPI.

---

## 📁 Cấu trúc thư mục

```
Tests/
├── e2e/                  # Test E2E tự động
│   ├── admin/            # Module Admin (dashboard, quản lý user, feedback)
│   ├── auth/             # Module Auth (đăng nhập, đăng ký, reset mật khẩu)
│   └── user/             # Module User (dịch tài liệu, rating modal)
├── pages/                # Các class theo mô hình Page Object Model (POM)
│   ├── admin/
│   └── user/
├── data/                 # Dữ liệu test
│   └── fixtures/         # File PDF mẫu, JSON fixtures
├── performance/          # Module kiểm thử hiệu năng
├── utils/                # Tiện ích dùng chung (API client, Faker factory)
├── conftest.py           # Fixtures dùng chung cho Pytest
├── pytest.ini            # Cấu hình Pytest
├── requirements.txt      # Thư viện cần cài
└── .env.example          # Mẫu biến môi trường
```

---

## 🛠️ Công nghệ sử dụng

| Công cụ | Mục đích |
|---------|---------|
| Pytest + Playwright | Tự động hóa kiểm thử E2E |
| Page Object Model | Mô hình tổ chức code test |
| Postman | Kiểm thử API thủ công |
| Google Sheets | Quản lý test case & theo dõi bug |
| Faker | Sinh dữ liệu test động |

---

## 🚀 Hướng dẫn chạy test

### 1. Clone & cài đặt

```bash
git clone https://github.com/duydua04/hus-ai-translator.git
cd Tests
pip install -r requirements.txt
playwright install chromium
```

### 2. Cấu hình môi trường

```bash
cp .env.example .env
# Điền BASE_URL và thông tin tài khoản test vào .env
```

### 3. Chạy test

```bash
# Chạy toàn bộ E2E
pytest e2e/ -v

# Chạy theo module
pytest e2e/auth/ -v
pytest e2e/admin/ -v
pytest e2e/user/ -v

# Chạy performance test
pytest performance/ -v

# Xuất báo cáo HTML
pytest e2e/ --html=reports/report.html --self-contained-html
```

---

## 📋 Phạm vi kiểm thử

| Module | Loại test | Mô tả |
|--------|-----------|-------|
| Auth | E2E, Boundary | Đăng nhập, Đăng ký, Reset mật khẩu |
| Admin | E2E, Functional | Dashboard, Quản lý user, Feedback |
| User | E2E, Functional | Luồng dịch tài liệu, Rating Modal |
| API | Thủ công (Postman) | 25+ REST endpoints |
| Performance | Tự động | Thời gian tải trang, thời gian phản hồi dịch |

---

## 📊 Tài liệu kiểm thử

| Tài liệu | Link |
|----------|------|
| 📄 Test Plan | [Google Sheets — Test Plan](https://docs.google.com/document/d/1YE7lUOPsaXc9oHhLAynKqsnkbYZU9JP5/edit) |
| 🗂️ Test Cases (300+) | [Google Sheets — Test Cases](https://docs.google.com/spreadsheets/d/10GPgtvYsajffjaWpGKRn23oY_hp1Go5goSuRwl4p3bo/edit?gid=662710053#gid=662710053) |
| 🐛 Bug Report | [Google Sheets — Bug Tracking](https://docs.google.com/spreadsheets/d/1b70eouFZ2PEjVS01Dl5c7DsUqMjYyZKs/edit?gid=344164659#gid=344164659) |

> **300+ test case** tổng cộng (thủ công + tự động) bao gồm UI/UX, logic nghiệp vụ, API, boundary và negative scenarios.

---

## 📈 Kết quả kiểm thử

| Chỉ số | Kết quả |
|--------|---------|
| Tổng test case tự động | ~100 |
| Tỉ lệ pass | 94% |
| Test case thủ công | 200+ |
| API endpoints đã kiểm thử | 25+ |

---

## 🧩 Kiến trúc — Page Object Model

```
File Test (e2e/)
      │
      ▼
Page Class (pages/)       ← chứa locators + hành động trên UI
      │
      ▼
conftest.py               ← fixtures dùng chung (browser, session đăng nhập...)
      │
      ▼
data/                     ← dữ liệu test (JSON, Python data files)
```

Mỗi page class đại diện cho một màn hình, tách biệt hoàn toàn với logic test — giúp dễ bảo trì khi UI thay đổi.

---

## 📝 Ghi chú

- File `.env` không được commit lên Git — dùng `.env.example` làm mẫu
- File PDF fixture nằm trong `data/fixtures/` để test upload (5, 10, 20 trang)
- Toàn bộ code test nằm ở nhánh: `test-branch`