import React from "react";
import { useNavigate } from "react-router-dom";
import "./NotFound.scss";

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="nf-page">
      <div className="nf-bg-grid" />
      <div className="nf-spotlight" />
      <div className="nf-scanline" />
      <span className="nf-dot nf-dot--1" />
      <span className="nf-dot nf-dot--2" />
      <span className="nf-dot nf-dot--3" />
      <span className="nf-dot nf-dot--4" />

      <div className="nf-ghost">
        <svg width="72" height="72" viewBox="0 0 72 72" fill="none">
          <ellipse
            cx="36"
            cy="34"
            rx="22"
            ry="24"
            fill="#163d1a"
            stroke="#4a9e55"
            strokeWidth="1.5"
          />
          <path
            d="M14 34 Q14 58 22 54 Q28 50 36 54 Q44 50 50 54 Q58 58 58 34"
            fill="#163d1a"
            stroke="#4a9e55"
            strokeWidth="1.5"
          />
          <circle cx="28" cy="30" r="4" fill="#6bbd77" />
          <circle cx="44" cy="30" r="4" fill="#6bbd77" />
          <circle cx="29" cy="30" r="2" fill="#0d2d12" />
          <circle cx="45" cy="30" r="2" fill="#0d2d12" />
          <circle cx="30" cy="29" r="1" fill="#9ed8a8" />
          <circle cx="46" cy="29" r="1" fill="#9ed8a8" />
          <path
            d="M30 38 Q36 43 42 38"
            stroke="#4a9e55"
            strokeWidth="1.5"
            fill="none"
            strokeLinecap="round"
          />
          <ellipse
            cx="36"
            cy="16"
            rx="6"
            ry="4"
            fill="#1e5224"
            stroke="#4a9e55"
            strokeWidth="1"
          />
          <line
            x1="36"
            y1="12"
            x2="36"
            y2="6"
            stroke="#4a9e55"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
          <circle cx="36" cy="5" r="2" fill="#6bbd77" />
        </svg>
      </div>

      <h1 className="nf-number">404</h1>

      <div className="nf-msg">
        <h2>OOPS!!!</h2>
        <p>Có vẻ như trang bạn đang tìm đã bị xóa hoặc chưa bao giờ tồn tại.</p>
      </div>

      <div className="nf-actions">
        <button
          className="nf-btn nf-btn--primary"
          onClick={() => navigate("/")}
        >
          <i className="bx bx-home-alt" />
          Về trang chủ
        </button>
        <button className="nf-btn nf-btn--ghost" onClick={() => navigate(-1)}>
          <i className="bx bx-chevron-left" />
          Quay lại
        </button>
      </div>
    </div>
  );
}
