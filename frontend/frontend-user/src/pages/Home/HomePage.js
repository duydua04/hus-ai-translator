import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import TranslatorBox from "../../components/TranslatorBox/TranslatorBox";
import ModeSwitcher from "../../components/ModeSwitcher/ModeSwitcher";
import UploadBox from "../../components/UploadBox/UploadBox";
import useTranslation from "../../hooks/useTranslation";
import "./HomePage.scss";

const MODES = [
  { id: "text", label: "Văn bản" },
  { id: "file", label: "Tệp đính kèm" },
];

function TransFilesPage({ user }) {
  const navigate = useNavigate();
  const { mode } = useParams();

  const currentMode = ["text", "file"].includes(mode) ? mode : "text";
  const isFile = currentMode === "file";

  // Lưu UUID của ngôn ngữ, không lưu code string
  const [sourceLang, setSourceLang] = useState("");
  const [targetLang, setTargetLang] = useState("");
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
    clearMessages,
  } = useTranslation();

  useEffect(() => {
    fetchLanguages();
    fetchHistory();
  }, [fetchLanguages, fetchHistory]);

  // Auto-set ngôn ngữ mặc định sau khi danh sách ngôn ngữ load xong
  useEffect(() => {
    if (languages.length >= 2 && !sourceLang && !targetLang) {
      setSourceLang(languages[0].id);
      setTargetLang(languages[1].id);
    }
  }, [languages]);

  const handleModeChange = (newMode) => {
    if (newMode === "file" && !user) {
      navigate("/login");
      return;
    }
    navigate(`/home/${newMode}`);
  };

  const handleAction = async () => {
    if (isFile) {
      if (!selectedFile) return alert("Vui lòng chọn tệp!");
      const res = await translateDocument({
        file: selectedFile,
        source_lang_id: sourceLang,
        target_lang_id: targetLang,
        llm_model: "gpt-4o",
      });
      if (res.success) fetchHistory();
    } else {
      if (!inputText.trim()) return;
      const res = await translateText({
        input_content: inputText,
        source_lang_id: sourceLang,
        target_lang_id: targetLang,
        llm_model: "gpt-4o",
      });
      if (res.success) {
        fetchHistory();
        setTimeout(() => {
          clearMessages();
        }, 3000);
      }
    }
  };

  return (
    <div className="transfiles-page">
      <section className="translator">
        <ModeSwitcher
          modes={MODES}
          active={currentMode}
          onChange={handleModeChange}
        />

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
                  value={result?.translated_content || ""}
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
                      navigator.clipboard.writeText(
                        result?.translated_content || ""
                      )
                    }
                    title="Sao chép"
                  >
                    <i className="bx bx-copy"></i>
                  </button>
                </div>
              </div>

              {error && <p className="status-msg error">{error}</p>}
              {success && <p className="status-msg success">{success}</p>}
            </div>
          )}
        </TranslatorBox>
      </section>

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
                    {item.type === "document_pdf" ? "FILE" : "TEXT"}
                  </span>
                  <span className="date">
                    {new Date(item.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="card-body">
                  <p>
                    <strong>Gốc:</strong> {item.input_content || "(Tài liệu)"}
                  </p>
                  <p className="result-text">
                    <strong>Dịch:</strong>{" "}
                    {item.translated_content || "Tài liệu đã được xử lý"}
                  </p>
                </div>
                <div className="card-footer">
                  <button
                    className="btn-icon"
                    onClick={() => removeTranslation(item.id)}
                  >
                    <i className="bx bx-trash"></i> Xóa
                  </button>
                  {item.result_file_id && (
                    <a
                      href={item.result_file_id}
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
