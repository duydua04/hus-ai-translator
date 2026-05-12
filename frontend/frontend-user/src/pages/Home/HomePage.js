import React, { useState, useEffect } from "react";
import TranslatorBox from "../../components/TranslatorBox/TranslatorBox";
import IntroSection from "../../components/IntroSection/IntroSection";
import useTranslation from "../../hooks/useTranslation";
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
    languages,
    fetchLanguages,
    result,
    history,
    loading,
    error,
    success,
    translateText,
    fetchHistory,
    removeTranslation,
  } = useTranslation();

  const [sourceLang, setSourceLang] = useState("vi");
  const [targetLang, setTargetLang] = useState("en");
  const [inputText, setInputText] = useState("");

  // Khởi tạo dữ liệu: Ngôn ngữ và Lịch sử
  useEffect(() => {
    fetchLanguages();
    fetchHistory({ limit: 5 });
  }, [fetchLanguages, fetchHistory]);

  // Tự động cập nhật source/target lang
  useEffect(() => {
    if (languages.length > 0) {
      const hasVi = languages.find((l) => l.language_code === "vi");
      const hasEn = languages.find((l) => l.language_code === "en");
      if (hasVi) setSourceLang("vi");
      if (hasEn) setTargetLang("en");
    }
  }, [languages]);

  const handleTranslate = async () => {
    if (!inputText.trim()) return;
    const res = await translateText({
      text: inputText,
      source_lang: sourceLang,
      target_lang: targetLang,
    });
    if (res.success) fetchHistory({ limit: 5 });
  };

  const handleSwapLangs = () => {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
  };

  return (
    <>
      <section className="translator">
        <TranslatorBox
          languages={languages}
          sourceLang={sourceLang}
          targetLang={targetLang}
          setSourceLang={setSourceLang}
          setTargetLang={setTargetLang}
          onSwapLangs={handleSwapLangs}
          onTranslate={handleTranslate}
          loading={loading}
        >
          <div className="translator__content">
            <textarea
              className="translator__input"
              placeholder="Nhập văn bản..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
            <textarea
              className="translator__output"
              placeholder="Bản dịch..."
              value={result?.translated_text || ""}
              disabled
              readOnly
            />
          </div>

          <div className="translator__selector">
            <div className="translator__selector-left">
              {inputText.length}/5000 ký tự
            </div>
            <div className="translator__selector-right">
              <button
                className="action-btn"
                onClick={() => setInputText("")}
                title="Xóa"
              >
                <i className="bx bx-trash"></i>
              </button>
              <button
                className="action-btn"
                onClick={() =>
                  navigator.clipboard.writeText(result?.translated_text || "")
                }
                title="Sao chép"
              >
                <i className="bx bx-copy"></i>
              </button>
            </div>
          </div>

          {error && <p className="status-msg error">{error}</p>}
          {success && <p className="status-msg success">{success}</p>}
        </TranslatorBox>
      </section>

      {/* LỊCH SỬ GẦN ĐÂY */}
      <section className="history-section container">
        <h3>Lịch sử gần đây</h3>
        <div className="history-list">
          {history.length > 0 ? (
            history.map((item) => (
              <div key={item.id} className="history-item">
                <div className="history-info">
                  <span className="lang-tag">
                    {item.source_lang} → {item.target_lang}
                  </span>
                  <p>{item.input_text || item.file_name}</p>
                </div>
                <div className="history-actions">
                  <button
                    onClick={() => alert(`Bản dịch: ${item.translated_text}`)}
                    title="Xem"
                  >
                    <i className="bx bx-show"></i>
                  </button>
                  <button
                    onClick={() => removeTranslation(item.id)}
                    className="delete-btn"
                    title="Xóa"
                  >
                    <i className="bx bx-x"></i>
                  </button>
                </div>
              </div>
            ))
          ) : (
            <p className="empty-msg">Chưa có lịch sử dịch thuật.</p>
          )}
        </div>
      </section>

      <section className="intro">
        <IntroSection title="Hỗ trợ dịch" cards={INTRO_FIRST} variant="first" />
        <IntroSection title="Giúp bạn" cards={INTRO_SECOND} variant="second" />
      </section>
    </>
  );
}

export default HomePage;
