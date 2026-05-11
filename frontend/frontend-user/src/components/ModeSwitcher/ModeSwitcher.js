import React from "react";
import "./ModeSwitcher.scss";

function ModeSwitcher({ modes, active, onChange }) {
  return (
    <div className="mode-switcher">
      {modes.map(({ id, label }) => (
        <button
          key={id}
          className={`mode-switcher__btn${
            active === id ? " mode-switcher__btn--active" : ""
          }`}
          onClick={() => onChange(id)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

export default ModeSwitcher;
