import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { Alert, Button, Card, Field, Input } from "../components/ui.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { useLang } from "../i18n/index.jsx";

export default function Login() {
  const { t } = useLang();
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await login(form.username, form.password);
      navigate(location.state?.from || "/", { replace: true });
    } catch (err) {
      // 429 - сработал троттлинг, 403 - блокировка axes после неудачных попыток.
      if (err.status === 429 || err.status === 403) setError(t("auth.tooManyTries"));
      else setError(t("auth.badCredentials"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-md px-4 py-16">
      <Card className="space-y-5 p-7">
        <h1 className="text-2xl font-bold text-ink">{t("auth.loginTitle")}</h1>

        <form onSubmit={submit} className="space-y-4">
          <Field label={t("auth.username")}>
            <Input
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              autoComplete="username"
              required
            />
          </Field>

          <Field label={t("auth.password")}>
            <Input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              autoComplete="current-password"
              required
            />
          </Field>

          {error && <Alert>{error}</Alert>}

          <Button type="submit" className="w-full" disabled={busy}>
            {busy ? t("common.loading") : t("auth.submitLogin")}
          </Button>
        </form>

        <p className="text-center text-sm text-slate-600">
          {t("auth.noAccount")}{" "}
          <Link to="/register" className="font-semibold text-brand-600 hover:underline">
            {t("auth.registerTitle")}
          </Link>
        </p>
      </Card>
    </div>
  );
}
