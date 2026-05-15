import React, { useState } from "react";

const STAR_COUNT = 5;

export function StarRating({ value, onChange, readonly = false }) {
  const [hovered, setHovered] = useState(0);

  return (
    <div className="star-rating">
      {Array.from({ length: STAR_COUNT }, (_, i) => i + 1).map((star) => (
        <button
          key={star}
          type="button"
          className={`star ${star <= (hovered || value) ? "filled" : ""}`}
          onClick={() => !readonly && onChange?.(star)}
          onMouseEnter={() => !readonly && setHovered(star)}
          onMouseLeave={() => !readonly && setHovered(0)}
          disabled={readonly}
          aria-label={`${star} sao`}
        >
          <i
            className={`bx ${
              star <= (hovered || value) ? "bxs-star" : "bx-star"
            }`}
          ></i>
        </button>
      ))}
    </div>
  );
}

export function FeedbackModal({ feedback, onClose, onSubmit, loading }) {
  const isEdit = !!feedback;
  const [rating, setRating] = useState(feedback?.rating || 0);
  const [feedbackNote, setFeedbackNote] = useState(
    feedback?.feedback_note || ""
  );
  const [correctedContent, setCorrectedContent] = useState(
    feedback?.corrected_content || ""
  );
  const [showCorrection, setShowCorrection] = useState(
    !!feedback?.corrected_content
  );

  const handleSubmit = () => {
    if (!rating) return alert("Vui lòng chọn số sao!");
    onSubmit({
      rating,
      feedback_note: feedbackNote,
      corrected_content: correctedContent || undefined,
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal__header">
          <h3>{isEdit ? "Chỉnh sửa đánh giá" : "Đánh giá bản dịch"}</h3>
          <button className="modal__close" onClick={onClose} disabled={loading}>
            <i className="bx bx-x"></i>
          </button>
        </div>

        <div className="modal__body">
          <label
            className="profile-page__label"
            style={{ marginBottom: "8px", display: "block" }}
          >
            Đánh giá của bạn <span style={{ color: "#b53c3c" }}>*</span>
          </label>
          <StarRating value={rating} onChange={setRating} />

          <label
            className="profile-page__label"
            style={{ marginTop: "20px", marginBottom: "8px", display: "block" }}
          >
            Nhận xét
          </label>
          <textarea
            className="profile-page__input"
            style={{ resize: "vertical", minHeight: "80px", lineHeight: "1.5" }}
            placeholder="Nhập nhận xét về bản dịch (tuỳ chọn)..."
            value={feedbackNote}
            onChange={(e) => setFeedbackNote(e.target.value)}
            rows={3}
          />

          <button
            type="button"
            className="btn-toggle-correction"
            onClick={() => setShowCorrection((v) => !v)}
            style={{ marginTop: "16px" }}
          >
            <i className={`bx ${showCorrection ? "bx-minus" : "bx-plus"}`}></i>
            {showCorrection ? " Ẩn đề xuất sửa" : " Thêm đề xuất sửa bản dịch"}
          </button>

          {showCorrection && (
            <>
              <label
                className="profile-page__label"
                style={{
                  marginTop: "16px",
                  marginBottom: "8px",
                  display: "block",
                }}
              >
                Nội dung đề xuất sửa
              </label>
              <textarea
                className="profile-page__input"
                style={{
                  resize: "vertical",
                  minHeight: "100px",
                  lineHeight: "1.5",
                }}
                placeholder="Nhập nội dung bản dịch đúng hơn theo ý bạn..."
                value={correctedContent}
                onChange={(e) => setCorrectedContent(e.target.value)}
                rows={4}
              />
            </>
          )}
        </div>

        <div className="modal__footer">
          <button
            className="profile-page__btn profile-page__btn--ghost"
            onClick={onClose}
            disabled={loading}
          >
            Huỷ
          </button>
          <button
            className="profile-page__btn profile-page__btn--primary"
            onClick={handleSubmit}
            disabled={loading}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              minWidth: "120px",
            }}
          >
            {loading ? (
              <span
                className="spinner spinner--sm"
                style={{ borderTopColor: "#fff" }}
              />
            ) : isEdit ? (
              "Cập nhật"
            ) : (
              "Gửi đánh giá"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
