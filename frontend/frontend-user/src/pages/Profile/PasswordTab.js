import React, { useState } from "react";

function Alert({ type, message }) {
  if (!message) return null;
  return (
    <div className={`profile-page__alert profile-page__alert--${type}`}>
      <i
        className={`bx ${
          type === "success" ? "bx-check-circle" : "bx-error-circle"
        }`}
      ></i>
      <span>{message}</span>
    </div>
  );
}

function PasswordInput({ id, label, value, onChange, hint }) {
  const [show, setShow] = useState(false);
  return (
    <div className="profile-page__field">
      <label className="profile-page__label" htmlFor={id}>
        {label}
      </label>
      <div className="profile-page__password-wrap">
        <input
          id={id}
          type={show ? "text" : "password"}
          className="profile-page__input"
          value={value}
          onChange={onChange}
          autoComplete="new-password"
        />
        <button
          type="button"
          className="profile-page__eye-btn"
          onClick={() => setShow((s) => !s)}
          tabIndex={-1}
          aria-label={show ? "Ẩn mật khẩu" : "Hiển thị mật khẩu"}
        >
          <i className={`bx ${show ? "bx-hide" : "bx-show"}`}></i>
        </button>
      </div>
      {hint && <span className="profile-page__input-hint">{hint}</span>}
    </div>
  );
}

export default function PasswordTab({
  loading,
  error,
  success,
  onChangePassword,
  onClearMessages,
}) {
  const [form, setForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [localError, setLocalError] = useState(null);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError(null);
    onClearMessages();

    if (form.new_password !== form.confirm_password) {
      setLocalError("Mật khẩu xác nhận không khớp.");
      return;
    }
    if (form.new_password.length < 6) {
      setLocalError("Mật khẩu mới phải có ít nhất 6 ký tự.");
      return;
    }

    const res = await onChangePassword({
      current_password: form.current_password,
      new_password: form.new_password,
      confirm_password: form.confirm_password,
    });

    if (res.success) {
      setForm({ current_password: "", new_password: "", confirm_password: "" });
    }
  };

  return (
    <div className="profile-page__card">
      <h2 className="profile-page__card-title">Đổi mật khẩu</h2>

      <Alert type="error" message={localError || error} />
      <Alert type="success" message={success} />

      <form className="profile-page__form" onSubmit={handleSubmit}>
        <PasswordInput
          id="currentPassword"
          label="Mật khẩu hiện tại"
          value={form.current_password}
          onChange={set("current_password")}
        />
        <PasswordInput
          id="newPassword"
          label="Mật khẩu mới"
          value={form.new_password}
          onChange={set("new_password")}
          hint="Tối thiểu 6 ký tự."
        />
        <PasswordInput
          id="confirmPassword"
          label="Xác nhận mật khẩu mới"
          value={form.confirm_password}
          onChange={set("confirm_password")}
        />

        <div className="profile-page__actions">
          <button
            type="submit"
            className="profile-page__btn profile-page__btn--primary"
            disabled={
              loading ||
              !form.current_password ||
              !form.new_password ||
              !form.confirm_password
            }
          >
            {loading ? "Đang xử lý..." : "Đổi mật khẩu"}
          </button>
          <button
            type="button"
            className="profile-page__btn profile-page__btn--ghost"
            onClick={() => {
              setForm({
                current_password: "",
                new_password: "",
                confirm_password: "",
              });
              setLocalError(null);
              onClearMessages();
            }}
          >
            Xoá form
          </button>
        </div>
      </form>
    </div>
  );
}
