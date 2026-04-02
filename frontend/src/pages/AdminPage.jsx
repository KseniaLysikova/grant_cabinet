import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import Loader from "../components/Loader";
import ErrorMessage from "../components/ErrorMessage";
import StatusBadge from "../components/StatusBadge";
import { formatDateTime } from "../utils";

export default function AdminPage() {
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

  if (loading) return <Loader text="Загружаем административную панель..." />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <section className="stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Администрирование</p>
          <h1>Панель обработки заявок</h1>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Всего заявок</span>
          <strong>{items.length}</strong>
        </div>
        <div className="stat-card">
          <span>На рассмотрении</span>
          <strong>{items.filter((item) => item.status === "in_review").length}</strong>
        </div>
        <div className="stat-card">
          <span>Одобрено</span>
          <strong>{items.filter((item) => item.status === "approved").length}</strong>
        </div>
        <div className="stat-card">
          <span>Отклонено</span>
          <strong>{items.filter((item) => item.status === "rejected").length}</strong>
        </div>
      </div>

      <div className="card table-card">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Заявка</th>
              <th>Статус</th>
              <th>Создана</th>
            </tr>
          </thead>
          <tbody>
            {items.map((app) => (
              <tr key={app.id}>
                <td>{app.id}</td>
                <td>
                  <Link className="table-link" to={`/applications/${app.id}`}>
                    {app.title}
                  </Link>
                </td>
                <td>
                  <StatusBadge status={app.status} />
                </td>
                <td>{formatDateTime(app.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}