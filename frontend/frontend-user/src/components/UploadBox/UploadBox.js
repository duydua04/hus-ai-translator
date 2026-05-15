import React, { useRef, useState } from "react";
import axiosUser from "../../api/axiosUser";
import "./UploadBox.scss";

const UPLOAD_TYPES = [
  {
    id: "pdf",
    icon: "bx bxs-file-pdf",
    label: "Tài liệu PDF",
    ext: ".pdf",
    accept: ".pdf,application/pdf",
  },
];

// Detect file type from result_path extension
function getFileType(path = "") {
  const ext = path.split(".").pop().toLowerCase();
  if (ext === "pdf") return "pdf";
  if (["jpg", "jpeg", "png", "webp", "gif"].includes(ext)) return "image";
  return "other";
}

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
  feedbackDone,
}) {
  const inputRef = useRef(null);
  const [actionError, setActionError] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  const showActionError = (msg) => {
    setActionError(msg);
    setTimeout(() => setActionError(null), 3000);
  };

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

  const getPresignedUrl = async () => {
    if (!result?.result_path) return null;
    try {
      const response = await axiosUser.get(
        `/api/files/presigned-url?path=${encodeURIComponent(
          result.result_path
        )}`
      );
      if (response.data?.success && response.data?.data?.url) {
        return response.data.data.url;
      }
      showActionError("Không thể lấy link tải xuống.");
      return null;
    } catch (err) {
      console.error(err);
      showActionError("Đã xảy ra lỗi khi tải file.");
      return null;
    }
  };

  const handleDownload = async () => {
    const url = await getPresignedUrl();
    if (!url) return;
    const link = document.createElement("a");
    link.href = url;
    link.download = result?.result_path?.split("/").pop() || "ban-dich";
    link.rel = "noreferrer";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePreview = async () => {
    const fileType = getFileType(result?.result_path || "");

    if (fileType === "other") {
      showActionError(
        "Định dạng Word không hỗ trợ xem trước. Vui lòng tải xuống để xem."
      );
      return;
    }

    // Open blank window BEFORE async work so browser doesn't block the popup
    const newWindow = window.open("", "_blank");
    if (!newWindow) {
      showActionError(
        "Trình duyệt đã chặn cửa sổ mới. Vui lòng cho phép popup và thử lại."
      );
      return;
    }
    newWindow.document.write(
      "<p style='font-family:sans-serif;padding:20px'>Đang tải...</p>"
    );

    setPreviewLoading(true);
    try {
      const presignedUrl = await getPresignedUrl();
      if (!presignedUrl) {
        newWindow.close();
        return;
      }

      // Fetch as blob to bypass Content-Disposition: attachment from server
      const res = await fetch(presignedUrl);
      if (!res.ok) throw new Error("Fetch failed");
      const blob = await res.blob();

      const mimeType = fileType === "pdf" ? "application/pdf" : blob.type;
      const typedBlob = new Blob([blob], { type: mimeType });
      const blobUrl = URL.createObjectURL(typedBlob);

      newWindow.location.href = blobUrl;

      // Revoke blob URL after a delay to free memory
      setTimeout(() => URL.revokeObjectURL(blobUrl), 30000);
    } catch (err) {
      console.error(err);
      newWindow.close();
      showActionError("Không thể tải file để xem trước.");
    } finally {
      setPreviewLoading(false);
    }
  };

  const renderNote = () => {
    if (actionError) {
      return (
        <span className="upload__error">
          <i className="bx bx-error-circle"></i> {actionError}
        </span>
      );
    }

    if (error) {
      return (
        <span className="upload__error">
          <i className="bx bx-error-circle"></i> {error}
        </span>
      );
    }

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

    if (isFailed) {
      return (
        <span className="upload__error">
          <i className="bx bx-error-circle"></i>{" "}
          {sseMessage || "Dịch tài liệu thất bại. Vui lòng thử lại."}
        </span>
      );
    }

    if (isCompleted && result?.result_path) {
      const fileType = getFileType(result.result_path);
      const canPreview = fileType !== "other";

      return (
        <div className="upload__result">
          <i className="bx bx-check-circle upload__result-icon"></i>
          <span>{success || "Dịch tài liệu thành công!"}</span>
          <div className="upload__result-actions">
            <button
              className="upload__action-btn upload__action-btn--preview"
              onClick={handlePreview}
              disabled={previewLoading || !canPreview}
              title={
                canPreview
                  ? "Xem trước bản dịch"
                  : "Định dạng Word không hỗ trợ xem trước, vui lòng tải xuống"
              }
            >
              {previewLoading ? (
                <i className="bx bx-loader-alt bx-spin"></i>
              ) : (
                <i className="bx bx-show"></i>
              )}{" "}
              Xem trước
            </button>
            <button
              className="upload__action-btn upload__action-btn--download"
              onClick={handleDownload}
              title="Tải xuống bản dịch"
            >
              <i className="bx bx-download"></i> Tải xuống
            </button>
          </div>
        </div>
      );
    }

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
