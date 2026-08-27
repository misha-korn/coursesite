import { Link } from "react-router-dom";

import { Button } from "../components/ui.jsx";
import { useLang } from "../i18n/index.jsx";

export default function NotFound() {
  const { t } = useLang();

  return (
    <div className="mx-auto max-w-md px-4 py-24 text-center">
      <p className="text-6xl font-bold text-brand-600">404</p>
      <h1 className="mt-4 text-xl font-semibold text-ink">{t("common.notFound")}</h1>
      <Link to="/" className="mt-6 inline-block">
        <Button>{t("common.toHome")}</Button>
      </Link>
    </div>
  );
}
