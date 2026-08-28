import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api } from "../api/client.js";
import { Alert, Button, Card, Field, Input } from "../components/ui.jsx";
import { useLang } from "../i18n/index.jsx";

// Ссылка из письма: /reset-password/<token>/
// Токен подписан на сервере и содержит внутри и пользователя, и срок годности.
export default function ResetPassword() {
  const { token } = useParams();
  const { t } = useLang();
  const navigate = useNavigate();

  const [form, setForm] = useState({ new_password: "", repeat: "" });
  const [done, setDone] = useState(false);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);

    if (form.new_password !== form.repeat) {
      setError(t("profile.passwordsDiffer"));
      return;
    }

    setBusy(true);
    try {
      await api.post("/api/auth/password/reset/confirm/", {
        token,
        new_password: form.new_password,
      });
      setDone(true);
      setTimeout(() => navigate("/login", { replace: true }), 2000);
    } catch (err) {
      // Тут приходят понятные тексты от сервера: срок истёк,
      // ссылка недействительна, ссылка уже использована.
      setError(err.text || t("common.error"));
    } finally {
      setBusy(false);
    }
  };

  if (!token) {
    return (
      <div className="mx-auto max-w-md px-4 py-16">
        <Card className="space-y-4 p-7">
          <Alert>{t("auth.noToken")}</Alert>
          <Link to="/forgot-password">
            <Button variant="outline" className="w-full">
              {t("auth.forgotTitle")}
            </Button>
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-md px-4 py-16">
      <Card className="space-y-5 p-7">
        <div>
          <h1 className="text-2xl font-bold text-ink">{t("auth.resetTitle")}</h1>
          <p className="mt-2 text-sm text-slate-600">{t("auth.resetSubtitle")}</p>
        </div>

        {done ? (
          <>
            <Alert kind="success">{t("auth.resetDone")}</Alert>
            <Link to="/login">
              <Button className="w-full">{t("auth.toLogin")}</Button>
            </Link>
          </>
        ) : (
          <form onSubmit={submit} className="space-y-4">
            <Field label={t("profile.newPassword")}>
              <Input
                type="password"
                value={form.new_password}
                onChange={(e) => setForm({ ...form, new_password: e.target.value })}
                autoComplete="new-password"
                required
              />
            </Field>

            <Field label={t("profile.repeatPassword")}>
              <Input
                type="password"
                value={form.repeat}
                onChange={(e) => setForm({ ...form, repeat: e.target.value })}
                autoComplete="new-password"
                required
              />
            </Field>

            {error && <Alert>{error}</Alert>}

            <Button type="submit" className="w-full" disabled={busy}>
              {busy ? t("common.loading") : t("auth.setPassword")}
            </Button>
          </form>
        )}
      </Card>
    </div>
  );
}
