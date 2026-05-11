import { useState, useCallback } from "react";
import { translateFile } from "../api/translationApi";

const LANGS = [
  { code: "en", label: "Tiếng Anh" },
  { code: "vi", label: "Tiếng Việt" },
];

export function useFileTranslator() {
  const [sourceLang, setSourceLang] = useState(LANGS[0]);
  const [targetLang, setTargetLang] = useState(LANGS[1]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSwapLangs = useCallback(() => {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
  }, [sourceLang, targetLang]);

  // accept — chuỗi MIME hoặc extension, vd ".pdf,.docx"
  const handleFileSelect = useCallback((accept) => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = accept;
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        setSelectedFile(file);
        setResult(null);
        setError(null);
      }
    };
    input.click();
  }, []);

  const handleTranslate = useCallback(async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    try {
      const data = await translateFile(
        selectedFile,
        sourceLang.code,
        targetLang.code
      );
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [selectedFile, sourceLang, targetLang]);

  return {
    langs: LANGS,
    sourceLang,
    targetLang,
    selectedFile,
    result,
    loading,
    error,
    handleSwapLangs,
    handleFileSelect,
    handleTranslate,
  };
}
