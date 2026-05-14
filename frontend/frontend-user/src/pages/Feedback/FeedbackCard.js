import React from "react";
import { StarRating } from "./FeedbackModal";

export function FeedbackCard({ feedback, onEdit, onDelete, onFetchDetail }) {
  const handleEdit = async () => {
    const res = await onFetchDetail(feedback.id);
    if (res?.success && res?.data) {
      onEdit(res.data);
    } else {
      onEdit(feedback);
    }
  };

  return (
    <div className="feedback-card">
      <div className="feedback-card__header">
        <StarRating value={feedback.rating} readonly />
        <span className="feedback-card__date">
          {new Date(feedback.created_at).toLocaleDateString("vi-VN")}
        </span>
      </div>

      <p className="feedback-card__comment">
        {feedback.feedback_note || <em>Không có nhận xét</em>}
      </p>

      {feedback.corrected_content && (
        <div className="feedback-card__correction">
          <span className="feedback-card__correction-label">
            <i className="bx bx-edit-alt"></i> Đề xuất sửa:
          </span>
          <p>{feedback.corrected_content}</p>
        </div>
      )}

      <div className="feedback-card__meta">
        <span className="feedback-card__translation">
          <i className="bx bx-file"></i> Bản dịch #
          {String(feedback.translation_id).slice(0, 8)}
        </span>
        <div className="feedback-card__actions">
          <button
            className="btn-icon btn-edit"
            onClick={handleEdit}
            title="Sửa"
          >
            <i className="bx bx-edit"></i>
          </button>
          <button
            className="btn-icon btn-delete"
            onClick={() => onDelete(feedback.id)}
            title="Xóa"
          >
            <i className="bx bx-trash"></i>
          </button>
        </div>
      </div>
    </div>
  );
}
