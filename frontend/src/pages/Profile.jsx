import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { api } from "../api/client.js";
import { Alert, Badge, Button, Card, Field, Input } from "../components/ui.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { useLang } from "../i18n/index.jsx";

const MAX_AVATAR_BYTES = 5 * 1024 * 1024;

function AvatarBlock() {
  const { t } = useLang();
  const { user, refreshUser } = useAuth();

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [msg, setMsg] = useState(null);
  const [busy, setBusy] = useState(false);

  const pick = (e) => {
    const picked = e.target.files?.[0];
    setMsg(null);
    if (!picked) return;

    if (picked.size > MAX_AVATAR_BYTES) {
      setMsg({ kind: "error", text: t("profile.avatarHint") });
      return;
    }

    setFile(picked);
    setPreview(URL.createObjectURL(picked)); // локальный предпросмотр до отправки
  };

  const upload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setBusy(true);
    setMsg(null);
    try {
      // Файлы уходят через FormData: заголовок Content-Type ставит браузер сам.
      const form = new FormData();
      form.append("image", file);
      await api.patchForm("/api/me/", form);
      await refreshUser();

      setFile(null);
      setPreview(null);
      setMsg({ kind: "success", text: t("profile.avatarSaved") });
    } catch (err) {
      setMsg({ kind: "error", text: err.text || t("common.error") });
    } finally {
      setBusy(false);
    }
  };

  const shown = preview || user.image;

  return (
    <Card className="space-y-4 p-6">
      <h2 className="font-semibold text-ink">{t("profile.avatar")}</h2>

      <div className="flex items-center gap-4">
        {shown ? (
          <img src={shown} alt="" className="h-20 w-20 rounded-full object-cover" />
        ) : (
          <span className="flex h-20 w-20 items-center justify-center rounded-full bg-brand-100 text-2xl font-bold text-brand-700">
            {user.username.slice(0, 1).toUpperCase()}
          </span>
        )}

        <form onSubmit={upload} className="space-y-3">
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={pick}
            className="block text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-brand-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-brand-700"
          />
          <p className="text-xs text-slate-500">{t("profile.avatarHint")}</p>
          {file && (
            <Button type="submit" disabled={busy}>
              {busy ? t("common.loading") : t("profile.upload")}
            </Button>
          )}
        </form>
      </div>

      {msg && <Alert kind={msg.kind}>{msg.text}</Alert>}
    </Card>
  );
}

function EmailBlock() {
  const { t } = useLang();
  const { user, refreshUser } = useAuth();

  const [form, setForm] = useState({ password: "", new_email: "" });
  const [msg, setMsg] = useState(null);
  const [busy, setBusy] = useState(false);
  const [resending, setResending] = useState(false);

  const resend = async () => {
    setResending(true);
    setMsg(null);
    try {
      await api.post("/api/auth/email/verify/", {});
      setMsg({ kind: "success", text: t("profile.verificationSent") });
    } catch (err) {
      setMsg({ kind: "error", text: err.text || t("common.error") });
    } finally {
      setResending(false);
    }
  };

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setMsg(null);
    try {
      await api.post("/api/auth/email/change/", form);
      setForm({ password: "", new_email: "" });
      setMsg({ kind: "success", text: t("profile.emailChangeSent") });
      await refreshUser().catch(() => {});
    } catch (err) {
      setMsg({ kind: "error", text: err.text || t("common.error") });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card className="space-y-4 p-6">
      <h2 className="font-semibold text-ink">{t("profile.email")}</h2>

      <div className="flex flex-wrap items-center gap-3">
        <span className="text-sm text-ink">{user.email}</span>
        {user.email_verified ? (
          <Badge tone="green">{t("profile.emailVerified")}</Badge>
        ) : (
          <>
            <Badge tone="amber">{t("profile.emailNotVerified")}</Badge>
            <Button variant="ghost" onClick={resend} disabled={resending}>
              {resending ? t("common.loading") : t("profile.resendVerification")}
            </Button>
          </>
        )}
      </div>

      <details className="pt-2">
        <summary className="cursor-pointer text-sm font-medium text-brand-600">
          {t("profile.changeEmail")}
        </summary>

        <form onSubmit={submit} className="mt-4 max-w-sm space-y-4">
          <Field label={t("profile.newEmail")}>
            <Input
              type="email"
              value={form.new_email}
              onChange={(e) => setForm({ ...form, new_email: e.target.value })}
              required
            />
          </Field>

          {/* Пароль тут не формальность: смена почты меняет канал восстановления,
              поэтому подтверждаем личность, а не доверяем открытой сессии. */}
          <Field label={t("profile.currentPassword")}>
            <Input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              autoComplete="current-password"
              required
            />
          </Field>

          <Button type="submit" disabled={busy}>
            {busy ? t("common.loading") : t("profile.submitEmail")}
          </Button>
        </form>
      </details>

      {msg && <Alert kind={msg.kind}>{msg.text}</Alert>}
    </Card>
  );
}

function PasswordBlock() {
  const { t } = useLang();
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ old_password: "", new_password: "", repeat: "" });
  const [msg, setMsg] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setMsg(null);

    if (form.new_password !== form.repeat) {
      setMsg({ kind: "error", text: t("profile.passwordsDiffer") });
      return;
    }

    setBusy(true);
    try {
      await api.post("/api/auth/password/change/", {
        old_password: form.old_password,
        new_password: form.new_password,
      });

      // Сервер отозвал все refresh-токены, поэтому дальше только заново войти.
      setMsg({ kind: "success", text: t("profile.passwordChanged") });
      setTimeout(async () => {
        await logout();
        navigate("/login", { replace: true });
      }, 1500);
    } catch (err) {
      setMsg({ kind: "error", text: err.text || t("common.error") });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card className="space-y-4 p-6">
      <h2 className="font-semibold text-ink">{t("profile.changePassword")}</h2>

      <form onSubmit={submit} className="max-w-sm space-y-4">
        <Field label={t("profile.oldPassword")}>
          <Input
            type="password"
            value={form.old_password}
            onChange={(e) => setForm({ ...form, old_password: e.target.value })}
            autoComplete="current-password"
            required
          />
        </Field>

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

        {msg && <Alert kind={msg.kind}>{msg.text}</Alert>}

        <Button type="submit" disabled={busy}>
          {busy ? t("common.loading") : t("profile.submitPassword")}
        </Button>
      </form>
    </Card>
  );
}

export default function Profile() {
  const { t } = useLang();
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-3xl space-y-6 px-4 py-10">
      <div>
        <h1 className="text-3xl font-bold text-ink">{t("profile.title")}</h1>
        <div className="mt-2 flex items-center gap-3 text-sm text-slate-600">
          <span>{user.username}</span>
          <Badge tone={user.role === "teacher" ? "green" : "slate"}>
            {user.role === "teacher" ? t("profile.roleTeacher") : t("profile.roleStudent")}
          </Badge>
        </div>
      </div>

      <AvatarBlock />
      <EmailBlock />
      <PasswordBlock />
    </div>
  );
}
