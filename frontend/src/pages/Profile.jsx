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
          {user.email && <span>{user.email}</span>}
          <Badge tone={user.role === "teacher" ? "green" : "slate"}>
            {user.role === "teacher" ? t("profile.roleTeacher") : t("profile.roleStudent")}
          </Badge>
        </div>
      </div>

      <AvatarBlock />
      <PasswordBlock />
    </div>
  );
}
