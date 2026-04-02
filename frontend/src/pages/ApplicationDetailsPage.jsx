import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";
import Loader from "../components/Loader";
import ErrorMessage from "../components/ErrorMessage";
import StatusBadge from "../components/StatusBadge";
import { formatDate, formatDateTime } from "../utils";
import { useAuth } from "../auth";

export default function ApplicationDetailsPage() {
  const { id } = useParams();
  const { user } = useAuth();

  const [application, setApplication] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [statusLoading, setStatusLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadApplication() {
    setLoading(true);
    setError("");

    try {
      const data = await api.getApplication(id);
      setApplication(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadApplication();
  }, [id]);

  async function handleUpload(e) {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setError("");
    setSuccess("");

    try {
      await api.uploadFile(id, selectedFile);
      setSuccess("Файл успешно загружен");
      setSelectedFile(null);
      await loadApplication();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleDownload(file) {
    try {
      const token = localStorage.getItem("token"); // или откуда берёшь токен
      if (!token) {
        setError("Необходимо войти в систему");
        return;
      }
  
      const downloadUrl = `/applications/${application.id}/files/${file.id}/download`;
      const fullUrl = `http://127.0.0.1:8000${downloadUrl}`;
  
      const response = await fetch(fullUrl, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
  
      if (!response.ok) {
        throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
      }
  
      // Создаём Blob и заставляем браузер скачать
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = file.original_name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
  
      setSuccess("Файл скачан");
    } catch (err) {
      setError(`Ошибка скачивания: ${err.message}`);
    }
  }

  async function handleStatusChange(newStatus) {
    setStatusLoading(true);
    setError("");
    setSuccess("");

    try {
      const updated = await api.updateStatus(id, newStatus);
      setApplication(updated);
      setSuccess("Статус заявки обновлён");
    } catch (err) {
      setError(err.message);
    } finally {
      setStatusLoading(false);
    }
  }

  if (loading) return <Loader text="Загружаем заявку..." />;
  if (error && !application) return <ErrorMessage message={error} />;

  return (
    <section className="stack">
      <div className="page-header">
        <div>
          <p className="eyebrow">Карточка заявки</p>
          <h1>{application.title}</h1>
        </div>
        <StatusBadge status={application.status} />
      </div>

      {error && <ErrorMessage message={error} />}
      {success && <div className="success-box">{success}</div>}

      <div className="details-grid">
        <article className="card">
          <h2>Основная информация</h2>

          <dl className="details-list">
            <div>
              <dt>Конкурс</dt>
              <dd>{application.competition?.title}</dd>
            </div>

            <div>
              <dt>Дедлайн</dt>
              <dd>{formatDate(application.competition?.deadline)}</dd>
            </div>

            <div>
              <dt>Автор</dt>
              <dd>{application.owner?.full_name}</dd>
            </div>

            <div>
              <dt>Дата отправки</dt>
              <dd>{formatDateTime(application.submitted_at)}</dd>
            </div>

            <div>
              <dt>Запрашиваемая сумма</dt>
              <dd>
                {application.requested_amount
                  ? `${application.requested_amount} ₽`
                  : "—"}
              </dd>
            </div>
          </dl>

          <div className="text-block">
            <h3>Описание</h3>
            <p>{application.description}</p>
          </div>

          <div className="text-block">
            <h3>Цель проекта</h3>
            <p>{application.project_goal || "Не указана"}</p>
          </div>
        </article>

        <aside className="stack">
          <div className="card">
            <h2>ExpertAI</h2>

            {application.ai_review ? (
              <>
                <div className="score-box">
                  <span>Score</span>
                  <strong>{application.ai_review.score}%</strong>
                </div>

                <div className="text-block">
                  <h3>Краткий вывод</h3>
                  <p>{application.ai_review.summary || "Нет данных"}</p>
                </div>

                <div className="text-block">
                  <h3>Рекомендации</h3>
                  <p>{application.ai_review.recommendations || "Нет рекомендаций"}</p>
                </div>
              </>
            ) : (
              <p className="muted">AI-анализ ещё не сформирован.</p>
            )}
          </div>

          <div className="card">
            <h2>Документы</h2>

            {application.files?.length ? (
              <ul className="file-list">
                {application.files.map((file) => (
                  <li key={file.id} className="file-item">
                    <div>
                      <div>{file.original_name}</div>
                      <small>{Math.round(file.size_bytes / 1024)} KB</small>
                    </div>

                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => handleDownload(file)}
                    >
                      Скачать
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">Файлы ещё не загружены.</p>
            )}

            <form className="upload-form" onSubmit={handleUpload}>
              <input
                type="file"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              />
              <button
                className="btn btn-secondary"
                disabled={!selectedFile || uploading}
              >
                {uploading ? "Загружаем..." : "Загрузить файл"}
              </button>
            </form>
          </div>

          {user?.role === "admin" && (
            <div className="card">
              <h2>Решение администратора</h2>

              <div className="action-row">
                <button
                  className="btn btn-secondary"
                  disabled={statusLoading}
                  onClick={() => handleStatusChange("in_review")}
                >
                  На рассмотрение
                </button>

                <button
                  className="btn btn-success"
                  disabled={statusLoading}
                  onClick={() => handleStatusChange("approved")}
                >
                  Одобрить
                </button>

                <button
                  className="btn btn-danger"
                  disabled={statusLoading}
                  onClick={() => handleStatusChange("rejected")}
                >
                  Отклонить
                </button>
              </div>
            </div>
          )}
        </aside>
      </div>
    </section>
  );
}