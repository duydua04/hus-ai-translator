import React from "react";
import "./Pagination.scss";

export default function Pagination({ current, total, limit, onChange }) {
  const totalPages = Math.ceil(total / limit);

  const getPages = () => {
    if (totalPages <= 5)
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    if (current <= 3) return [1, 2, 3, "…", totalPages];
    if (current >= totalPages - 2)
      return [1, "…", totalPages - 2, totalPages - 1, totalPages];
    return [1, "…", current - 1, current, current + 1, "…", totalPages];
  };

  return (
    <div className="pagination">
      <span className="pagination__info">
        Hiển thị {(current - 1) * limit + 1}–{Math.min(current * limit, total)}{" "}
        / {total.toLocaleString()} mục
      </span>
      <button
        className="pagination__btn"
        onClick={() => onChange(current - 1)}
        disabled={current === 1}
      >
        ‹
      </button>
      {getPages().map((p, i) => (
        <button
          key={i}
          className={`pagination__btn${
            p === current ? " pagination__btn--active" : ""
          }`}
          onClick={() => typeof p === "number" && onChange(p)}
          disabled={p === "…"}
        >
          {p}
        </button>
      ))}
      <button
        className="pagination__btn"
        onClick={() => onChange(current + 1)}
        disabled={current === totalPages}
      >
        ›
      </button>
    </div>
  );
}
