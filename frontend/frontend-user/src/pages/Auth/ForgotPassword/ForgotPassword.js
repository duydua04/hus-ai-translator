import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { forgotPassword, verifyOtp, resetPassword } from "../../../api/authApi";
import "./ForgotPassword.scss";

// 3 bước: "email" → "otp" → "reset" → "done"
const STEPS = { EMAIL: "email", OTP: "otp", RESET: "reset", DONE: "done" };

export default function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(STEPS.EMAIL);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Bước 1
  const [email, setEmail] = useState("");
  // Bước 2
  const [otp, setOtp] = useState("");
  // Bước 3
  const [passwords, setPasswords] = useState({
    new_password: "",
    confirm_password: "",
  });
  const [showPassword, setShowPassword] = useState(false);

  const clearError = () => setError(null);

  // ── Bước 1: Gửi email ──
  const handleSendEmail = async () => {
    if (!email.trim()) {
      setError("Vui lòng nhập email.");
      return;
    }
    setLoading(true);
    clearError();
    try {
      await forgotPassword(email);
      setStep(STEPS.OTP);
    } catch (err) {
      setError(err.response?.data?.detail || "Gửi OTP thất bại.");
    } finally {
      setLoading(false);
    }
  };

  // ── Bước 2: Xác thực OTP ──
  const handleVerifyOtp = async () => {
    if (otp.trim().length < 4) {
      setError("Vui lòng nhập mã OTP hợp lệ.");
      return;
    }
    setLoading(true);
    clearError();
    try {
      await verifyOtp(otp);
      setStep(STEPS.RESET);
    } catch (err) {
      setError(err.response?.data?.detail || "Mã OTP không hợp lệ.");
    } finally {
      setLoading(false);
    }
  };

  // ── Bước 3: Đặt mật khẩu mới ──
  const handleResetPassword = async () => {
    if (passwords.new_password.length < 6) {
      setError("Mật khẩu tối thiểu 6 ký tự.");
      return;
    }
    if (passwords.new_password !== passwords.confirm_password) {
      setError("Mật khẩu xác nhận không khớp.");
      return;
    }
    setLoading(true);
    clearError();
    try {
      await resetPassword(passwords);
      setStep(STEPS.DONE);
    } catch (err) {
      setError(err.response?.data?.detail || "Đặt mật khẩu thất bại.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page auth-page--forgot">
      <div className="auth-page__card">
        <div className="auth-page__brand">
          <i className="bx bx-store auth-page__brand-icon"></i>
          <span className="auth-page__brand-name">TRANSDE</span>
        </div>

        {/* Progress indicator */}
        {step !== STEPS.DONE && (
          <div className="forgot-steps">
            {["Nhập email", "Xác thực OTP", "Mật khẩu mới"].map((label, i) => {
              const stepKeys = [STEPS.EMAIL, STEPS.OTP, STEPS.RESET];
              const currentIndex = stepKeys.indexOf(step);
              const isActive = i === currentIndex;
              const isDone = i < currentIndex;
              return (
                <div
                  key={i}
                  className={`forgot-steps__item
                    ${isActive ? "forgot-steps__item--active" : ""}
                    ${isDone ? "forgot-steps__item--done" : ""}
                  `}
                >
                  <div className="forgot-steps__dot">
                    {isDone ? (
                      <i className="bx bx-check"></i>
                    ) : (
                      <span>{i + 1}</span>
                    )}
                  </div>
                  <span className="forgot-steps__label">{label}</span>
                </div>
              );
            })}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="auth-page__alert auth-page__alert--error">
            <i className="bx bx-error-circle"></i>
            {error}
          </div>
        )}

        {/* ── BƯỚC 1: Email ── */}
        {step === STEPS.EMAIL && (
          <>
            <h1 className="auth-page__title">Quên mật khẩu</h1>
            <p className="auth-page__subtitle">
              Nhập email đã đăng ký. Chúng tôi sẽ gửi mã OTP để xác thực.
            </p>
            <div className="auth-form">
              <div className="auth-form__field">
                <label className="auth-form__label">Email</label>
                <div className="auth-form__input-wrapper">
                  <i className="bx bx-envelope auth-form__input-icon"></i>
                  <input
                    type="email"
                    placeholder="email@example.com"
                    className="auth-form__input"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      clearError();
                    }}
                    onKeyDown={(e) => e.key === "Enter" && handleSendEmail()}
                  />
                </div>
              </div>
              <button
                className="auth-form__submit btn btn--primary"
                onClick={handleSendEmail}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <i className="bx bx-loader-alt bx-spin"></i> Đang gửi...
                  </>
                ) : (
                  "Gửi mã OTP"
                )}
              </button>
            </div>
          </>
        )}

        {/* ── BƯỚC 2: OTP ── */}
        {step === STEPS.OTP && (
          <>
            <h1 className="auth-page__title">Nhập mã OTP</h1>
            <p className="auth-page__subtitle">
              Mã OTP đã được gửi đến <strong>{email}</strong>. Vui lòng kiểm tra
              hộp thư.
            </p>
            <div className="auth-form">
              <div className="auth-form__field">
                <label className="auth-form__label">Mã OTP</label>
                <div className="auth-form__input-wrapper">
                  <i className="bx bx-key auth-form__input-icon"></i>
                  <input
                    type="text"
                    placeholder="Nhập mã OTP"
                    className="auth-form__input auth-form__input--otp"
                    value={otp}
                    maxLength={8}
                    onChange={(e) => {
                      setOtp(e.target.value);
                      clearError();
                    }}
                    onKeyDown={(e) => e.key === "Enter" && handleVerifyOtp()}
                    autoComplete="one-time-code"
                  />
                </div>
              </div>
              <button
                className="auth-form__submit btn btn--primary"
                onClick={handleVerifyOtp}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <i className="bx bx-loader-alt bx-spin"></i> Đang xác
                    thực...
                  </>
                ) : (
                  "Xác nhận OTP"
                )}
              </button>
              <button
                className="auth-form__resend"
                onClick={() => {
                  setStep(STEPS.EMAIL);
                  setOtp("");
                  clearError();
                }}
              >
                <i className="bx bx-refresh"></i> Gửi lại mã
              </button>
            </div>
          </>
        )}

        {/* ── BƯỚC 3: Mật khẩu mới ── */}
        {step === STEPS.RESET && (
          <>
            <h1 className="auth-page__title">Đặt mật khẩu mới</h1>
            <p className="auth-page__subtitle">
              Mật khẩu mới phải có ít nhất 6 ký tự.
            </p>
            <div className="auth-form">
              <div className="auth-form__field">
                <label className="auth-form__label">Mật khẩu mới</label>
                <div className="auth-form__input-wrapper">
                  <i className="bx bx-lock-alt auth-form__input-icon"></i>
                  <input
                    type={showPassword ? "text" : "password"}
                    name="new_password"
                    placeholder="Tối thiểu 6 ký tự"
                    className="auth-form__input"
                    value={passwords.new_password}
                    onChange={(e) => {
                      setPasswords((p) => ({
                        ...p,
                        new_password: e.target.value,
                      }));
                      clearError();
                    }}
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    className="auth-form__toggle-pw"
                    onClick={() => setShowPassword((v) => !v)}
                    tabIndex={-1}
                  >
                    <i
                      className={`bx ${showPassword ? "bx-hide" : "bx-show"}`}
                    ></i>
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
                    value={passwords.confirm_password}
                    onChange={(e) => {
                      setPasswords((p) => ({
                        ...p,
                        confirm_password: e.target.value,
                      }));
                      clearError();
                    }}
                    autoComplete="new-password"
                  />
                </div>
              </div>
              <button
                className="auth-form__submit btn btn--primary"
                onClick={handleResetPassword}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <i className="bx bx-loader-alt bx-spin"></i> Đang lưu...
                  </>
                ) : (
                  "Đặt mật khẩu mới"
                )}
              </button>
            </div>
          </>
        )}

        {/* ── DONE ── */}
        {step === STEPS.DONE && (
          <div className="auth-page__done">
            <div className="auth-page__done-icon">
              <i className="bx bx-check-circle"></i>
            </div>
            <h1 className="auth-page__title">Thành công!</h1>
            <p className="auth-page__subtitle">
              Mật khẩu của bạn đã được cập nhật.
            </p>
            <button
              className="auth-form__submit btn btn--primary"
              onClick={() => navigate("/login")}
            >
              Về trang đăng nhập
            </button>
          </div>
        )}

        {step !== STEPS.DONE && (
          <p className="auth-page__footer-text">
            <Link to="/login" className="auth-form__link">
              <i className="bx bx-arrow-back"></i> Quay lại đăng nhập
            </Link>
          </p>
        )}
      </div>
    </div>
  );
}
