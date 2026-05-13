import React, { useState } from "react";
import "./AddLanguage.scss";

export default function AddLanguageForm({ onSubmit, onCancel }) {
  const [form, setForm] = useState({ language_code: "", language_name: "" });
  const [formError, setFormError] = useState(null);
  const [formLoading, setFormLoading] = useState(false);

  const handleChange = (e) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
    setFormError(null);
  };

  const handleSubmit = async () => {
    if (!form.language_code.trim() || !form.language_name.trim()) {
      setFormError("Vui lòng điền đầy đủ mã và tên ngôn ngữ.");
      return;
    }
    setFormLoading(true);
    setFormError(null);
    try {
      await onSubmit({
        language_code: form.language_code.trim().toLowerCase(),
        language_name: form.language_name.trim(),
      });
      setForm({ language_code: "", language_name: "" });
    } catch (err) {
      setFormError(err.response?.data?.detail || "Thêm ngôn ngữ thất bại.");
    } finally {
      setFormLoading(false);
    }
  };

  const handleCancel = () => {
    setForm({ language_code: "", language_name: "" });
    setFormError(null);
    onCancel();
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) handleCancel();
  };

  return (
    <div className="add-lang-form-overlay" onClick={handleOverlayClick}>
      <div className="add-lang-form">
        {/* Header */}
        <div className="add-lang-form__header">
          <span className="add-lang-form__title">Thêm ngôn ngữ mới</span>
          <button className="add-lang-form__close" onClick={handleCancel}>
            <i className="bx bx-x" />
          </button>
        </div>

        {/* Body */}
        <div className="add-lang-form__body">
          <div className="add-lang-form__row">
            <div className="add-lang-form__field">
              <label className="add-lang-form__label">Mã ngôn ngữ</label>
              <input
                className="add-lang-form__input"
                name="language_code"
                placeholder="vd: en, vi, ja"
                value={form.language_code}
                onChange={handleChange}
                maxLength={10}
              />
            </div>
            <div className="add-lang-form__field">
              <label className="add-lang-form__label">Tên ngôn ngữ</label>
              <input
                className="add-lang-form__input"
                name="language_name"
                placeholder="vd: English, Tiếng Việt"
                value={form.language_name}
                onChange={handleChange}
              />
            </div>
          </div>

          {formError && (
            <div className="add-lang-form__error">
              <i className="bx bx-error-circle" />
              {formError}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="add-lang-form__footer">
          <button className="btn btn--ghost" onClick={handleCancel}>
            Hủy
          </button>
          <button
            className="btn btn--primary"
            onClick={handleSubmit}
            disabled={formLoading}
          >
            {formLoading ? (
              <>
                <i className="bx bx-loader-alt bx-spin" />
                Đang lưu...
              </>
            ) : (
              <>
                <i className="bx bx-plus" />
                Lưu ngôn ngữ
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
