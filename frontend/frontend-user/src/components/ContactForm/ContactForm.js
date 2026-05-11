import React from "react";
import "./ContactForm.scss";

function ContactForm({ form, onChange, onSubmit, loading, success, error }) {
  return (
    <div className="contact">
      <h3 className="contact__title">Contact me</h3>

      {success && (
        <p className="contact__success">
          Gửi thành công! Chúng tôi sẽ liên hệ sớm.
        </p>
      )}
      {error && <p className="contact__error">{error}</p>}

      <div className="contact__row">
        <div className="contact__field">
          <label className="contact__label">First name</label>
          <input
            type="text"
            name="firstName"
            placeholder="Jane"
            className="contact__input"
            value={form.firstName}
            onChange={onChange}
          />
        </div>
        <div className="contact__field">
          <label className="contact__label">Last name</label>
          <input
            type="text"
            name="lastName"
            placeholder="Smitherton"
            className="contact__input"
            value={form.lastName}
            onChange={onChange}
          />
        </div>
      </div>

      <div className="contact__field">
        <label className="contact__label">Email address</label>
        <input
          type="email"
          name="email"
          placeholder="email@domain.com"
          className="contact__input"
          value={form.email}
          onChange={onChange}
        />
      </div>

      <div className="contact__field">
        <label className="contact__label">Your message</label>
        <textarea
          name="message"
          placeholder="Enter your question or message"
          className="contact__textarea"
          value={form.message}
          onChange={onChange}
        ></textarea>
      </div>

      <button
        className="btn btn--primary contact__submit"
        onClick={onSubmit}
        disabled={loading}
      >
        {loading ? "Đang gửi..." : "Submit"}
      </button>
    </div>
  );
}

export default ContactForm;
