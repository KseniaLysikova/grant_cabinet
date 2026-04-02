import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import ErrorMessage from "../components/ErrorMessage";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    role: "applicant"
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await register(form);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <p className="eyebrow">Регистрация</p>
        <h1>Создать аккаунт</h1>
        <p className="muted">После регистрации можно создавать и отслеживать грантовые заявки.</p>

        <form className="form" onSubmit={handleSubmit}>
          <label>
            ФИО
            <input name="full_name" value={form.full_name} onChange={handleChange} required />
          </label>

          <label>
            Email
            <input name="email" type="email" value={form.email} onChange={handleChange} required />
          </label>

          <label>
            Пароль
            <input name="password" type="password" value={form.password} onChange={handleChange} required />
          </label>

          <label>
            Роль
            <select name="role" value={form.role} onChange={handleChange}>
              <option value="applicant">Заявитель</option>
              <option value="admin">Администратор</option>
            </select>
          </label>

          <ErrorMessage message={error} />

          <button className="btn btn-primary" disabled={loading}>
            {loading ? "Создаём..." : "Создать аккаунт"}
          </button>
        </form>

        <p className="auth-footer">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  );
}