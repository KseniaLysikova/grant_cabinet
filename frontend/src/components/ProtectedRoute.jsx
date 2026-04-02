import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth";
import Loader from "./Loader";

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <Loader fullPage text="Проверяем авторизацию..." />;
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}