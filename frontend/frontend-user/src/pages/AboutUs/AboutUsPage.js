import React from "react";
import ContactForm from "../../components/ContactForm/ContactForm";
import { useContactForm } from "../../hooks/useContactForm";
import "./AboutUsPage.scss";

function AboutUsPage() {
  const { form, loading, success, error, handleChange, handleSubmit } =
    useContactForm();

  return (
    <section className="about">
      <div className="about__inner">
        <div className="about__content">
          <h2 className="about__title">About</h2>
          <p className="about__subheading">
            Subheading for description or instructions
          </p>
          <p className="about__body">
            Body text for your whole article or post. We'll put in some lorem
            ipsum to show how a filled-out page might look:
          </p>
          <p className="about__body">
            Excepteur efficient emerging, minim veniam anim aute carefully
            curated Ginza conversation exquisite perfect nostrud nisi intricate
            Content. Qui international first-class nulla ut.
          </p>

          <ContactForm
            form={form}
            onChange={handleChange}
            onSubmit={handleSubmit}
            loading={loading}
            success={success}
            error={error}
          />
        </div>

        <div className="about__image">
          <img
            src="https://picsum.photos/400/500"
            alt="About us"
            className="about__img"
          />
        </div>
      </div>
    </section>
  );
}

export default AboutUsPage;
