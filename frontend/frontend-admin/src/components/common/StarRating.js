import React from "react";

export default function StarRating({ value, max = 5 }) {
  return (
    <div className="star-rating">
      {Array.from({ length: max }, (_, i) => (
        <span
          key={i}
          className={`star-rating__star${
            i >= value ? " star-rating__star--off" : ""
          }`}
        >
          ★
        </span>
      ))}
    </div>
  );
}
