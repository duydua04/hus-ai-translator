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

function UploadBox({ onFileSelect, selectedFile, result, loading, error }) {
  const inputRef = useRef(null);

  const handleItemClick = (accept) => {
    if (inputRef.current) {
      inputRef.current.accept = accept;
      inputRef.current.value = ""; // reset để có thể chọn lại cùng file
      inputRef.current.click();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  return (
    <div className="translator__content translator__content--file">
      {/* Input ẩn, dùng chung cho cả 3 loại */}
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
            className="upload__item"
            onClick={() => handleItemClick(accept)}
          >
            <i className={icon}></i>
            <p>{label}</p>
            <small>{ext}</small>
          </div>
        ))}
      </div>

      <div className="upload__note">
        {loading && "Đang xử lý tệp..."}
        {error && <span className="upload__error">{error}</span>}
        {!loading && !error && selectedFile && (
          <span>
            Đã chọn: <strong>{selectedFile.name}</strong>
          </span>
        )}
        {!loading && !error && result?.translatedText && (
          <span>{result.translatedText}</span>
        )}
        {!loading &&
          !error &&
          !selectedFile &&
          !result &&
          "Bản dịch sẽ xuất hiện ở đây sau khi xử lý..."}
      </div>
    </div>
  );
}

export default UploadBox;
