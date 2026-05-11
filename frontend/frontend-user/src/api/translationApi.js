// Base URL — đổi thành URL backend thực tế
const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000/api";

/**
 * Dịch văn bản thuần
 * @param {string} text      - Văn bản cần dịch
 * @param {string} sourceLang - Ngôn ngữ nguồn, vd: "en"
 * @param {string} targetLang - Ngôn ngữ đích,  vd: "vi"
 * @returns {Promise<{ translatedText: string }>}
 */
export async function translateText(text, sourceLang, targetLang) {
  const response = await fetch(`${API_BASE_URL}/translate/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, sourceLang, targetLang }),
  });
  if (!response.ok) throw new Error("Lỗi khi dịch văn bản");
  return response.json();
}

/**
 * Dịch tệp đính kèm
 * @param {File}   file       - File cần dịch
 * @param {string} sourceLang
 * @param {string} targetLang
 * @returns {Promise<{ translatedText: string, downloadUrl?: string }>}
 */
export async function translateFile(file, sourceLang, targetLang) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("sourceLang", sourceLang);
  formData.append("targetLang", targetLang);

  const response = await fetch(`${API_BASE_URL}/translate/file`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) throw new Error("Lỗi khi dịch tệp");
  return response.json();
}

/**
 * Gửi form liên hệ
 * @param {{ firstName, lastName, email, message }} data
 * @returns {Promise<{ success: boolean }>}
 */
export async function submitContact(data) {
  const response = await fetch(`${API_BASE_URL}/contact`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Lỗi khi gửi liên hệ");
  return response.json();
}
