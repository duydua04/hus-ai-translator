import { useState, useCallback } from "react";
import { translateText } from "../api/translationApi";

const LANGS = [
  { code: "en", label: "Tiếng Anh" },
  { code: "vi", label: "Tiếng Việt" },
];
const MAX_CHARS = 5000;

export function useTranslator() {
  const [sourceLang, setSourceLang] = useState(LANGS[0]);
  const [targetLang, setTargetLang] = useState(LANGS[1]);
  const [inputText, setInputText] = useState("");
  const [outputText, setOutputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSwapLangs = useCallback(() => {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    setInputText(outputText);
    setOutputText(inputText);
  }, [sourceLang, targetLang, inputText, outputText]);

  const handleInputChange = useCallback((e) => {
    if (e.target.value.length <= MAX_CHARS) setInputText(e.target.value);
  }, []);

  const handleClear = useCallback(() => {
    setInputText("");
    setOutputText("");
    setError(null);
  }, []);

  const handleCopy = useCallback(() => {
    if (outputText) navigator.clipboard.writeText(outputText);
  }, [outputText]);

  const handleTranslate = useCallback(async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await translateText(
        inputText,
        sourceLang.code,
        targetLang.code
      );
      setOutputText(data.translatedText);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [inputText, sourceLang, targetLang]);

  return {
    langs: LANGS,
    sourceLang,
    targetLang,
    inputText,
    outputText,
    loading,
    error,
    charCount: inputText.length,
    maxChars: MAX_CHARS,
    handleSwapLangs,
    handleInputChange,
    handleClear,
    handleCopy,
    handleTranslate,
  };
}
