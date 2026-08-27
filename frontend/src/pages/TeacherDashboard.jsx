import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api, withQuery } from "../api/client.js";
import { Alert, Badge, Button, Card, Price, Spinner } from "../components/ui.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { useCategories } from "../hooks/useCategories.js";
import { useLang } from "../i18n/index.jsx";

export default function TeacherDashboard() {
  const { t } = useLang();
  const { user } = useAuth();
  const { nameById } = useCategories();

  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // author_id - фильтр из CourseFilter на бэкенде.
    api
      .get(withQuery("/api/courses/", { author_id: user.id, page_size: 100 }))
      .then((data) => setCourses(data.results ?? data))
      .catch((e) => setError(e.text || t("common.error")))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user.id]);

  if (loading) return <Spinner text={t("common.loading")} />;

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-ink">{t("teacher.dashboard")}</h1>
        <Link to="/teach/courses/new">
          <Button>{t("teacher.newCourse")}</Button>
        </Link>
      </div>

      {error && <Alert>{error}</Alert>}

      {!error && courses.length === 0 && (
        <Card className="p-8 text-center text-slate-600">{t("teacher.noCourses")}</Card>
      )}

      <div className="space-y-3">
        {courses.map((course) => (
          <Card key={course.id} className="flex items-center gap-4 p-5">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <h2 className="font-semibold text-ink">{course.title}</h2>
                <Badge tone={course.status === "published" ? "green" : "amber"}>
                  {course.status === "published" ? t("teacher.published") : t("teacher.draft")}
                </Badge>
              </div>
              <p className="mt-1 text-sm text-slate-500">
                {nameById(course.category)} · {course.students_count} {t("course.students")}
              </p>
            </div>

            <Price value={course.price} currency={t("common.rub")} freeLabel={t("course.free")} />

            <Link to={`/teach/courses/${course.id}`}>
              <Button variant="outline">{t("teacher.editCourse")}</Button>
            </Link>
          </Card>
        ))}
      </div>
    </div>
  );
}
