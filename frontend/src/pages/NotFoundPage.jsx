import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <p className="eyebrow">404</p>
        <h1>Страница не найдена</h1>
        <p className="muted">Указанный маршрут отсутствует в клиентской маршрутизации.</p>
        <Link className="btn btn-primary" to="/dashboard">
          На главную
        </Link>
      </div>
    </div>
  );
}