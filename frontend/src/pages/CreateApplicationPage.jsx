import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import Loader from "../components/Loader";
import ErrorMessage from "../components/ErrorMessage";

export default function CreateApplicationPage() {
  const navigate = useNavigate();
  const [competitions, setCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    title: "",
    description: "",
    project_goal: "",
    requested_amount: "",
    competition_id: ""
  });

  useEffect(() => {
    async function loadCompetitions() {
      try {
        const data = await api.getCompetitions();
        setCompetitions(data);
        if (data.length > 0) {
          setForm((prev) => ({ ...prev, competition_id: String(data[0].id) }));
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadCompetitions();
  }, []);

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError("");

    try {
      const created = await api.createApplication({
        title: form.title,
        description: form.description,
        project_goal: form.project_goal,
        requested_amount: form.requested_amount ? Number(form.requested_amount) : null,
        competition_id: Number(form.competition_id)
      });

      navigate(`/applications/${created.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Loader text="Загружаем конкурсы..." />;

  return (
    <section className="stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Новая заявка</p>
          <h1>Регистрация заявки на грант</h1>
        </div>
      </div>

      <div className="card form-card">
        <form className="form" onSubmit={handleSubmit}>
          <label>
            Название проекта
            <input name="title" value={form.title} onChange={handleChange} required />
          </label>

          <label>
            Конкурс
            <select name="competition_id" value={form.competition_id} onChange={handleChange} required>
              {competitions.map((competition) => (
                <option key={competition.id} value={competition.id}>
                  {competition.title}
                </option>
              ))}
            </select>
          </label>

          <label>
            Описание заявки
            <textarea
              name="description"
              rows="6"
              value={form.description}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Цель проекта
            <textarea
              name="project_goal"
              rows="4"
              value={form.project_goal}
              onChange={handleChange}
            />
          </label>

          <label>
            Запрашиваемая сумма
            <input
              name="requested_amount"
              type="number"
              min="0"
              value={form.requested_amount}
              onChange={handleChange}
            />
          </label>

          <ErrorMessage message={error} />

          <button className="btn btn-primary" disabled={saving}>
            {saving ? "Создаём заявку..." : "Создать заявку"}
          </button>
        </form>
      </div>
    </section>
  );
}