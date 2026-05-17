import { useState, useCallback, useRef } from "react";
import {
  getLanguage as apiGetLanguages,
  translateText as apiTranslateText,
  uploadFile as apiUploadFile,
  startFileTranslation as apiStartFileTranslation,
  openSSEStream,
} from "../api/translationApi";

const MAX_TEXT_LENGTH = 2000;
const MAX_FILE_SIZE_MB = 5;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
const MESSAGE_DURATION_MS = 3000;

export default function useTranslation() {
  const [languages, setLanguages] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const abortControllerRef = useRef(null);

  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  const showError = useCallback((msg) => {
    setError(msg);
    setTimeout(() => setError(null), MESSAGE_DURATION_MS);
  }, []);

  const showSuccess = useCallback((msg) => {
    setSuccess(msg);
    setTimeout(() => setSuccess(null), MESSAGE_DURATION_MS);
  }, []);

  const createAbortSignal = useCallback(() => {
    abortControllerRef.current?.abort();
    const controller = new AbortController();
    abortControllerRef.current = controller;
    return controller.signal;
  }, []);

  const isAbortError = (err) =>
    err.name === "AbortError" || err.code === "ERR_CANCELED";

  const fetchLanguages = useCallback(async () => {
    try {
      const data = await apiGetLanguages();
      setLanguages(data);
    } catch (err) {
      console.error("Không thể lấy danh sách ngôn ngữ", err);
    }
  }, []);

  const translateText = useCallback(
    async (payload) => {
      if (payload.input_content?.length > MAX_TEXT_LENGTH) {
        showError(`Văn bản không được vượt quá ${MAX_TEXT_LENGTH} ký tự.`);
        return { success: false };
      }

      const signal = createAbortSignal();
      setLoading(true);
      clearMessages();

      try {
        const data = await apiTranslateText(payload, signal);
        setResult(data);
        showSuccess("Dịch văn bản thành công.");
        return { success: true, data };
      } catch (err) {
        if (isAbortError(err)) return { success: false, aborted: true };
        const msg = err.response?.data?.detail || "Dịch văn bản thất bại.";
        showError(msg);
        return { success: false, message: msg };
      } finally {
        setLoading(false);
      }
    },
    [createAbortSignal, clearMessages, showError, showSuccess]
  );

  const translateDocument = useCallback(
    async ({ file, source_lang_id, target_lang_id, llm_model }) => {
      if (file?.size > MAX_FILE_SIZE_BYTES) {
        showError(`File không được vượt quá ${MAX_FILE_SIZE_MB}MB.`);
        return { success: false };
      }

      const signal = createAbortSignal();
      setLoading(true);
      setResult(null);
      clearMessages();

      try {
        const formData = new FormData();
        formData.append("file", file);
        const uploadData = await apiUploadFile(formData, signal);

        const fileId =
          uploadData?.data?.file_id ||
          uploadData?.data?.id ||
          uploadData?.file_id ||
          uploadData?.id;

        if (!fileId)
          throw new Error("Upload file thất bại, không nhận được file_id.");

        const clientId = crypto.randomUUID();

        await new Promise((resolve, reject) => {
          if (signal.aborted) {
            reject(new DOMException("Aborted", "AbortError"));
            return;
          }

          const es = openSSEStream(
            clientId,
            (data) => {
              setResult(data);
              if (data.status === "success" || data.status === "completed") {
                showSuccess("Dịch tài liệu thành công.");
                es.close();
                resolve(data);
              }
              if (data.status === "error") {
                es.close();
                reject(new Error(data.message));
              }
            },
            () => reject(new Error("Kết nối SSE thất bại."))
          );

          signal.addEventListener("abort", () => {
            es.close();
            reject(new DOMException("Aborted", "AbortError"));
          });

          apiStartFileTranslation(
            clientId,
            {
              input_file_id: fileId,
              source_lang_id,
              target_lang_id,
              llm_model,
            },
            signal
          ).catch(reject);
        });

        return { success: true };
      } catch (err) {
        if (isAbortError(err)) return { success: false, aborted: true };
        const msg =
          err.response?.data?.detail ||
          err.message ||
          "Dịch tài liệu thất bại.";
        showError(msg);
        return { success: false, message: msg };
      } finally {
        setLoading(false);
      }
    },
    [createAbortSignal, clearMessages, showError, showSuccess]
  );

  const cancelTranslation = useCallback(() => {
    abortControllerRef.current?.abort();
    setLoading(false);
    setResult(null);
  }, []);

  return {
    languages,
    fetchLanguages,
    result,
    setResult,
    loading,
    error,
    success,
    clearMessages,
    translateText,
    translateDocument,
    cancelTranslation,
  };
}
