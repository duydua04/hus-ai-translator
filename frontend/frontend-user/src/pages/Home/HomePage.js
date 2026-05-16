import React, { useState, useEffect, useRef, useCallback } from "react";
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

const MAX_TEXT_LENGTH = 2000;
const DEBOUNCE_DELAY_MS = 800;

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
  const [showThankYou, setShowThankYou] = useState(false);

  const debounceTimerRef = useRef(null);

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
    cancelTranslation,
  } = useTranslation();

  const { submitFeedback, loading: feedbackLoading } = useFeedback();

  const translatedText = result?.data?.translated_text || "";
  const translationId = result?.data?.translation_id || result?.translation_id;
  const isOverLimit = inputText.length >= MAX_TEXT_LENGTH;

  const sseStatus = isFile ? result?.status : null;
  const sseProgress = isFile ? result?.progress ?? 0 : 0;
  const sseMessage = isFile ? result?.message : null;

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

  // Helpers
  const clearDebounce = () => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
      debounceTimerRef.current = null;
    }
  };

  const scheduleTranslate = (text, srcLang, tgtLang) => {
    clearDebounce();
    debounceTimerRef.current = setTimeout(() => {
      runTranslateText(text, srcLang, tgtLang);
    }, DEBOUNCE_DELAY_MS);
  };

  const resetFeedbackState = () => {
    setFeedbackTranslationId(null);
    setFeedbackDone(null);
  };

  // Effects
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
    if (!translationId) {
      setFeedbackDone(null);
      return;
    }
    setFeedbackTranslationId(translationId);
    setFeedbackDone(false);
  }, [result]);

  useEffect(() => {
    return () => clearDebounce();
  }, []);

  // Handlers
  const runTranslateText = useCallback(
    async (text, srcLang, tgtLang) => {
      if (!text.trim()) return;
      const sourceLangObj = languages.find((l) => l.id === srcLang);
      const targetLangObj = languages.find((l) => l.id === tgtLang);
      await translateText({
        text,
        source_lang_code: sourceLangObj?.language_code || "",
        target_lang_code: targetLangObj?.language_code || "",
        llm_model: "gpt-4o",
      });
    },
    [languages, translateText]
  );

  const handleTextChange = (e) => {
    const newText = e.target.value;
    if (newText.length > MAX_TEXT_LENGTH) return;

    setInputText(newText);

    if (!newText.trim()) {
      clearDebounce();
      setResult(null);
      return;
    }

    scheduleTranslate(newText, sourceLang, targetLang);
  };

  const handleSourceLangChange = (langId) => {
    setSourceLang(langId);
    if (inputText.trim() && !isFile)
      scheduleTranslate(inputText, langId, targetLang);
  };

  const handleTargetLangChange = (langId) => {
    setTargetLang(langId);
    if (inputText.trim() && !isFile)
      scheduleTranslate(inputText, sourceLang, langId);
  };

  const handleModeChange = (newMode) => {
    if (newMode === "file" && !user) {
      navigate("/login");
      return;
    }
    clearDebounce();
    clearMessages();
    setResult(null);
    setSelectedFile(null);
    resetFeedbackState();
    navigate(`/home/${newMode}`);
  };

  const handleSwapLangs = () => {
    const newSource = targetLang;
    const newTarget = sourceLang;

    setSourceLang(newSource);
    setTargetLang(newTarget);

    if (translatedText) {
      setInputText(translatedText);
      setResult(null);
      resetFeedbackState();
      clearMessages();
      if (!isFile) {
        scheduleTranslate(translatedText, newSource, newTarget);
      }
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
    clearDebounce();
    await runTranslateText(inputText, sourceLang, targetLang);
  };

  const handleClearText = () => {
    clearDebounce();
    setInputText("");
    setSelectedFile(null);
    setResult(null);
    resetFeedbackState();
    clearMessages();
  };

  const handleCopyResult = () => {
    if (translatedText) navigator.clipboard.writeText(translatedText);
  };

  const handleFeedbackSubmit = async (payload) => {
    const res = await submitFeedback({
      ...payload,
      translation_id: feedbackTranslationId,
    });
    if (res?.success) {
      setShowFeedbackModal(false);
      setFeedbackDone(true);
      setShowThankYou(true);
      setTimeout(() => setShowThankYou(false), 3000);
    }
  };

  const handleCancel = () => {
    cancelTranslation();
    resetFeedbackState();
    clearMessages();
  };

  const mainActionLabel = showFeedbackBtn ? "Đánh giá bản dịch" : "Dịch ngay";
  const onMainAction = showFeedbackBtn
    ? () => setShowFeedbackModal(true)
    : handleAction;

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
          setSourceLang={handleSourceLangChange}
          setTargetLang={handleTargetLangChange}
          onSwapLangs={handleSwapLangs}
          onTranslate={onMainAction}
          actionLabel={mainActionLabel}
          loading={isActionLoading}
          onCancel={isFile && loading ? handleCancel : null}
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
                  value={translatedText}
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
                    disabled={!translatedText}
                  >
                    <i className="bx bx-copy" />
                  </button>
                </div>
              </div>

              {showThankYou && (
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
