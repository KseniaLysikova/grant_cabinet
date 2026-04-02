import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import ErrorMessage from "../components/ErrorMessage";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/dashboard";

  const [form, setForm] = useState({
    email: "",
    password: ""
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
      await login(form.email, form.password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <p className="eyebrow">Грантовый кабинет</p>
        <h1>Вход в систему</h1>
        <p className="muted">
          Авторизация заявителя и администратора для работы с заявками и результатами ExpertAI.
        </p>

        <form className="form" onSubmit={handleSubmit}>
          <label>
            Email
            <input name="email" type="email" value={form.email} onChange={handleChange} required />
          </label>

          <label>
            Пароль
            <input name="password" type="password" value={form.password} onChange={handleChange} required />
          </label>

          <ErrorMessage message={error} />

          <button className="btn btn-primary" disabled={loading}>
            {loading ? "Входим..." : "Войти"}
          </button>
        </form>

        <div className="demo-box">
          <p><strong>Тестовые аккаунты:</strong></p>
          <p>admin@example.com / admin123</p>
          <p>applicant@example.com / applicant123</p>
        </div>

        <p className="auth-footer">
          Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
        </p>
      </div>
    </div>
  );
}