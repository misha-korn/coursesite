import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/client.js";
import { Alert, Button, Card, Spinner } from "../components/ui.jsx";
import { useLang } from "../i18n/index.jsx";

function ProgressBar({ done, total }) {
  const percent = total ? Math.round((done / total) * 100) : 0;
  return (
    <div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
        <div className="h-full rounded-full bg-brand-600 transition-all" style={{ width: `${percent}%` }} />
      </div>
      <span className="mt-1 block text-xs text-slate-500">{percent}%</span>
    </div>
  );
}

export default function MyCourses() {
  const { t } = useLang();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const enrollmentsRaw = await api.get("/api/enrollments/");
        const enrollments = enrollmentsRaw.results ?? enrollmentsRaw;

        // Полные данные курса (в том числе список уроков) тянем по каждому курсу.
        const courses = await Promise.all(
          enrollments.map((e) => api.get(`/api/courses/${e.course}/`))
        );

        const progressRaw = await api.get("/api/lesson_progress/");
        const progress = progressRaw.results ?? progressRaw;
        const doneIds = new Set(progress.filter((p) => p.is_completed).map((p) => p.lesson));

        setItems(
          courses.map((course) => {
            const lessons = course.lessons ?? [];
            const done = lessons.filter((l) => doneIds.has(l.id)).length;
            const nextLesson = lessons.find((l) => !doneIds.has(l.id)) ?? lessons[0];
            return { course, total: lessons.length, done, nextLesson };
          })
        );
      } catch (e) {
        setError(e.text || t("common.error"));
      } finally {
        setLoading(false);
      }
    }

    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) return <Spinner text={t("common.loading")} />;

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <h1 className="mb-6 text-3xl font-bold text-ink">{t("student.myCourses")}</h1>

      {error && <Alert>{error}</Alert>}

      {!error && items.length === 0 && (
        <Card className="space-y-4 p-8 text-center">
          <p className="text-slate-600">{t("student.empty")}</p>
          <Link to="/catalog">
            <Button>{t("student.toCatalog")}</Button>
          </Link>
        </Card>
      )}

      <div className="space-y-4">
        {items.map(({ course, total, done, nextLesson }) => (
          <Card key={course.id} className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center">
            <div className="min-w-0 flex-1">
              <Link
                to={`/courses/${course.id}`}
                className="font-semibold text-ink hover:text-brand-600"
              >
                {course.title}
              </Link>
              <p className="mt-1 text-sm text-slate-500">
                {done} / {total} {t("student.lessonsDone")}
              </p>
              <div className="mt-3 max-w-sm">
                <ProgressBar done={done} total={total} />
              </div>
            </div>

            {nextLesson && (
              <Link to={`/lessons/${nextLesson.id}`} className="shrink-0">
                <Button>{t("course.open")}</Button>
              </Link>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
