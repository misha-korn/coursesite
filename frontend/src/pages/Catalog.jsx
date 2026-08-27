import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { api, withQuery } from "../api/client.js";
import CourseCard from "../components/CourseCard.jsx";
import { Alert, Button, Card, Field, Input, Select, Spinner } from "../components/ui.jsx";
import { useCategories } from "../hooks/useCategories.js";
import { useLang } from "../i18n/index.jsx";

// Фильтры живут в адресной строке: ссылку на выборку можно скинуть другому.
export default function Catalog() {
  const { t } = useLang();
  const { categories, nameById } = useCategories();
  const [params, setParams] = useSearchParams();

  const [data, setData] = useState({ results: [], count: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const get = (key, fallback = "") => params.get(key) ?? fallback;
  const page = Number(get("page", 1));

  useEffect(() => {
    setLoading(true);
    setError(null);

    const url = withQuery("/api/courses/", {
      search: get("search"),
      category_id: get("category_id"),
      price_min: get("price_min"),
      price_max: get("price_max"),
      ordering: get("ordering", "-created_at"),
      page: page > 1 ? page : "",
    });

    api
      .get(url)
      .then((res) => setData(res.results ? res : { results: res, count: res.length }))
      .catch((e) => setError(e.text || t("common.error")))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params]);

  // Меняем один параметр и всегда сбрасываем страницу на первую.
  const update = (key, value) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    next.delete("page");
    setParams(next);
  };

  const goToPage = (nextPage) => {
    const next = new URLSearchParams(params);
    next.set("page", nextPage);
    setParams(next);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const pageSize = 20;
  const lastPage = Math.max(1, Math.ceil(data.count / pageSize));

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="mb-6 text-3xl font-bold text-ink">{t("catalog.title")}</h1>

      <div className="grid gap-8 lg:grid-cols-[260px_1fr]">
        <Card className="h-fit space-y-4 p-5">
          <h2 className="font-semibold text-ink">{t("catalog.filters")}</h2>

          <Field label={t("catalog.category")}>
            <Select value={get("category_id")} onChange={(e) => update("category_id", e.target.value)}>
              <option value="">{t("catalog.allCategories")}</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </Select>
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label={t("catalog.priceFrom")}>
              <Input
                type="number"
                min="0"
                value={get("price_min")}
                onChange={(e) => update("price_min", e.target.value)}
              />
            </Field>
            <Field label={t("catalog.priceTo")}>
              <Input
                type="number"
                min="0"
                value={get("price_max")}
                onChange={(e) => update("price_max", e.target.value)}
              />
            </Field>
          </div>

          <Field label={t("catalog.sort")}>
            <Select value={get("ordering", "-created_at")} onChange={(e) => update("ordering", e.target.value)}>
              <option value="-created_at">{t("catalog.sortNewest")}</option>
              <option value="price">{t("catalog.sortCheap")}</option>
              <option value="-price">{t("catalog.sortExpensive")}</option>
              <option value="-students_count">{t("catalog.sortPopular")}</option>
              <option value="-avg_rating">{t("catalog.sortRating")}</option>
            </Select>
          </Field>

          <Button variant="outline" className="w-full" onClick={() => setParams({})}>
            {t("catalog.reset")}
          </Button>
        </Card>

        <div>
          <div className="mb-4">
            <Input
              value={get("search")}
              onChange={(e) => update("search", e.target.value)}
              placeholder={t("home.searchPlaceholder")}
            />
          </div>

          {loading && <Spinner text={t("common.loading")} />}
          {error && <Alert>{error}</Alert>}

          {!loading && !error && (
            <>
              <p className="mb-4 text-sm text-slate-500">
                {t("catalog.found")} {data.count}
              </p>

              {data.results.length === 0 ? (
                <Alert kind="info">{t("catalog.empty")}</Alert>
              ) : (
                <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
                  {data.results.map((course) => (
                    <CourseCard
                      key={course.id}
                      course={course}
                      categoryName={nameById(course.category)}
                    />
                  ))}
                </div>
              )}

              {lastPage > 1 && (
                <div className="mt-8 flex items-center justify-center gap-4">
                  <Button variant="outline" disabled={page <= 1} onClick={() => goToPage(page - 1)}>
                    {t("catalog.prev")}
                  </Button>
                  <span className="text-sm text-slate-500">
                    {t("catalog.page")} {page} / {lastPage}
                  </span>
                  <Button
                    variant="outline"
                    disabled={page >= lastPage}
                    onClick={() => goToPage(page + 1)}
                  >
                    {t("catalog.next")}
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
