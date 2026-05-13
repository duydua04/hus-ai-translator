import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./LoginPage.scss";

/**
 * Props:
 *  login   (payload) => { success, message? }
 *  loading boolean
 *  error   string | null
 */
export default function LoginPage({ login, loading, error }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async () => {
    if (!form.email || !form.password) return;
    const result = await login(form);
    if (result.success) navigate("/");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSubmit();
  };

  return (
    <div className="auth-page">
      <div className="auth-page__card">
        {/* Logo / Brand */}
        <div className="auth-page__brand">
          <i className="bx bx-store auth-page__brand-icon"></i>
          <span className="auth-page__brand-name">Site name</span>
        </div>

        <h1 className="auth-page__title">Đăng nhập</h1>
        <p className="auth-page__subtitle">
          Chào mừng trở lại! Vui lòng nhập thông tin của bạn.
        </p>

        {/* Error */}
        {error && (
          <div className="auth-page__alert auth-page__alert--error">
            <i className="bx bx-error-circle"></i>
            {error}
          </div>
        )}

        {/* Form */}
        <div className="auth-form">
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
                onKeyDown={handleKeyDown}
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
                placeholder="••••••••"
                className="auth-form__input"
                value={form.password}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                autoComplete="current-password"
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

          {/* Quên mật khẩu */}
          <div className="auth-form__row auth-form__row--right">
            <Link to="/forgot-password" className="auth-form__link">
              Quên mật khẩu?
            </Link>
          </div>

          <button
            className="auth-form__submit btn btn--primary"
            onClick={handleSubmit}
            disabled={loading || !form.email || !form.password}
          >
            {loading ? (
              <>
                <i className="bx bx-loader-alt bx-spin"></i> Đang đăng nhập...
              </>
            ) : (
              "Đăng nhập"
            )}
          </button>
        </div>

        <p className="auth-page__footer-text">
          Chưa có tài khoản?{" "}
          <Link to="/register" className="auth-form__link">
            Đăng ký ngay
          </Link>
        </p>
      </div>
    </div>
  );
}
