import React, { useState } from "react";
import "./Login.scss";

function Login({ login, loading, error }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await login(email, password);
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-badge">
          <i className="ti ti-shield-check" aria-hidden="true" />
          Admin Portal
        </div>

        <h1 className="login-title">Chào mừng quay trở lại!</h1>
        <p className="login-subtitle">Đăng nhập vào quản trị hệ thống</p>

        <form onSubmit={handleSubmit}>
          <div className="login-field">
            <label htmlFor="email">Email</label>
            <div className="login-input-wrap">
              <i className="ti ti-mail" aria-hidden="true" />
              <input
                className="login-input"
                id="email"
                type="email"
                placeholder="admin@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="login-field">
            <label htmlFor="password">Mật khẩu</label>
            <div className="login-input-wrap">
              <i className="ti ti-lock" aria-hidden="true" />
              <input
                className="login-input login-input--pw"
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="login-eye-btn"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
              >
                <i
                  className={`ti ${showPassword ? "ti-eye-off" : "ti-eye"}`}
                  aria-hidden="true"
                />
              </button>
            </div>
          </div>

          {error && (
            <div className="login-error">
              <i className="ti ti-alert-circle" aria-hidden="true" />
              {error}
            </div>
          )}

          <button type="submit" className="login-btn" disabled={loading}>
            <i className="ti ti-login-2" aria-hidden="true" />
            {loading ? "Đang đăng nhập..." : "Đăng nhập"}
          </button>
        </form>

        <div className="login-footer">
          <i className="ti ti-lock-check" aria-hidden="true" />
          Chỉ dành cho quản trị viên
        </div>
      </div>
    </div>
  );
}

export default Login;
