import React from "react";
import Stars from "./Stars";

export default function FeedbackCard({ feedbacks }) {
  return (
    <div className="chart-card">
      <div className="chart-card__header">
        <div className="chart-card__title">Feedback gần đây</div>
      </div>
      <div className="feedback-list">
        {(feedbacks ?? []).map((fb) => (
          <div className="feedback-item" key={fb.id}>
            <div className="feedback-item__bar" />
            <div className="feedback-item__body">
              <Stars value={fb.rating} />
              {fb.feedback_note && (
                <div className="feedback-item__text">"{fb.feedback_note}"</div>
              )}
              <div className="feedback-item__meta">
                {fb.user_name} · {fb.direction} · {fb.time_ago}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
