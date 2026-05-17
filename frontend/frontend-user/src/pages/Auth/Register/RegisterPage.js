import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./RegisterPage.scss";

/**
 * Props:
 *  register (payload) => { success, message? }
 *  loading  boolean
 *  error    string | null
 */
export default function RegisterPage({ register, loading, error }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setLocalError(null);
  };

  const validate = () => {
    if (!form.full_name.trim()) return "Vui lòng nhập họ tên.";

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!form.email.trim()) return "Vui lòng nhập email.";
    if (!emailRegex.test(form.email)) return "Email không đúng định dạng.";

    if (form.password.length < 8) return "Mật khẩu tối thiểu 8 ký tự.";
    if (!/[A-Z]/.test(form.password))
      return "Mật khẩu phải có ít nhất 1 chữ hoa.";
    if (!/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(form.password))
      return "Mật khẩu phải có ít nhất 1 ký tự đặc biệt.";
    if (!/[0-9]/.test(form.password))
      return "Mật khẩu phải có ít nhất 1 chữ số.";
    if (form.password === form.email)
      return "Mật khẩu không được trùng với email.";

    if (form.password !== form.confirm_password)
      return "Mật khẩu xác nhận không khớp.";

    return null;
  };

  const handleSubmit = async () => {
    const validationError = validate();
    if (validationError) {
      setLocalError(validationError);
      return;
    }

    const { confirm_password, ...payload } = form;
    const result = await register(payload);

    if (result.success) {
      setSuccess(true);
      setTimeout(() => navigate("/login"), 2000);
    }
  };

  return (
    <div className="auth-page auth-page--register">
      <div className="auth-page__card">
        <div className="auth-page__brand">
          <i className="bx bx-store auth-page__brand-icon"></i>
          <span className="auth-page__brand-name">TRANSDE</span>
        </div>

        <h1 className="auth-page__title">Tạo tài khoản</h1>
        <p className="auth-page__subtitle">
          Điền thông tin để bắt đầu sử dụng dịch vụ.
        </p>

        {/* Success */}
        {success && (
          <div className="auth-page__alert auth-page__alert--success">
            <i className="bx bx-check-circle"></i>
            Đăng ký thành công! Đang chuyển đến trang đăng nhập...
          </div>
        )}

        {/* Error */}
        {(localError || error) && !success && (
          <div className="auth-page__alert auth-page__alert--error">
            <i className="bx bx-error-circle"></i>
            {localError || error}
          </div>
        )}

        <div className="auth-form">
          <div className="auth-form__field">
            <label className="auth-form__label">Họ và tên</label>
            <div className="auth-form__input-wrapper">
              <i className="bx bx-user auth-form__input-icon"></i>
              <input
                type="text"
                name="full_name"
                placeholder="Nguyễn Văn A"
                className="auth-form__input"
                value={form.full_name}
                onChange={handleChange}
                autoComplete="name"
              />
            </div>
          </div>

          <div className="auth-form__field">
            <label className="auth-form__label">Email</label>
            <div className="auth-form__input-wrapper">
              <i className="bx bx-envelope auth-form__input-icon"></i>
              <input
                type="email"
                name="email"
                placeholder="email@example.com"
                className="auth-form__input"
                value={form.email}
                onChange={handleChange}
                autoComplete="email"
              />
            </div>
          </div>

          <div className="auth-form__field">
            <label className="auth-form__label">Mật khẩu</label>
            <div className="auth-form__input-wrapper">
              <i className="bx bx-lock-alt auth-form__input-icon"></i>
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                placeholder="Ít nhất 8 ký tự, 1 chữ hoa, 1 ký tự đặc biệt"
                className="auth-form__input"
                value={form.password}
                onChange={handleChange}
                autoComplete="new-password"
              />
              <button
                type="button"
                className="auth-form__toggle-pw"
                onClick={() => setShowPassword((v) => !v)}
                tabIndex={-1}
              >
                <i className={`bx ${showPassword ? "bx-hide" : "bx-show"}`}></i>
              </button>
            </div>
          </div>

          <div className="auth-form__field">
            <label className="auth-form__label">Xác nhận mật khẩu</label>
            <div className="auth-form__input-wrapper">
              <i className="bx bx-lock auth-form__input-icon"></i>
              <input
                type={showPassword ? "text" : "password"}
                name="confirm_password"
                placeholder="Nhập lại mật khẩu"
                className="auth-form__input"
                value={form.confirm_password}
                onChange={handleChange}
                autoComplete="new-password"
              />
            </div>
          </div>

          <button
            className="auth-form__submit btn btn--primary"
            onClick={handleSubmit}
            disabled={loading || success}
          >
            {loading ? (
              <>
                <i className="bx bx-loader-alt bx-spin"></i> Đang xử lý...
              </>
            ) : (
              "Đăng ký"
            )}
          </button>
        </div>

        <p className="auth-page__footer-text">
          Đã có tài khoản?{" "}
          <Link to="/login" className="auth-form__link">
            Đăng nhập
          </Link>
        </p>
      </div>
    </div>
  );
}
