import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { api } from "../api/client.js";
import ImageManager from "../components/ImageManager.jsx";
import {
  Alert,
  Button,
  Card,
  Field,
  Input,
  Select,
  Spinner,
  Textarea,
} from "../components/ui.jsx";
import { useCategories } from "../hooks/useCategories.js";
import { useLang } from "../i18n/index.jsx";

const EMPTY_COURSE = {
  title: "",
  description: "",
  price: "",
  category: "",
  status: "draft",
};

const EMPTY_LESSON = {
  title: "",
  number: 1,
  content: "",
  video_url: "",
  duration_minutes: 10,
};

// Одна страница на два случая: создание нового курса и редактирование готового.
// Уроки показываем только у сохранённого курса, потому что уроку нужен course_id.
export default function CourseEditor() {
  const { id } = useParams();
  const isNew = !id;
  const { t } = useLang();
  const { categories } = useCategories();
  const navigate = useNavigate();

  const [course, setCourse] = useState(EMPTY_COURSE);
  const [lessons, setLessons] = useState([]);
  const [courseImages, setCourseImages] = useState([]);
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const [lessonForm, setLessonForm] = useState(null); // null = форма закрыта

  const loadCourse = async () => {
    try {
      const data = await api.get(`/api/courses/${id}/`);
      setCourse({
        title: data.title,
        description: data.description,
        price: data.price,
        category: data.category,
        status: data.status,
      });
      setLessons(data.lessons ?? []);
      setCourseImages(data.course_images ?? []);
    } catch (e) {
      setError(e.text || t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isNew) loadCourse();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const saveCourse = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      if (isNew) {
        const created = await api.post("/api/courses/", course);
        navigate(`/teach/courses/${created.id}`, { replace: true });
      } else {
        await api.patch(`/api/courses/${id}/`, course);
        await loadCourse();
      }
    } catch (err) {
      setError(err.text || t("common.error"));
    } finally {
      setSaving(false);
    }
  };

  const removeCourse = async () => {
    if (!window.confirm(t("teacher.confirmDelete"))) return;
    try {
      await api.delete(`/api/courses/${id}/`);
      navigate("/teach", { replace: true });
    } catch (err) {
      setError(err.text || t("common.error"));
    }
  };

  const saveLesson = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const payload = { ...lessonForm, course: Number(id) };
      if (lessonForm.id) await api.patch(`/api/lessons/${lessonForm.id}/`, payload);
      else await api.post("/api/lessons/", payload);

      setLessonForm(null);
      await loadCourse();
    } catch (err) {
      setError(err.text || t("common.error"));
    }
  };

  const removeLesson = async (lessonId) => {
    try {
      await api.delete(`/api/lessons/${lessonId}/`);
      await loadCourse();
    } catch (err) {
      setError(err.text || t("common.error"));
    }
  };

  if (loading) return <Spinner text={t("common.loading")} />;

  return (
    <div className="mx-auto max-w-3xl space-y-8 px-4 py-10">
      <h1 className="text-3xl font-bold text-ink">
        {isNew ? t("teacher.newCourse") : t("teacher.editCourse")}
      </h1>

      {error && <Alert>{error}</Alert>}

      <Card className="p-6">
        <form onSubmit={saveCourse} className="space-y-4">
          <Field label={t("teacher.title")}>
            <Input
              value={course.title}
              onChange={(e) => setCourse({ ...course, title: e.target.value })}
              required
            />
          </Field>

          <Field label={t("teacher.description")}>
            <Textarea
              value={course.description}
              onChange={(e) => setCourse({ ...course, description: e.target.value })}
              required
            />
          </Field>

          <div className="grid gap-4 sm:grid-cols-3">
            <Field label={t("teacher.price")}>
              <Input
                type="number"
                min="0"
                step="0.01"
                value={course.price}
                onChange={(e) => setCourse({ ...course, price: e.target.value })}
                required
              />
            </Field>

            <Field label={t("teacher.category")}>
              <Select
                value={course.category}
                onChange={(e) => setCourse({ ...course, category: e.target.value })}
                required
              >
                <option value="">—</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </Select>
            </Field>

            <Field label={t("teacher.status")}>
              <Select
                value={course.status}
                onChange={(e) => setCourse({ ...course, status: e.target.value })}
              >
                <option value="draft">{t("teacher.draft")}</option>
                <option value="published">{t("teacher.published")}</option>
              </Select>
            </Field>
          </div>

          <div className="flex gap-3">
            <Button type="submit" disabled={saving}>
              {saving ? t("common.loading") : t("teacher.save")}
            </Button>
            {!isNew && (
              <Button type="button" variant="danger" onClick={removeCourse}>
                {t("teacher.delete")}
              </Button>
            )}
            <Button type="button" variant="ghost" onClick={() => navigate("/teach")}>
              {t("common.cancel")}
            </Button>
          </div>
        </form>
      </Card>

      {!isNew && (
        <ImageManager
          endpoint="/api/courses-images/"
          ownerField="course"
          ownerId={id}
          images={courseImages}
          onChange={loadCourse}
        />
      )}

      {!isNew && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-ink">{t("teacher.lessons")}</h2>
            <Button
              variant="outline"
              onClick={() =>
                setLessonForm({ ...EMPTY_LESSON, number: lessons.length + 1 })
              }
            >
              {t("teacher.addLesson")}
            </Button>
          </div>

          {lessons.length === 0 && (
            <Card className="p-6 text-center text-sm text-slate-500">
              {t("teacher.noLessons")}
            </Card>
          )}

          <Card className="divide-y divide-slate-200">
            {lessons.map((lesson) => (
              <div key={lesson.id} className="flex items-center gap-3 px-4 py-3">
                <span className="w-6 text-sm text-slate-500">{lesson.number}</span>
                <span className="flex-1 text-sm text-ink">{lesson.title}</span>
                <span className="text-xs text-slate-500">
                  {lesson.duration_minutes} {t("course.min")}
                </span>
                <Button
                  variant="ghost"
                  onClick={async () => {
                    // В списке нет content и video_url, поэтому берём урок целиком.
                    const full = await api.get(`/api/lessons/${lesson.id}/`);
                    setLessonForm(full);
                  }}
                >
                  ✎
                </Button>
                <Button variant="ghost" onClick={() => removeLesson(lesson.id)}>
                  ✕
                </Button>
              </div>
            ))}
          </Card>

          {lessonForm && (
            <Card className="p-6">
              <h3 className="mb-4 font-semibold text-ink">
                {lessonForm.id ? t("teacher.editLesson") : t("teacher.addLesson")}
              </h3>

              <form onSubmit={saveLesson} className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-[1fr_120px_140px]">
                  <Field label={t("teacher.lessonTitle")}>
                    <Input
                      value={lessonForm.title}
                      onChange={(e) => setLessonForm({ ...lessonForm, title: e.target.value })}
                      required
                    />
                  </Field>
                  <Field label={t("teacher.lessonNumber")}>
                    <Input
                      type="number"
                      min="1"
                      value={lessonForm.number}
                      onChange={(e) => setLessonForm({ ...lessonForm, number: e.target.value })}
                      required
                    />
                  </Field>
                  <Field label={t("teacher.duration")}>
                    <Input
                      type="number"
                      min="0"
                      value={lessonForm.duration_minutes}
                      onChange={(e) =>
                        setLessonForm({ ...lessonForm, duration_minutes: e.target.value })
                      }
                    />
                  </Field>
                </div>

                <Field label={t("teacher.videoUrl")}>
                  <Input
                    value={lessonForm.video_url || ""}
                    onChange={(e) => setLessonForm({ ...lessonForm, video_url: e.target.value })}
                    placeholder="https://www.youtube.com/watch?v=..."
                  />
                </Field>

                <Field label={t("teacher.content")}>
                  <Textarea
                    value={lessonForm.content}
                    onChange={(e) => setLessonForm({ ...lessonForm, content: e.target.value })}
                    required
                  />
                </Field>

                <div className="flex gap-3">
                  <Button type="submit">{t("teacher.save")}</Button>
                  <Button type="button" variant="ghost" onClick={() => setLessonForm(null)}>
                    {t("common.cancel")}
                  </Button>
                </div>
              </form>
            </Card>
          )}
        </section>
      )}
    </div>
  );
}
