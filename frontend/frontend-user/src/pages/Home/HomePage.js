import React from "react";
import TranslatorBox from "../../components/TranslatorBox/TranslatorBox";
import IntroSection from "../../components/IntroSection/IntroSection";
import { useTranslator } from "../../hooks/useTranslator";
import "./HomePage.scss";

const INTRO_FIRST = [
  { id: 1, img: "https://picsum.photos/300/200", text: "Văn bản" },
  { id: 2, img: "https://picsum.photos/301/200", text: "Tài liệu" },
];

const INTRO_SECOND = [
  { id: 3, img: "https://picsum.photos/302/200", text: "Dịch thuật chính xác" },
  { id: 4, img: "https://picsum.photos/303/200", text: "Đánh giá chất lượng" },
  {
    id: 5,
    img: "https://picsum.photos/304/200",
    text: "Trích xuất thông tin bản dịch",
  },
];

function HomePage() {
  const {
    sourceLang,
    targetLang,
    inputText,
    outputText,
    loading,
    error,
    charCount,
    maxChars,
    handleSwapLangs,
    handleInputChange,
    handleClear,
    handleCopy,
    handleTranslate,
  } = useTranslator();

  return (
    <>
      {/* HERO */}
      <section className="translator">
        <TranslatorBox
          sourceLang={sourceLang}
          targetLang={targetLang}
          onSwapLangs={handleSwapLangs}
          onTranslate={handleTranslate}
          loading={loading}
        >
          <div className="translator__content">
            <textarea
              className="translator__input"
              placeholder="Nhập văn bản..."
              value={inputText}
              onChange={handleInputChange}
            ></textarea>
            <textarea
              className="translator__output"
              placeholder="Bản dịch..."
              value={outputText}
              disabled
              readOnly
            ></textarea>
          </div>

          <div className="translator__selector">
            <div className="translator__selector-left">
              {charCount}/{maxChars} ký tự
            </div>
            <div className="translator__selector-right">
              <button
                className="action-btn action-btn--delete"
                title="Xoá"
                onClick={handleClear}
              >
                <i className="bx bx-trash"></i>
              </button>
              <button
                className="action-btn action-btn--copy"
                title="Copy"
                onClick={handleCopy}
              >
                <i className="bx bx-copy"></i>
              </button>
            </div>
          </div>

          {error && <p className="translator__error">{error}</p>}
        </TranslatorBox>
      </section>

      {/* INTRO */}
      <section className="intro">
        <IntroSection title="Hỗ trợ dịch" cards={INTRO_FIRST} variant="first" />
        <IntroSection title="Giúp bạn" cards={INTRO_SECOND} variant="second" />
      </section>
    </>
  );
}

export default HomePage;
