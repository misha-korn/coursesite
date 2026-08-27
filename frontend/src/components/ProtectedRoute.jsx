import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../context/AuthContext.jsx";
import { useLang } from "../i18n/index.jsx";
import { Alert, Spinner } from "./ui.jsx";

// Оборачивает приватные маршруты. teacherOnly закрывает раздел преподавателя.
export default function ProtectedRoute({ teacherOnly = false }) {
  const { user, loading, isTeacher } = useAuth();
  const { t } = useLang();
  const location = useLocation();

  if (loading) return <Spinner text={t("common.loading")} />;

  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />;

  if (teacherOnly && !isTeacher) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16">
        <Alert>{t("teacher.onlyTeachers")}</Alert>
      </div>
    );
  }

  return <Outlet />;
}
