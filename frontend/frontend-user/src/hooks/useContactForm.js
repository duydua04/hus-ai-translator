import { useState, useCallback } from "react";
import { submitContact } from "../api/translationApi";

const INITIAL = { firstName: "", lastName: "", email: "", message: "" };

export function useContactForm() {
  const [form, setForm] = useState(INITIAL);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }, []);

  const handleSubmit = useCallback(async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await submitContact(form);
      setSuccess(true);
      setForm(INITIAL);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [form]);

  return { form, loading, success, error, handleChange, handleSubmit };
}
