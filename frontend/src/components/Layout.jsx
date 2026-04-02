import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth";

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">GK</div>
          <div>
            <div className="brand-title">Грантовый кабинет</div>
            <div className="brand-subtitle">ExpertAI workflow</div>
          </div>
        </div>

        <nav className="nav">
          <NavLink to="/dashboard" className="nav-link">
            Заявки
          </NavLink>
          <NavLink to="/applications/new" className="nav-link">
            Новая заявка
          </NavLink>
          {user?.role === "admin" && (
            <NavLink to="/admin" className="nav-link">
              Панель администратора
            </NavLink>
          )}
        </nav>

        <div className="sidebar-footer">
          <div className="user-card">
            <div className="user-name">{user?.full_name}</div>
            <div className="user-role">{user?.role === "admin" ? "Администратор" : "Заявитель"}</div>
          </div>
          <button className="btn btn-secondary w-full" onClick={logout}>
            Выйти
          </button>
        </div>
      </aside>

      <div className="content-area">
        <header className="topbar">
          <div>
            <p className="topbar-title">Сервис подачи и проверки грантовых заявок</p>
            <p className="topbar-subtitle">
              Создание заявки, отслеживание статуса, загрузка документов и просмотр AI-анализа
            </p>
          </div>
        </header>

        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}