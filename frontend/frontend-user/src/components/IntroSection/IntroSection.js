import React from "react";
import "./IntroSection.scss";

function IntroSection({ title, cards, variant = "first" }) {
  return (
    <div className={`intro__${variant}`}>
      <h2 className="intro__title">{title}</h2>
      <div className="intro__grid">
        {cards.map(({ id, img, text, subtext }) => (
          <div className="intro__card" key={id}>
            <img src={img} alt={text} className="intro__img" />
            <p className="intro__text">{text}</p>
            {subtext && <p className="intro__subtext">{subtext}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}

export default IntroSection;
