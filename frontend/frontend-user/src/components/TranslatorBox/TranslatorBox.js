import React from "react";
import "./TranslatorBox.scss";

function TranslatorBox({
  sourceLang,
  targetLang,
  onSwapLangs,
  children,
  onTranslate,
  loading = false,
  actionLabel = "Dịch ngay",
}) {
  return (
    <div className="translator__box">
      {/* Tabs */}
      <div className="translator__tabs">
        <span className="translator__tab translator__tab--active">
          {sourceLang.label}
        </span>
        <i className="bx bx-transfer" onClick={onSwapLangs}></i>
        <span className="translator__tab">{targetLang.label}</span>
      </div>

      {/* Content slot */}
      {children}

      {/* Action */}
      <div className="translator__action">
        <button
          className="btn btn--primary"
          onClick={onTranslate}
          disabled={loading}
        >
          {loading ? "Đang dịch..." : actionLabel}
        </button>
      </div>
    </div>
  );
}

export default TranslatorBox;
