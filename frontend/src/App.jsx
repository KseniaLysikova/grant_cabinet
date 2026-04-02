import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import RoleGuard from "./components/RoleGuard";
import Layout from "./components/Layout";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import CreateApplicationPage from "./pages/CreateApplicationPage";
import ApplicationDetailsPage from "./pages/ApplicationDetailsPage";
import AdminPage from "./pages/AdminPage";
import NotFoundPage from "./pages/NotFoundPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/applications/new" element={<CreateApplicationPage />} />
        <Route path="/applications/:id" element={<ApplicationDetailsPage />} />

        <Route
          path="/admin"
          element={
            <RoleGuard role="admin">
              <AdminPage />
            </RoleGuard>
          }
        />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}