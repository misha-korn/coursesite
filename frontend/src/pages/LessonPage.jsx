import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api } from "../api/client.js";
import { Alert, Button, Card, Spinner } from "../components/ui.jsx";
import { useLang } from "../i18n/index.jsx";

// Превращает обычную ссылку YouTube во встраиваемую. Для других ссылок
// вернём null и просто покажем кликабельный адрес.
function toEmbed(url) {
  if (!url) return null;
  const match = url.match(/(?:youtu\.be\/|v=)([\w-]{11})/);
  return match ? `https://www.youtube.com/embed/${match[1]}` : null;
}

export default function LessonPage() {
  const { id } = useParams();
  const { t } = useLang();
  const navigate = useNavigate();

  const [lesson, setLesson] = useState(null);
  const [siblings, setSiblings] = useState([]);
  const [progressId, setProgressId] = useState(null);
  const [isDone, setIsDone] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await api.get(`/api/lessons/${id}/`);
        setLesson(data);

        const course = await api.get(`/api/courses/${data.course}/`);
        setSiblings(course.lessons ?? []);

        const progressRaw = await api.get("/api/lesson_progress/");
        const progress = (progressRaw.results ?? progressRaw).find(
          (p) => p.lesson === Number(id)
        );
        setProgressId(progress?.id ?? null);
        setIsDone(Boolean(progress?.is_completed));
      } catch (e) {
        // 403 или 404 здесь означают, что курс не куплен.
        setError(e.status === 404 || e.status === 403 ? t("student.lessonLocked") : e.text);
      } finally {
        setLoading(false);
      }
    }

    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const markDone = async () => {
    setSaving(true);
    try {
      if (progressId) {
        await api.patch(`/api/lesson_progress/${progressId}/`, { is_completed: true });
      } else {
        const created = await api.post("/api/lesson_progress/", {
          lesson: Number(id),
          is_completed: true,
        });
        setProgressId(created.id);
      }
      setIsDone(true);
    } catch (e) {
      setError(e.text || t("common.error"));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Spinner text={t("common.loading")} />;

  if (error && !lesson) {
    return (
      <div className="mx-auto max-w-3xl space-y-4 px-4 py-16">
        <Alert>{error}</Alert>
        <Button variant="outline" onClick={() => navigate(-1)}>
          {t("common.back")}
        </Button>
      </div>
    );
  }

  const embed = toEmbed(lesson.video_url);
  const index = siblings.findIndex((l) => l.id === lesson.id);
  const prev = index > 0 ? siblings[index - 1] : null;
  const next = index >= 0 && index < siblings.length - 1 ? siblings[index + 1] : null;

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <div className="grid gap-8 lg:grid-cols-[1fr_280px]">
        <div className="space-y-6">
          <div>
            <Link
              to={`/courses/${lesson.course}`}
              className="text-sm font-medium text-brand-600 hover:underline"
            >
              ← {t("student.backToCourse")}
            </Link>
            <h1 className="mt-2 text-3xl font-bold text-ink">
              {lesson.number}. {lesson.title}
            </h1>
          </div>

          {embed && (
            <div className="aspect-video overflow-hidden rounded-xl bg-black">
              <iframe
                src={embed}
                title={lesson.title}
                allowFullScreen
                className="h-full w-full"
              />
            </div>
          )}

          {!embed && lesson.video_url && (
            <a
              href={lesson.video_url}
              target="_blank"
              rel="noreferrer"
              className="text-brand-600 hover:underline"
            >
              {lesson.video_url}
            </a>
          )}

          <article className="whitespace-pre-line leading-relaxed text-slate-700">
            {lesson.content}
          </article>

          {error && <Alert>{error}</Alert>}

          <div className="flex flex-wrap items-center gap-3 border-t border-slate-200 pt-6">
            {isDone ? (
              <span className="rounded-lg bg-emerald-50 px-4 py-2.5 text-sm font-semibold text-emerald-700">
                ✓ {t("student.done")}
              </span>
            ) : (
              <Button onClick={markDone} disabled={saving}>
                {saving ? t("common.loading") : t("student.markDone")}
              </Button>
            )}

            <div className="ml-auto flex gap-2">
              {prev && (
                <Link to={`/lessons/${prev.id}`}>
                  <Button variant="outline">←</Button>
                </Link>
              )}
              {next && (
                <Link to={`/lessons/${next.id}`}>
                  <Button variant="outline">→</Button>
                </Link>
              )}
            </div>
          </div>
        </div>

        <aside>
          <Card className="sticky top-24 divide-y divide-slate-200 overflow-hidden">
            {siblings.map((l) => (
              <Link
                key={l.id}
                to={`/lessons/${l.id}`}
                className={`block px-4 py-3 text-sm hover:bg-slate-50 ${
                  l.id === lesson.id ? "bg-brand-50 font-semibold text-brand-700" : "text-slate-700"
                }`}
              >
                {l.number}. {l.title}
              </Link>
            ))}
          </Card>
        </aside>
      </div>
    </div>
  );
}
