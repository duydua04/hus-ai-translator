import React, { useState, useEffect } from "react";

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

export default function InfoTab({
  profile,
  loading,
  error,
  success,
  onUpdate,
  onClearMessages,
}) {
  const [fullName, setFullName] = useState("");

  useEffect(() => {
    if (profile) setFullName(profile.full_name || "");
  }, [profile]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    onClearMessages();
    const payload = {};
    if (fullName !== profile?.full_name) payload.full_name = fullName;
    if (!Object.keys(payload).length) return;
    await onUpdate(payload);
  };

  const isDirty = fullName !== (profile?.full_name || "");

  return (
    <div className="profile-page__card">
      <h2 className="profile-page__card-title">Cập nhật thông tin cá nhân</h2>

      <Alert type={success ? "success" : "error"} message={success || error} />

      <form className="profile-page__form" onSubmit={handleSubmit}>
        <div className="profile-page__field">
          <label className="profile-page__label" htmlFor="email">
            Địa chỉ email
          </label>
          <input
            id="email"
            type="email"
            className="profile-page__input"
            value={profile?.email || ""}
            disabled
          />
          <span className="profile-page__input-hint">
            Email không thể thay đổi.
          </span>
        </div>

        <div className="profile-page__field">
          <label className="profile-page__label" htmlFor="fullName">
            Họ và tên
          </label>
          <input
            id="fullName"
            type="text"
            className="profile-page__input"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Nhập họ và tên của bạn"
          />
        </div>

        <div className="profile-page__actions">
          <button
            type="submit"
            className="profile-page__btn profile-page__btn--primary"
            disabled={loading || !isDirty}
          >
            {loading ? "Đang lưu..." : "Lưu thay đổi"}
          </button>
          {isDirty && (
            <button
              type="button"
              className="profile-page__btn profile-page__btn--ghost"
              onClick={() => {
                setFullName(profile?.full_name || "");
                onClearMessages();
              }}
            >
              Huỷ
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
