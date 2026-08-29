import { Link } from "react-router-dom";

import { mediaUrl } from "../api/client.js";
import { useLang } from "../i18n/index.jsx";
import { Badge, Card, Price, Stars } from "./ui.jsx";

// Обложек в API нет, поэтому рисуем цветную заглушку с первой буквой названия.
// Цвет стабильный: зависит от id, значит у курса он всегда один и тот же.
const COVERS = [
  "from-blue-500 to-indigo-600",
  "from-emerald-500 to-teal-600",
  "from-amber-500 to-orange-600",
  "from-fuchsia-500 to-purple-600",
  "from-rose-500 to-red-600",
];

export default function CourseCard({ course, categoryName }) {
  const { t } = useLang();
  const cover = COVERS[course.id % COVERS.length];
  const preview = mediaUrl(course.image_preview);

  return (
    <Link to={`/courses/${course.id}`} className="group block">
      <Card className="h-full overflow-hidden transition group-hover:-translate-y-0.5 group-hover:shadow-md">
        {/* Есть обложка - показываем её, нет - цветная заглушка с буквой */}
        {preview ? (
          <img src={preview} alt="" className="h-32 w-full object-cover" />
        ) : (
          <div
            className={`flex h-32 items-center justify-center bg-gradient-to-br ${cover} text-4xl font-bold text-white`}
          >
            {course.title.slice(0, 1).toUpperCase()}
          </div>
        )}

        <div className="space-y-2 p-4">
          <div className="flex items-center gap-2">
            {categoryName && <Badge>{categoryName}</Badge>}
            {course.status === "draft" && <Badge tone="amber">{t("course.draft")}</Badge>}
          </div>

          <h3 className="line-clamp-2 font-semibold text-ink group-hover:text-brand-600">
            {course.title}
          </h3>

          <div className="flex items-center gap-2 text-sm text-slate-500">
            {course.avg_rating ? (
              <>
                <Stars value={course.avg_rating} />
                <span>{course.avg_rating.toFixed(1)}</span>
              </>
            ) : (
              <span>{t("course.noRating")}</span>
            )}
          </div>

          <div className="flex items-center justify-between pt-1">
            <span className="text-sm text-slate-500">
              {course.students_count} {t("course.students")}
            </span>
            <Price value={course.price} currency={t("common.rub")} freeLabel={t("course.free")} />
          </div>
        </div>
      </Card>
    </Link>
  );
}
