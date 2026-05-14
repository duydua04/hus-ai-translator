import axiosUser from "./axiosUser";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Dịch văn bản thuần
export const translateText = async (payload) => {
  const res = await axiosUser.post("/api/translations/text", payload);
  return res.data;
};

// Upload file PDF
export const uploadFile = async (formData) => {
  const res = await axiosUser.post("/api/upload/file", formData);
  return res.data;
};

// Lấy presigned URL để truy cập file
export const getFilePresignedUrl = async (params = {}) => {
  const res = await axiosUser.get("/api/files/presigned-url", { params });
  return res.data;
};

// Bắt đầu dịch file (sau khi upload)
export const startFileTranslation = async (clientId, payload) => {
  const res = await axiosUser.post(
    `/api/translations/file/start/${clientId}`,
    payload
  );
  return res.data;
};

// Lấy danh sách ngôn ngữ active
export const getLanguage = async () => {
  const res = await axiosUser.get("/languages");
  return res.data;
};

// CONTACT
export const submitContact = async (payload) => {
  const res = await axiosUser.post("/contact", payload);
  return res.data;
};

// Mở kết nối SSE để nhận kết quả dịch realtime
export const openSSEStream = (clientId, onMessage, onError) => {
  const token = sessionStorage.getItem("access_token_user");
  const url = `${API_URL}/stream/${clientId}?token=${token}`;

  const eventSource = new EventSource(url);

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {
      onMessage(event.data);
    }
  };

  eventSource.onerror = (err) => {
    if (onError) onError(err);
    eventSource.close();
  };

  return eventSource;
};
