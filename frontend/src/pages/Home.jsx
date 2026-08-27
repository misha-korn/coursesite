import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { api } from "../api/client.js";
import CourseCard from "../components/CourseCard.jsx";
import { Button, Input, Spinner } from "../components/ui.jsx";
import { useCategories } from "../hooks/useCategories.js";
import { useLang } from "../i18n/index.jsx";

export default function Home() {
  const { t } = useLang();
  const navigate = useNavigate();
  const { nameById } = useCategories();

  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");

  useEffect(() => {
    api
      .get("/api/courses/?ordering=-students_count")
      .then((data) => setCourses((data.results ?? data).slice(0, 6)))
      .catch(() => setCourses([]))
      .finally(() => setLoading(false));
  }, []);

  const submitSearch = (e) => {
    e.preventDefault();
    navigate(`/catalog?search=${encodeURIComponent(query)}`);
  };

  return (
    <>
      <section className="bg-gradient-to-b from-brand-50 to-white">
        <div className="mx-auto max-w-6xl px-4 py-20 text-center">
          <h1 className="mx-auto max-w-3xl text-4xl font-bold text-ink sm:text-5xl">
            {t("home.heroTitle")}
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-slate-600">{t("home.heroSubtitle")}</p>

          <form onSubmit={submitSearch} className="mx-auto mt-8 flex max-w-xl gap-2">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t("home.searchPlaceholder")}
            />
            <Button type="submit" className="shrink-0">
              {t("home.searchButton")}
            </Button>
          </form>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-14">
        <div className="mb-6 flex items-end justify-between">
          <h2 className="text-2xl font-bold text-ink">{t("home.popular")}</h2>
          <Link to="/catalog" className="text-sm font-semibold text-brand-600 hover:underline">
            {t("home.viewAll")}
          </Link>
        </div>

        {loading ? (
          <Spinner text={t("common.loading")} />
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {courses.map((course) => (
              <CourseCard key={course.id} course={course} categoryName={nameById(course.category)} />
            ))}
          </div>
        )}
      </section>

      <section className="border-t border-slate-200 bg-slate-50">
        <div className="mx-auto max-w-6xl px-4 py-14">
          <h2 className="mb-8 text-center text-2xl font-bold text-ink">{t("home.stepsTitle")}</h2>
          <div className="grid gap-8 sm:grid-cols-3">
            {[1, 2, 3].map((n) => (
              <div key={n} className="text-center">
                <div className="mx-auto mb-3 flex h-11 w-11 items-center justify-center rounded-full bg-brand-600 text-lg font-bold text-white">
                  {n}
                </div>
                <h3 className="mb-1 font-semibold text-ink">{t(`home.step${n}Title`)}</h3>
                <p className="text-sm text-slate-600">{t(`home.step${n}Text`)}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
