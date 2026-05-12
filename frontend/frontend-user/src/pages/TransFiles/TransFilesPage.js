import React, { useState, useEffect } from "react";
import TranslatorBox from "../../components/TranslatorBox/TranslatorBox";
import ModeSwitcher from "../../components/ModeSwitcher/ModeSwitcher";
import UploadBox from "../../components/UploadBox/UploadBox";
import useTranslation from "../../hooks/useTranslation";
import "./TransFilesPage.scss";

const MODES = [
  { id: "text", label: "Văn bản" },
  { id: "file", label: "Tệp đính kèm" },
];

function TransFilesPage() {
  const [mode, setMode] = useState("file");
  const [sourceLang, setSourceLang] = useState("vi");
  const [targetLang, setTargetLang] = useState("en");
  const [inputText, setInputText] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);

  const {
    languages,
    fetchLanguages,
    result,
    history,
    loading,
    error,
    success,
    translateText,
    translateDocument,
    fetchHistory,
    removeTranslation,
  } = useTranslation();

  const isFile = mode === "file";

  useEffect(() => {
    fetchLanguages();
    fetchHistory();
  }, [fetchLanguages, fetchHistory]);

  const handleAction = async () => {
    if (isFile) {
      if (!selectedFile) return alert("Vui lòng chọn tệp!");
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("source_lang", sourceLang);
      formData.append("target_lang", targetLang);
      const res = await translateDocument(formData);
      if (res.success) fetchHistory();
    } else {
      if (!inputText.trim()) return;
      const res = await translateText({
        text: inputText,
        source_lang: sourceLang,
        target_lang: targetLang,
      });
      if (res.success) fetchHistory();
    }
  };

  return (
    <div className="transfiles-page">
      <section className="translator">
        <ModeSwitcher modes={MODES} active={mode} onChange={setMode} />

        <TranslatorBox
          languages={languages}
          sourceLang={sourceLang}
          targetLang={targetLang}
          setSourceLang={setSourceLang}
          setTargetLang={setTargetLang}
          onSwapLangs={() => {
            setSourceLang(targetLang);
            setTargetLang(sourceLang);
          }}
          onTranslate={handleAction}
          loading={loading}
        >
          {isFile ? (
            <UploadBox
              onFileSelect={setSelectedFile}
              selectedFile={selectedFile}
              result={result}
              loading={loading}
              error={error}
            />
          ) : (
            <div className="text-mode-container">
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
                  readOnly
                />
              </div>
            </div>
          )}
        </TranslatorBox>
      </section>

      {/* LỊCH SỬ */}
      <section className="history-container container">
        <div className="history-header">
          <h2>Lịch sử dịch thuật ({history.length})</h2>
        </div>

        <div className="history-grid">
          {history.length > 0 ? (
            history.map((item) => (
              <div key={item.id} className="history-card">
                <div className="card-header">
                  <span className="type-badge">
                    {item.file_name ? "FILE" : "TEXT"}
                  </span>
                  <span className="date">
                    {new Date(item.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="card-body">
                  <p>
                    <strong>Gốc:</strong> {item.input_text || item.file_name}
                  </p>
                  <p className="result-text">
                    <strong>Dịch:</strong>{" "}
                    {item.translated_text || "Tài liệu đã được xử lý"}
                  </p>
                </div>
                <div className="card-footer">
                  <button
                    className="btn-icon"
                    onClick={() => removeTranslation(item.id)}
                  >
                    <i className="bx bx-trash"></i> Xóa
                  </button>
                  {item.file_url && (
                    <a
                      href={item.file_url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-link"
                    >
                      <i className="bx bx-download"></i> Tải về
                    </a>
                  )}
                </div>
              </div>
            ))
          ) : (
            <p>Chưa có dữ liệu lịch sử.</p>
          )}
        </div>
      </section>
    </div>
  );
}

export default TransFilesPage;
