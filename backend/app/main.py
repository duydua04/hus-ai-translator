from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from passlib.context import CryptContext
import uuid

# --- 1. CẤU HÌNH DATABASE (Dùng tạm SQLite để test nhanh, nó sẽ tự tạo file test_login.db) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_login.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. CẤU HÌNH BĂM MẬT KHẨU ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 3. ĐỊNH NGHĨA BẢNG USER ---
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Tự động tạo bảng trong CSDL
Base.metadata.create_all(bind=engine)

# --- 4. KHỞI TẠO FASTAPI ---
app = FastAPI(title="Test Login API")

# Dependency để kết nối DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 5. API ĐĂNG KÝ (Tạo tài khoản test) ---
@app.post("/register", tags=["Authentication"])
def register(email: str, password: str, db: Session = Depends(get_db)):
    # Kiểm tra xem email đã tồn tại chưa
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email này đã được đăng ký!")
    
    # Băm mật khẩu và lưu vào DB
    hashed_pw = pwd_context.hash(password)
    new_user = User(email=email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    return {"message": "Tạo tài khoản thành công!", "email": email}

# --- 6. API ĐĂNG NHẬP (Cái bạn cần test) ---
@app.post("/login", tags=["Authentication"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Tìm user trong DB theo email (form_data.username chính là email người dùng nhập)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Kiểm tra tài khoản và so sánh mật khẩu người dùng nhập với mật khẩu đã băm trong DB
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai email hoặc mật khẩu!",
        )
    
    # Đăng nhập thành công, trả về Token (Ở đây làm token giả lập cho dễ hiểu)
    return {
        "access_token": f"thanh-cong-token-cua-{user.email}", 
        "token_type": "bearer"
    }