import React, { useState, useEffect } from "react";
import useFeedback from "../../hooks/useFeedback";
import { FeedbackModal } from "./FeedbackModal";
import { FeedbackCard } from "./FeedbackCard";
import "./FeedbackPage.scss";

function FeedbackPage() {
  const {
    feedbacks,
    loading,
    error,
    success,
    fetchMyFeedbacks,
    fetchFeedbackDetail,
    editFeedback,
    removeFeedback,
    clearMessages,
  } = useFeedback();

  const [showModal, setShowModal] = useState(false);
  const [editTarget, setEditTarget] = useState(null);

  useEffect(() => {
    fetchMyFeedbacks();
  }, [fetchMyFeedbacks]);

  const handleOpenEdit = (freshFeedback) => {
    clearMessages();
    setEditTarget(freshFeedback);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditTarget(null);
  };

  const handleSubmit = async (payload) => {
    const res = await editFeedback(editTarget.id, payload);
    if (res?.success) {
      handleCloseModal();
      fetchMyFeedbacks();
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Bạn có chắc muốn xóa đánh giá này?")) return;
    const res = await removeFeedback(id);
    if (res?.success) fetchMyFeedbacks();
  };

  const avgRating =
    feedbacks.length > 0
      ? (
          feedbacks.reduce((sum, f) => sum + f.rating, 0) / feedbacks.length
        ).toFixed(1)
      : null;

  return (
    <div className="profile-page__card feedback-tab">
      <div className="feedback-tab__header">
        <h2
          className="profile-page__card-title"
          style={{ border: "none", padding: 0 }}
        >
          Đánh giá của tôi
        </h2>
        {avgRating && (
          <div className="feedback-tab__avg">
            <i className="bx bxs-star"></i>
            <span>{avgRating}</span>
            <em>({feedbacks.length} đánh giá)</em>
          </div>
        )}
      </div>

      {error && (
        <div className="profile-page__alert profile-page__alert--error">
          <i className="bx bx-error-circle"></i> {error}
        </div>
      )}
      {success && (
        <div className="profile-page__alert profile-page__alert--success">
          <i className="bx bx-check-circle"></i> {success}
        </div>
      )}

      {loading && feedbacks.length === 0 ? (
        <div className="feedback-tab__empty">
          <div className="spinner spinner--lg" />
          <p>Đang tải đánh giá...</p>
        </div>
      ) : feedbacks.length === 0 ? (
        <div className="feedback-tab__empty">
          <i className="bx bx-comment-x feedback-tab__empty-icon"></i>
          <p>Bạn chưa có đánh giá nào.</p>
          <p className="feedback-tab__empty-hint">
            Hãy dịch một đoạn văn bản và để lại đánh giá nhé!
          </p>
        </div>
      ) : (
        <div className="feedback-grid">
          {feedbacks.map((fb) => (
            <FeedbackCard
              key={fb.id}
              feedback={fb}
              onEdit={handleOpenEdit}
              onDelete={handleDelete}
              onFetchDetail={fetchFeedbackDetail}
            />
          ))}
        </div>
      )}

      {showModal && (
        <FeedbackModal
          feedback={editTarget}
          onClose={handleCloseModal}
          onSubmit={handleSubmit}
          loading={loading}
        />
      )}
    </div>
  );
}

export default FeedbackPage;
