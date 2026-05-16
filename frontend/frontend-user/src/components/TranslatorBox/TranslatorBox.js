import React from "react";
import "./TranslatorBox.scss";

function TranslatorBox({
  languages = [],
  sourceLang,
  targetLang,
  setSourceLang,
  setTargetLang,
  onSwapLangs,
  children,
  onTranslate,
  loading = false,
  actionLabel = "Dịch ngay",
  onCancel = null,
}) {
  return (
    <div className="translator__box">
      <div className="translator__tabs">
        <div className="translator__select-wrapper">
          <select
            className="translator__select"
            value={sourceLang}
            onChange={(e) => setSourceLang(e.target.value)}
          >
            {languages.map((lang) => (
              <option key={lang.id} value={lang.id}>
                {lang.language_name}
              </option>
            ))}
          </select>
        </div>

        <button
          className="translator__swap-btn"
          onClick={onSwapLangs}
          type="button"
        >
          <i className="bx bx-transfer"></i>
        </button>

        <div className="translator__select-wrapper">
          <select
            className="translator__select"
            value={targetLang}
            onChange={(e) => setTargetLang(e.target.value)}
          >
            {languages.map((lang) => (
              <option key={lang.id} value={lang.id}>
                {lang.language_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="translator__main-content">{children}</div>

      <div className="translator__action">
        {onCancel && (
          <button className="btn btn--primary" onClick={onCancel} type="button">
            Hủy
          </button>
        )}
        <button
          className={`btn btn--primary ${loading ? "btn--loading" : ""}`}
          onClick={onTranslate}
          disabled={loading}
        >
          {loading ? (
            <>
              <i className="bx bx-loader-alt bx-spin"></i> Đang xử lý...
            </>
          ) : (
            actionLabel
          )}
        </button>
      </div>
    </div>
  );
}

export default TranslatorBox;
