import React, { useRef } from "react";
import "./UploadBox.scss";

const UPLOAD_TYPES = [
  {
    id: "docx",
    icon: "bx bx-file",
    label: "Tài liệu Word",
    ext: ".docx",
    accept:
      ".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  },
  {
    id: "pdf",
    icon: "bx bxs-file-pdf",
    label: "Tài liệu PDF",
    ext: ".pdf",
    accept: ".pdf,application/pdf",
  },
  {
    id: "image",
    icon: "bx bx-image",
    label: "Hình ảnh",
    ext: ".jpg, .png, .webp",
    accept: ".jpg,.jpeg,.png,.webp,image/*",
  },
];

/**
 * result shape từ SSE (translateDocument):
 *   { status: "processing"|"completed"|"failed", progress: 0-100, message, translation_id, result_path }
 * result shape từ translateText (không dùng ở đây):
 *   { translation_id, original_text, translated_text, source_lang_code, target_lang_code, status }
 */
function UploadBox({
  onFileSelect,
  selectedFile,
  result,
  loading,
  error,
  success,
  sseStatus,
  sseProgress = 0,
  sseMessage,
}) {
  const inputRef = useRef(null);

  const handleItemClick = (accept) => {
    if (inputRef.current) {
      inputRef.current.accept = accept;
      inputRef.current.value = "";
      inputRef.current.click();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  const isCompleted = sseStatus === "completed";
  const isFailed = sseStatus === "failed";
  const isProcessing = loading || sseStatus === "processing";

  const renderNote = () => {
    // Lỗi hook (validate phía FE hoặc lỗi API)
    if (error) {
      return (
        <span className="upload__error">
          <i className="bx bx-error-circle"></i> {error}
        </span>
      );
    }

    // Đang xử lý — hiển thị progress bar + message từ SSE
    if (isProcessing) {
      return (
        <div className="upload__progress">
          <div className="upload__progress-bar">
            <div
              className="upload__progress-fill"
              style={{ width: `${sseProgress}%` }}
            />
          </div>
          <span className="upload__progress-text">
            {sseMessage || "Đang xử lý tệp..."}{" "}
            {sseProgress > 0 && `(${sseProgress}%)`}
          </span>
        </div>
      );
    }

    // SSE báo thất bại
    if (isFailed) {
      return (
        <span className="upload__error">
          <i className="bx bx-error-circle"></i>{" "}
          {sseMessage || "Dịch tài liệu thất bại. Vui lòng thử lại."}
        </span>
      );
    }

    // SSE báo hoàn thành — result_path là đường dẫn file kết quả
    if (isCompleted && result?.result_path) {
      return (
        <div className="upload__result">
          <i className="bx bx-check-circle upload__result-icon"></i>
          <span>{success || "Dịch tài liệu thành công!"}</span>
          <a
            className="upload__download-btn"
            href={result.result_path}
            download
            target="_blank"
            rel="noreferrer"
          >
            <i className="bx bx-download"></i> Tải xuống bản dịch
          </a>
        </div>
      );
    }

    // Đã chọn file, chưa dịch
    if (selectedFile) {
      return (
        <div className="upload__selected">
          <div className="upload__selected-main">
            <i className="bx bxs-file-blank upload__selected-icon"></i>
            <span className="upload__selected-name" title={selectedFile.name}>
              {selectedFile.name}
            </span>
          </div>
          <span className="upload__selected-size">
            {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
          </span>
        </div>
      );
    }

    // Trạng thái mặc định
    return <span>Bản dịch sẽ xuất hiện ở đây sau khi xử lý...</span>;
  };

  return (
    <div className="translator__content translator__content--file">
      <input
        ref={inputRef}
        type="file"
        style={{ display: "none" }}
        onChange={handleFileChange}
      />

      <div className="upload__box">
        {UPLOAD_TYPES.map(({ id, icon, label, ext, accept }) => (
          <div
            key={id}
            className={`upload__item ${
              isProcessing ? "upload__item--disabled" : ""
            }`}
            onClick={() => !isProcessing && handleItemClick(accept)}
          >
            <i className={icon}></i>
            <p>{label}</p>
            <small>{ext}</small>
          </div>
        ))}
      </div>

      <div className="upload__note">{renderNote()}</div>
    </div>
  );
}

export default UploadBox;
