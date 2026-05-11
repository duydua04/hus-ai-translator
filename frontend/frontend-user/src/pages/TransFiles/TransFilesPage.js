import React, { useState } from "react";
import TranslatorBox from "../../components/TranslatorBox/TranslatorBox";
import ModeSwitcher from "../../components/ModeSwitcher/ModeSwitcher";
import UploadBox from "../../components/UploadBox/UploadBox";
import { useTranslator } from "../../hooks/useTranslator";
import { useFileTranslator } from "../../hooks/useFileTranslator";
import "./TransFilesPage.scss";

const MODES = [
  { id: "text", label: "Văn bản" },
  { id: "file", label: "Tệp đính kèm" },
];

function TransFilesPage() {
  const [mode, setMode] = useState("file");

  const textState = useTranslator();
  const fileState = useFileTranslator();

  const isFile = mode === "file";
  const currentLang = isFile ? fileState : textState;
  const onSwap = isFile ? fileState.handleSwapLangs : textState.handleSwapLangs;
  const onTranslate = isFile
    ? fileState.handleTranslate
    : textState.handleTranslate;
  const loading = isFile ? fileState.loading : textState.loading;

  return (
    <div className="transfiles-page">
      <section className="translator">
        <ModeSwitcher modes={MODES} active={mode} onChange={setMode} />

        <TranslatorBox
          sourceLang={currentLang.sourceLang}
          targetLang={currentLang.targetLang}
          onSwapLangs={onSwap}
          onTranslate={onTranslate}
          loading={loading}
        >
          {isFile ? (
            <UploadBox
              onFileSelect={fileState.handleFileSelect}
              selectedFile={fileState.selectedFile}
              result={fileState.result}
              loading={fileState.loading}
              error={fileState.error}
            />
          ) : (
            <>
              <div className="translator__content translator__content--text">
                <textarea
                  className="translator__input"
                  placeholder="Nhập văn bản..."
                  value={textState.inputText}
                  onChange={textState.handleInputChange}
                />
                <textarea
                  className="translator__output"
                  placeholder="Bản dịch..."
                  value={textState.outputText}
                  disabled
                  readOnly
                />
              </div>

              <div className="translator__selector">
                <div className="translator__selector-left">
                  {textState.charCount}/{textState.maxChars} ký tự
                </div>
                <div className="translator__selector-right">
                  <button
                    className="action-btn action-btn--delete"
                    title="Xoá"
                    onClick={textState.handleClear}
                  >
                    <i className="bx bx-trash" />
                  </button>
                  <button
                    className="action-btn action-btn--copy"
                    title="Copy"
                    onClick={textState.handleCopy}
                  >
                    <i className="bx bx-copy" />
                  </button>
                </div>
              </div>
            </>
          )}
        </TranslatorBox>
      </section>
    </div>
  );
}

export default TransFilesPage;
