import { Navigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function RoleGuard({ role, children }) {
  const { user } = useAuth();

  if (!user || user.role !== role) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}