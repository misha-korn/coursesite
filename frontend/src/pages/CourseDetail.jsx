import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api, withQuery } from "../api/client.js";
import Gallery from "../components/Gallery.jsx";
import { Alert, Badge, Button, Card, Field, Price, Spinner, Stars, Textarea } from "../components/ui.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { useCategories } from "../hooks/useCategories.js";
import { useLang } from "../i18n/index.jsx";

export default function CourseDetail() {
  const { id } = useParams();
  const { t } = useLang();
  const { user } = useAuth();
  const { nameById } = useCategories();
  const navigate = useNavigate();

  const [course, setCourse] = useState(null);
  const [owned, setOwned] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [buying, setBuying] = useState(false);
  const [rating, setRating] = useState(5);
  const [reviewText, setReviewText] = useState("");
  const [reviewMsg, setReviewMsg] = useState(null);

  // Отзывы приходят двумя путями: первые пять внутри курса,
  // остальные подгружаются постранично с отдельного эндпоинта.
  const [extraReviews, setExtraReviews] = useState([]);
  const [reviewsPage, setReviewsPage] = useState(1);
  const [loadingMore, setLoadingMore] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await api.get(`/api/courses/${id}/`);
      setCourse(data);

      if (user) {
        const enrollments = await api.get("/api/enrollments/");
        const list = enrollments.results ?? enrollments;
        setOwned(list.some((e) => e.course === data.id));
      }
    } catch (e) {
      setError(e.text || t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, user]);

  const buy = async () => {
    if (!user) return navigate("/login", { state: { from: `/courses/${id}` } });

    setBuying(true);
    setError(null);
    try {
      const { payment_url } = await api.post("/api/payments/", { course: course.id });
      // Провайдер оплаты уводит пользователя на свою страницу.
      if (payment_url) window.location.href = payment_url;
    } catch (e) {
      setError(e.text || t("common.error"));
    } finally {
      setBuying(false);
    }
  };

  const sendReview = async (e) => {
    e.preventDefault();
    setReviewMsg(null);
    try {
      await api.post("/api/reviews/", {
        course: course.id,
        rating,
        description: reviewText,
      });
      setReviewText("");
      setReviewMsg({ kind: "success", text: t("course.reviewSent") });
      load();
    } catch (err) {
      setReviewMsg({ kind: "error", text: err.text || t("course.reviewOnlyOwners") });
    }
  };

  if (loading) return <Spinner text={t("common.loading")} />;
  if (!course) return <div className="mx-auto max-w-3xl px-4 py-16"><Alert>{error}</Alert></div>;

  const lessons = course.lessons ?? [];
  const preview = course.reviews_preview ?? [];
  const reviews = [...preview, ...extraReviews];
  const reviewsCount = course.reviews_count ?? reviews.length;
  const author = course.author ?? null;
  const hasMoreReviews = reviews.length < reviewsCount;

  const loadMoreReviews = async () => {
    setLoadingMore(true);
    try {
      const nextPage = reviewsPage + 1;
      const data = await api.get(
        withQuery("/api/reviews/", { course: course.id, ordering: "-created_at", page: nextPage })
      );
      setExtraReviews((prev) => [...prev, ...(data.results ?? data)]);
      setReviewsPage(nextPage);
    } catch (e) {
      setError(e.text || t("common.error"));
    } finally {
      setLoadingMore(false);
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
        <div className="space-y-8">
          <div>
            <div className="mb-3 flex items-center gap-2">
              {nameById(course.category) && <Badge>{nameById(course.category)}</Badge>}
              {course.status === "draft" && <Badge tone="amber">{t("course.draft")}</Badge>}
            </div>

            <h1 className="text-3xl font-bold text-ink">{course.title}</h1>

            <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-slate-600">
              {course.avg_rating ? (
                <span className="flex items-center gap-1.5">
                  <Stars value={course.avg_rating} />
                  {course.avg_rating.toFixed(1)}
                </span>
              ) : (
                <span>{t("course.noRating")}</span>
              )}
              <span>
                {course.students_count} {t("course.students")}
              </span>
              <span>
                {lessons.length} {t("course.lessons")}
              </span>
            </div>
          </div>

          {course.course_images?.length > 0 && <Gallery images={course.course_images} />}

          <section>
            <h2 className="mb-3 text-xl font-bold text-ink">{t("course.about")}</h2>
            <p className="whitespace-pre-line leading-relaxed text-slate-700">
              {course.description}
            </p>
          </section>

          <section>
            <h2 className="mb-3 text-xl font-bold text-ink">{t("course.program")}</h2>
            <Card className="divide-y divide-slate-200">
              {lessons.map((lesson) => {
                const row = (
                  <div className="flex items-center gap-3 px-4 py-3">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-600">
                      {lesson.number}
                    </span>
                    <span className="flex-1 text-sm text-ink">{lesson.title}</span>
                    <span className="text-xs text-slate-500">
                      {lesson.duration_minutes} {t("course.min")}
                    </span>
                    {!owned && <span className="text-slate-400">🔒</span>}
                  </div>
                );

                return owned ? (
                  <Link key={lesson.id} to={`/lessons/${lesson.id}`} className="block hover:bg-slate-50">
                    {row}
                  </Link>
                ) : (
                  <div key={lesson.id}>{row}</div>
                );
              })}
            </Card>
          </section>

          <section>
            <h2 className="mb-3 text-xl font-bold text-ink">
              {t("course.reviews")} ({reviewsCount})
            </h2>

            {reviews.length === 0 ? (
              <p className="text-sm text-slate-500">{t("course.noReviews")}</p>
            ) : (
              <div className="space-y-3">
                {reviews.map((r) => (
                  <Card key={r.id} className="p-4">
                    <div className="mb-1 flex items-center gap-2">
                      <Stars value={r.rating} />
                      <span className="text-xs text-slate-500">
                        {new Date(r.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm text-slate-700">{r.description}</p>
                  </Card>
                ))}
              </div>
            )}

            {hasMoreReviews && (
              <Button
                variant="outline"
                className="mt-4"
                onClick={loadMoreReviews}
                disabled={loadingMore}
              >
                {loadingMore ? t("common.loading") : t("course.showMore")}
              </Button>
            )}

            {owned && (
              <Card className="mt-5 space-y-4 p-5">
                <h3 className="font-semibold text-ink">{t("course.leaveReview")}</h3>
                <form onSubmit={sendReview} className="space-y-4">
                  <Field label={t("course.yourRating")}>
                    <Stars value={rating} onChange={setRating} />
                  </Field>
                  <Field label={t("course.reviewText")}>
                    <Textarea
                      value={reviewText}
                      onChange={(e) => setReviewText(e.target.value)}
                      required
                    />
                  </Field>
                  {reviewMsg && <Alert kind={reviewMsg.kind}>{reviewMsg.text}</Alert>}
                  <Button type="submit">{t("course.sendReview")}</Button>
                </form>
              </Card>
            )}
          </section>
        </div>

        <aside>
          <Card className="sticky top-24 space-y-4 p-6">
            <div className="text-3xl">
              <Price value={course.price} currency={t("common.rub")} freeLabel={t("course.free")} />
            </div>

            {error && <Alert>{error}</Alert>}

            {owned ? (
              <>
                <Alert kind="success">{t("course.owned")}</Alert>
                <Link to="/my-courses">
                  <Button className="w-full">{t("course.open")}</Button>
                </Link>
              </>
            ) : (
              <Button className="w-full" onClick={buy} disabled={buying}>
                {buying ? t("course.payRedirect") : user ? t("course.buy") : t("course.loginToBuy")}
              </Button>
            )}

            {author && (
              <div className="flex items-center gap-2 border-t border-slate-200 pt-4">
                {author.image ? (
                  <img
                    src={author.image}
                    alt={author.username}
                    className="h-9 w-9 rounded-full object-cover"
                  />
                ) : (
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700">
                    {author.username.slice(0, 1).toUpperCase()}
                  </span>
                )}
                <div className="min-w-0">
                  <p className="text-xs text-slate-500">{t("course.author")}</p>
                  <p className="truncate text-sm font-medium text-ink">{author.username}</p>
                </div>
              </div>
            )}
          </Card>
        </aside>
      </div>
    </div>
  );
}
