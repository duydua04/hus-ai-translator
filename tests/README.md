# 🧪 Tests — Bộ kiểm thử tự động

Bộ kiểm thử tự động cho hệ thống học thuật, bao gồm kiểm thử end-to-end (E2E), kiểm thử hiệu năng và các tiện ích hỗ trợ.

---

## 📋 Mục lục

- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Chạy kiểm thử](#chạy-kiểm-thử)
- [Mô tả các module](#mô-tả-các-module)
---

## Yêu cầu hệ thống

- Python >= 3.9
- pip hoặc virtualenv
- Trình duyệt Chrome
- ChromeDriver tương ứng với phiên bản trình duyệt

---

## Cài đặt

```bash
# Clone repository (nếu chưa có)
git clone <repo-url>
cd Tests

# Tạo và kích hoạt môi trường ảo
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

---



## Cấu trúc dự án

```
Tests/
├── .env                        # Biến môi trường (không commit)
├── conftest.py                 # Cấu hình và fixture chung cho toàn bộ bộ test
├── pytest.ini                  # Cấu hình pytest (markers, đường dẫn, v.v.)
├── requirements.txt            # Danh sách thư viện phụ thuộc
├── __init__.py
│
├── data/                       # Dữ liệu đầu vào cho các test case
│   ├── admin_login_data.py     # Dữ liệu đăng nhập admin
│   ├── dashboard_data.py       # Dữ liệu kiểm thử dashboard
│   ├── feedback_data.py        # Dữ liệu phản hồi / feedback
│   ├── register_data.py        # Dữ liệu đăng ký tài khoản
│   ├── reset_password_data.py  # Dữ liệu đặt lại mật khẩu
│   ├── translation_data.py     # Dữ liệu kiểm thử dịch thuật
│   ├── user_login_data.py      # Dữ liệu đăng nhập người dùng
│   └── fixtures/               # File đính kèm dùng trong test
│       ├── Easy-Test1-EV.pdf
│       ├── Easy-Test3-EV.pdf
│       ├── Test-Large-10Page-EVpdf.pdf
│       ├── Test-Large-20Page-EVpdf.pdf
│       ├── Test-Large-5Page-EV.pdf
│       ├── Test-Large-5Page-VE.pdf
│       ├── test_cards.json     # Dữ liệu thẻ học (flashcard)
│       └── users.json          # Danh sách người dùng mẫu
│
├── e2e/                        # Kiểm thử end-to-end
│   ├── admin/                  # Luồng nghiệp vụ của Admin
│   │   ├── test_admin_user.py  # Quản lý người dùng
│   │   ├── test_dashboard.py   # Dashboard thống kê
│   │   └── test_feedback.py    # Xem và xử lý phản hồi
│   ├── auth/                   # Xác thực và phân quyền
│   │   ├── test_admin_login.py # Đăng nhập admin
│   │   ├── test_register.py    # Đăng ký tài khoản mới
│   │   ├── test_reset_password.py  # Đặt lại mật khẩu
│   │   └── test_user_login.py  # Đăng nhập người dùng
│   └── user/                   # Luồng nghiệp vụ của Người dùng
│       ├── test_home_transilation.py  # Dịch thuật trang chủ
│       └── test_rating_modal.py       # Modal đánh giá
│
├── pages/                      # Page Object Model (POM)
│   ├── base_login_page.py      # Lớp cơ sở cho các trang đăng nhập
│   ├── home_page.py            # Trang chủ người dùng
│   ├── rating_modal_page.py    # Modal đánh giá
│   ├── admin/                  # Các trang trong giao diện Admin
│   │   ├── admin_login_page.py
│   │   ├── admin_user_page.py
│   │   ├── dashboard_page.py
│   │   └── feedback_page.py
│   └── user/                   # Các trang trong giao diện Người dùng
│       ├── register_page.py
│       ├── reset_password_page.py
│       └── user_login_page.py
│
├── performance/                # Kiểm thử hiệu năng (Locust)
│   ├── conftest.py             # Fixture riêng cho performance test
│   ├── test_performance.py     # Kịch bản tải (load scenario)
│   ├── data/
│   │   └── performance_data.py # Dữ liệu tải và ngưỡng chấp nhận
│   └── pages/
│       └── performance_page.py # Định nghĩa các endpoint được kiểm thử
│
└── utils/                      # Tiện ích dùng chung
    ├── api_client.py           # HTTP client gọi REST API
    └── faker_factory.py        # Sinh dữ liệu giả ngẫu nhiên (Faker)
```

---

## Chạy kiểm thử

### Chạy toàn bộ bộ test E2E

```bash
pytest e2e/ -v
```

### Chạy theo nhóm (marker)

```bash
# Chỉ chạy test xác thực
pytest e2e/auth/ -v

# Chỉ chạy test admin
pytest e2e/admin/ -v

# Chỉ chạy test người dùng
pytest e2e/user/ -v
```

### Chạy một file test cụ thể

```bash
pytest e2e/auth/test_user_login.py -v
```

### Chạy với báo cáo HTML

```bash
pytest e2e/ -v --html=report.html --self-contained-html
```

### Chạy song song (tăng tốc độ)

```bash
pytest e2e/ -v -n auto          # Dùng pytest-xdist
```

### Chạy kiểm thử hiệu năng
 
Bộ test hiệu năng dùng **pytest + Playwright** — đo thời gian thực tế trên trình duyệt
 
```bash
# Chạy toàn bộ (headless)
pytest performance/test_performance.py -v -s
 
# Chạy có giao diện trình duyệt để quan sát
pytest performance/test_performance.py -v -s --headed
 
# Chỉ chạy nhóm văn bản thuần
pytest performance/test_performance.py::TestTextTranslationTiming -v -s --headed
 
# Chỉ chạy nhóm PDF
pytest performance/test_performance.py::TestPDFTranslationTiming -v -s --headed
 
# Chạy báo cáo tổng hợp (văn bản + PDF cùng lúc)
pytest performance/test_performance.py::TestFullTimingReport -v -s --headed
```
 
---

## Mô tả các module

### `conftest.py` (gốc)
Khởi tạo WebDriver, quản lý vòng đời của browser session, và cung cấp các fixture dùng chung như `driver`, `base_url`, `authenticated_user`, `authenticated_admin`.

### `data/`
Chứa các hằng số và tập dữ liệu tham số hóa (parametrize) cho từng tính năng. Mỗi file tương ứng với một module nghiệp vụ, giúp tách biệt logic dữ liệu khỏi logic kiểm thử.

### `e2e/`
Các test case E2E được tổ chức theo vai trò người dùng (`auth`, `admin`, `user`). Mỗi test case sử dụng Page Object tương ứng và dữ liệu từ `data/`.

### `pages/`
Triển khai mô hình **Page Object Model (POM)**. Mỗi class đóng gói các selector và hành động tương tác với một trang cụ thể, giúp test case dễ đọc và dễ bảo trì.

### `performance/`
Kịch bản kiểm thử tải dùng **Locust**. Định nghĩa các luồng người dùng ảo (virtual user) mô phỏng hành vi thực tế để đo throughput, thời gian phản hồi và tỷ lệ lỗi.

### `utils/`
| File | Mô tả |
|---|---|
| `api_client.py` | Wrapper cho `requests`, hỗ trợ xác thực, retry, và logging |
| `faker_factory.py` | Sinh dữ liệu ngẫu nhiên (tên, email, mật khẩu, v.v.) dùng thư viện `Faker` |

---
