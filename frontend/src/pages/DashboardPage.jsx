import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import Loader from "../components/Loader";
import ErrorMessage from "../components/ErrorMessage";
import EmptyState from "../components/EmptyState";
import StatusBadge from "../components/StatusBadge";
import { formatDate, formatDateTime } from "../utils";
import { useAuth } from "../auth";

export default function DashboardPage() {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const data = await api.getApplications();
      setItems(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <Loader text="Загружаем заявки..." />;
  if (error) return <ErrorMessage message={error} />;

  if (!items.length) {
    return (
      <EmptyState
        title="Заявок пока нет"
        description="Создайте первую заявку, чтобы отправить её на конкурс и получить предварительную AI-проверку."
        action={
          <Link className="btn btn-primary" to="/applications/new">
            Создать заявку
          </Link>
        }
      />
    );
  }

  return (
    <section className="stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Рабочая панель</p>
          <h1>{user?.role === "admin" ? "Все заявки" : "Мои заявки"}</h1>
        </div>
        <Link className="btn btn-primary" to="/applications/new">
          Новая заявка
        </Link>
      </div>

      <div className="card table-card">
        <table className="table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Конкурс</th>
              <th>Статус</th>
              <th>Дата отправки</th>
              <th>Создана</th>
            </tr>
          </thead>
          <tbody>
            {items.map((app) => (
              <tr key={app.id}>
                <td>
                  <Link className="table-link" to={`/applications/${app.id}`}>
                    {app.title}
                  </Link>
                </td>
                <td>
                  <div>{app.competition?.title}</div>
                  <div className="table-subtext">Дедлайн: {formatDate(app.competition?.deadline)}</div>
                </td>
                <td>
                  <StatusBadge status={app.status} />
                </td>
                <td>{formatDateTime(app.submitted_at)}</td>
                <td>{formatDateTime(app.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}