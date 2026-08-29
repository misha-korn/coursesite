import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api } from "../api/client.js";
import { Alert, Button, Card, Spinner } from "../components/ui.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { useLang } from "../i18n/index.jsx";

// Одна страница на два сценария: подтверждение почты после регистрации
// и подтверждение нового адреса при смене. Отличаются только эндпоинтом
// и текстами, поэтому логика общая.
const MODES = {
  verify: {
    endpoint: "/api/auth/email/verify/confirm/",
    titleKey: "auth.verifyTitle",
    okKey: "auth.verifyOk",
  },
  change: {
    endpoint: "/api/auth/email/change/confirm/",
    titleKey: "auth.changeEmailTitle",
    okKey: "auth.changeEmailOk",
  },
};

export default function ConfirmToken({ mode }) {
  const { token } = useParams();
  const { t } = useLang();
  const { user, refreshUser } = useAuth();

  const [state, setState] = useState("loading"); // loading | ok | error
  const [error, setError] = useState(null);
  const sent = useRef(false); // StrictMode в разработке монтирует дважды

  const config = MODES[mode];

  useEffect(() => {
    if (!token || sent.current) return;
    sent.current = true;

    api
      .post(config.endpoint, { token })
      .then(async () => {
        setState("ok");
        // Если человек залогинен, обновим его данные: статус или адрес изменились.
        if (user) await refreshUser().catch(() => {});
      })
      .catch((err) => {
        setError(err.text || t("common.error"));
        setState("error");
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return (
    <div className="mx-auto max-w-md px-4 py-16">
      <Card className="space-y-5 p-7 text-center">
        <h1 className="text-2xl font-bold text-ink">{t(config.titleKey)}</h1>

        {!token && <Alert>{t("auth.noToken")}</Alert>}

        {token && state === "loading" && <Spinner text={t("auth.verifyChecking")} />}

        {state === "ok" && (
          <>
            <div className="text-5xl">✓</div>
            <Alert kind="success">{t(config.okKey)}</Alert>
            <Link to={user ? "/profile" : "/login"}>
              <Button className="w-full">
                {user ? t("auth.toProfile") : t("auth.toLogin")}
              </Button>
            </Link>
          </>
        )}

        {state === "error" && (
          <>
            <Alert>{error}</Alert>
            <Link to="/">
              <Button variant="outline" className="w-full">
                {t("auth.toHome")}
              </Button>
            </Link>
          </>
        )}
      </Card>
    </div>
  );
}
