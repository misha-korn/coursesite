import { useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/client.js";
import { Alert, Button, Card, Field, Input } from "../components/ui.jsx";
import { useLang } from "../i18n/index.jsx";

export default function ForgotPassword() {
  const { t } = useLang();

  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await api.post("/api/auth/password/reset/", { email });
      // Сервер намеренно отвечает одинаково для любого адреса,
      // поэтому и мы показываем один и тот же текст.
      setSent(true);
    } catch (err) {
      setError(err.text || t("common.error"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-md px-4 py-16">
      <Card className="space-y-5 p-7">
        <div>
          <h1 className="text-2xl font-bold text-ink">{t("auth.forgotTitle")}</h1>
          <p className="mt-2 text-sm text-slate-600">{t("auth.forgotSubtitle")}</p>
        </div>

        {sent ? (
          <>
            <Alert kind="success">{t("auth.forgotSent")}</Alert>
            <Link to="/login">
              <Button variant="outline" className="w-full">
                {t("auth.toLogin")}
              </Button>
            </Link>
          </>
        ) : (
          <form onSubmit={submit} className="space-y-4">
            <Field label={t("auth.email")}>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </Field>

            {error && <Alert>{error}</Alert>}

            <Button type="submit" className="w-full" disabled={busy}>
              {busy ? t("common.loading") : t("auth.sendLink")}
            </Button>
          </form>
        )}

        <p className="text-center text-sm text-slate-600">
          <Link to="/login" className="font-semibold text-brand-600 hover:underline">
            {t("auth.loginTitle")}
          </Link>
        </p>
      </Card>
    </div>
  );
}
