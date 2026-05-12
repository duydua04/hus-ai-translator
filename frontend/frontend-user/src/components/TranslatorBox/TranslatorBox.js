import React from "react";
import "./TranslatorBox.scss";

function TranslatorBox({
  languages = [], // Danh sách ngôn ngữ từ API
  sourceLang, // Mã ngôn ngữ hiện tại (vd: "vi")
  targetLang, // Mã ngôn ngữ hiện tại (vd: "en")
  setSourceLang, // Hàm cập nhật
  setTargetLang, // Hàm cập nhật
  onSwapLangs,
  children,
  onTranslate,
  loading = false,
  actionLabel = "Dịch ngay",
}) {
  // Hàm tìm tên ngôn ngữ dựa vào mã (để hiển thị label)
  const getLangName = (code) => {
    const lang = languages.find((l) => l.language_code === code);
    return lang ? lang.language_name : code;
  };

  return (
    <div className="translator__box">
      {/* Tabs / Selectors */}
      <div className="translator__tabs">
        <div className="translator__select-wrapper">
          <select
            className="translator__select"
            value={sourceLang}
            onChange={(e) => setSourceLang(e.target.value)}
          >
            {languages.map((lang) => (
              <option key={lang.language_code} value={lang.language_code}>
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
              <option key={lang.language_code} value={lang.language_code}>
                {lang.language_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Content slot (Textareas hoặc UploadBox) */}
      <div className="translator__main-content">{children}</div>

      {/* Action Button */}
      <div className="translator__action">
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
