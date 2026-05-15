import React from "react";

export default function Stars({ value, max = 5 }) {
  return (
    <span className="stars">
      {Array.from({ length: max }, (_, i) => {
        const filled = i < Math.floor(value);
        const half = !filled && i < value && value - Math.floor(value) >= 0.5;
        return (
          <i
            key={i}
            className={
              filled ? "bx bxs-star" : half ? "bx bxs-star-half" : "bx bx-star"
            }
            style={{
              color: filled || half ? "#e8d317" : "var(--border2, #ddd)",
              fontSize: 14,
            }}
          />
        );
      })}
    </span>
  );
}
