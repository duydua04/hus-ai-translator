import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import TranslatorBox from "../../components/TranslatorBox/TranslatorBox";
import ModeSwitcher from "../../components/ModeSwitcher/ModeSwitcher";
import UploadBox from "../../components/UploadBox/UploadBox";
import useTranslation from "../../hooks/useTranslation";
import useFeedback from "../../hooks/useFeedback";
import { FeedbackModal } from "../Feedback/FeedbackModal";
import "./HomePage.scss";

const MODES = [
  { id: "text", label: "Văn bản" },
  { id: "file", label: "Tệp đính kèm" },
];

const MAX_TEXT_LENGTH = 1024;

function TransFilesPage({ user }) {
  const navigate = useNavigate();
  const { mode } = useParams();

  const currentMode = ["text", "file"].includes(mode) ? mode : "text";
  const isFile = currentMode === "file";

  const [sourceLang, setSourceLang] = useState("");
  const [targetLang, setTargetLang] = useState("");
  const [inputText, setInputText] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackTranslationId, setFeedbackTranslationId] = useState(null);
  const [feedbackDone, setFeedbackDone] = useState(null);

  const {
    languages,
    fetchLanguages,
    result,
    setResult,
    loading,
    error,
    success,
    translateText,
    translateDocument,
    clearMessages,
  } = useTranslation();

  const {
    submitFeedback,
    fetchFeedbackByTranslation,
    loading: feedbackLoading,
  } = useFeedback();

  useEffect(() => {
    fetchLanguages();
  }, [fetchLanguages]);

  useEffect(() => {
    if (languages.length >= 2 && !sourceLang && !targetLang) {
      setSourceLang(languages[0].id);
      setTargetLang(languages[1].id);
    }
  }, [languages]);

  useEffect(() => {
    const translationId =
      result?.data?.translation_id || result?.translation_id;

    if (!translationId) {
      setFeedbackDone(null);
      return;
    }

    setFeedbackTranslationId(translationId);
    setFeedbackDone(null);

    fetchFeedbackByTranslation(translationId).then((res) => {
      setFeedbackDone(res?.success && res?.data ? true : false);
    });
  }, [result]);

  const handleModeChange = (newMode) => {
    if (newMode === "file" && !user) {
      navigate("/login");
      return;
    }
    clearMessages();
    setResult(null); // ← thêm dòng này
    setSelectedFile(null); // ← thêm dòng này
    setFeedbackTranslationId(null); // ← thêm dòng này
    setFeedbackDone(null); // ← thêm dòng này
    navigate(`/home/${newMode}`);
  };
  const handleTextChange = (e) => {
    if (e.target.value.length <= MAX_TEXT_LENGTH) {
      setInputText(e.target.value);
    }
  };

  const handleSwapLangs = () => {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    if (result?.data?.translated_text) {
      setInputText(result.data.translated_text);
      clearMessages();
    }
  };

  const handleAction = async () => {
    if (isFile) {
      if (!selectedFile) return alert("Vui lòng chọn tệp!");
      await translateDocument({
        file: selectedFile,
        source_lang_id: sourceLang,
        target_lang_id: targetLang,
        llm_model: "gpt-4o",
      });
      return;
    }

    if (!inputText.trim()) return;

    const sourceLangObj = languages.find((l) => l.id === sourceLang);
    const targetLangObj = languages.find((l) => l.id === targetLang);

    await translateText({
      text: inputText,
      source_lang_code: sourceLangObj?.language_code || "",
      target_lang_code: targetLangObj?.language_code || "",
      llm_model: "gpt-4o",
    });
  };

  const handleClearText = () => {
    setInputText("");
    setSelectedFile(null);
    setFeedbackTranslationId(null);
    setFeedbackDone(null);
    setResult(null);
    clearMessages();
  };

  const handleCopyResult = () => {
    const text = result?.data?.translated_text || "";
    if (text) navigator.clipboard.writeText(text);
  };

  const handleOpenFeedback = () => setShowFeedbackModal(true);

  const handleFeedbackSubmit = async (payload) => {
    const res = await submitFeedback({
      ...payload,
      translation_id: feedbackTranslationId,
    });
    if (res?.success) {
      setShowFeedbackModal(false);
      setFeedbackDone(true);
    }
  };

  const sseStatus = isFile ? result?.status : null;
  const sseProgress = isFile ? result?.progress ?? 0 : 0;
  const sseMessage = isFile ? result?.message : null;

  const translationId = result?.data?.translation_id || result?.translation_id;
  const isOverLimit = inputText.length >= MAX_TEXT_LENGTH;

  const showFeedbackBtn =
    !!translationId &&
    !error &&
    feedbackDone === false &&
    (isFile ? sseStatus === "completed" : true);

  const isActionLoading = isFile
    ? loading ||
      (!!translationId &&
        !error &&
        feedbackDone === null &&
        sseStatus === "completed")
    : loading || (!!translationId && !error && feedbackDone === null);

  const mainActionLabel = showFeedbackBtn ? "Đánh giá bản dịch" : "Dịch ngay";
  const onMainAction = showFeedbackBtn ? handleOpenFeedback : handleAction;

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
          onSwapLangs={handleSwapLangs}
          onTranslate={onMainAction}
          actionLabel={mainActionLabel}
          loading={isActionLoading}
        >
          {isFile ? (
            <UploadBox
              onFileSelect={setSelectedFile}
              selectedFile={selectedFile}
              result={result}
              loading={loading}
              error={error}
              success={success}
              sseStatus={sseStatus}
              sseProgress={sseProgress}
              sseMessage={sseMessage}
              feedbackDone={feedbackDone}
            />
          ) : (
            <div className="text-mode-container">
              <div className="translator__content">
                <textarea
                  className="translator__input"
                  placeholder="Nhập văn bản..."
                  value={inputText}
                  onChange={handleTextChange}
                />
                <textarea
                  className="translator__output"
                  placeholder="Bản dịch..."
                  value={result?.data?.translated_text || ""}
                  readOnly
                />
              </div>

              <div className="translator__selector">
                <div
                  className={`translator__selector-left ${
                    isOverLimit ? "at-limit" : ""
                  }`}
                >
                  {inputText.length}/{MAX_TEXT_LENGTH} ký tự
                </div>
                <div className="translator__selector-right">
                  <button
                    className="action-btn"
                    onClick={handleClearText}
                    title="Xóa"
                    disabled={loading}
                  >
                    <i className="bx bx-trash" />
                  </button>
                  <button
                    className="action-btn"
                    onClick={handleCopyResult}
                    title="Sao chép"
                    disabled={!result?.data?.translated_text}
                  >
                    <i className="bx bx-copy" />
                  </button>
                </div>
              </div>

              {feedbackDone === true && (
                <p className="status-msg success">
                  <i className="bx bx-check-circle" /> Cảm ơn bạn đã đóng góp ý
                  kiến!
                </p>
              )}

              {error && (
                <p className="status-msg error">
                  <i className="bx bx-error-circle" />
                  {typeof error === "object"
                    ? error.detail?.[0]?.msg || error.detail || "Có lỗi xảy ra"
                    : error}
                </p>
              )}

              {success && (
                <p className="status-msg success">
                  <i className="bx bx-check-circle" /> {success}
                </p>
              )}
            </div>
          )}
        </TranslatorBox>
      </section>

      {showFeedbackModal && (
        <FeedbackModal
          feedback={null}
          onClose={() => setShowFeedbackModal(false)}
          onSubmit={handleFeedbackSubmit}
          loading={feedbackLoading}
        />
      )}
    </div>
  );
}

export default TransFilesPage;
