import { useState, useCallback } from "react";
import {
  getLanguage as apiGetLanguages,
  translateText as apiTranslateText,
  uploadFile as apiUploadFile,
  startFileTranslation as apiStartFileTranslation,
  openSSEStream,
} from "../api/translationApi";

const MAX_TEXT_LENGTH = 1024;
const MAX_FILE_SIZE_MB = 5;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
const MESSAGE_DURATION_MS = 3000;

export default function useTranslation() {
  const [languages, setLanguages] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

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

  const fetchLanguages = useCallback(async () => {
    try {
      const data = await apiGetLanguages();
      setLanguages(data);
    } catch (err) {
      console.error("Không thể lấy danh sách ngôn ngữ", err);
    }
  }, []);

  const translateText = useCallback(async (payload) => {
    if (payload.input_content?.length > MAX_TEXT_LENGTH) {
      showError(`Văn bản không được vượt quá ${MAX_TEXT_LENGTH} ký tự.`);
      return { success: false };
    }

    setLoading(true);
    clearMessages();
    try {
      const data = await apiTranslateText(payload);
      setResult(data);
      showSuccess("Dịch văn bản thành công.");
      return { success: true, data };
    } catch (err) {
      const msg = err.response?.data?.detail || "Dịch văn bản thất bại.";
      showError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  // upload => SSE stream => startFileTranslation
  const translateDocument = useCallback(async (payload) => {
    const { file, source_lang_id, target_lang_id, llm_model } = payload;

    if (file?.size > MAX_FILE_SIZE_BYTES) {
      showError(`File không được vượt quá ${MAX_FILE_SIZE_MB}MB.`);
      return { success: false };
    }

    setLoading(true);
    setResult(null);
    clearMessages();

    try {
      const formData = new FormData();
      formData.append("file", file);
      const uploadData = await apiUploadFile(formData);

      const fileId =
        uploadData?.data?.file_id ||
        uploadData?.data?.id ||
        uploadData?.file_id ||
        uploadData?.id;

      if (!fileId)
        throw new Error("Upload file thất bại, không nhận được file_id.");

      const clientId = crypto.randomUUID();

      await new Promise((resolve, reject) => {
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
          (err) => {
            reject(new Error("Kết nối SSE thất bại."));
          }
        );

        apiStartFileTranslation(clientId, {
          input_file_id: fileId,
          source_lang_id,
          target_lang_id,
          llm_model,
        }).catch(reject);
      });

      return { success: true };
    } catch (err) {
      const msg =
        err.response?.data?.detail || err.message || "Dịch tài liệu thất bại.";
      showError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    languages,
    fetchLanguages,
    result,
    loading,
    error,
    success,
    setResult,
    clearMessages,
    translateText,
    translateDocument,
  };
}
