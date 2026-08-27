import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Alert, Button, Card, Field, Input, Select } from "../components/ui.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { useLang } from "../i18n/index.jsx";

export default function Register() {
  const { t } = useLang();
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    role: "student",
  });
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await register(form);
      navigate("/", { replace: true });
    } catch (err) {
      // Здесь показываем текст от API: он объясняет, чем плох пароль или логин.
      setError(err.text || t("common.error"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-md px-4 py-16">
      <Card className="space-y-5 p-7">
        <h1 className="text-2xl font-bold text-ink">{t("auth.registerTitle")}</h1>

        <form onSubmit={submit} className="space-y-4">
          <Field label={t("auth.username")}>
            <Input
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              autoComplete="username"
              required
            />
          </Field>

          <Field label={t("auth.email")}>
            <Input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              autoComplete="email"
            />
          </Field>

          <Field label={t("auth.password")}>
            <Input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              autoComplete="new-password"
              required
            />
          </Field>

          <Field label={t("auth.role")}>
            <Select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
              <option value="student">{t("auth.roleStudent")}</option>
              <option value="teacher">{t("auth.roleTeacher")}</option>
            </Select>
          </Field>

          {error && <Alert>{error}</Alert>}

          <Button type="submit" className="w-full" disabled={busy}>
            {busy ? t("common.loading") : t("auth.submitRegister")}
          </Button>
        </form>

        <p className="text-center text-sm text-slate-600">
          {t("auth.haveAccount")}{" "}
          <Link to="/login" className="font-semibold text-brand-600 hover:underline">
            {t("auth.loginTitle")}
          </Link>
        </p>
      </Card>
    </div>
  );
}
