import { useState } from "react";

import { api, mediaUrl } from "../api/client.js";
import { useLang } from "../i18n/index.jsx";
import { Alert, Button, Card } from "./ui.jsx";

const MAX_IMAGES = 5;
const MAX_BYTES = 5 * 1024 * 1024;

// Управление картинками курса или урока: загрузка, выбор главной, удаление.
// endpoint и ownerField задаются снаружи, потому что API у курса и урока разные,
// а поведение одинаковое.
export default function ImageManager({ endpoint, ownerField, ownerId, images, onChange }) {
  const { t } = useLang();

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const upload = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = ""; // сбрасываем, чтобы можно было выбрать тот же файл повторно
    if (!file) return;

    setError(null);

    if (file.size > MAX_BYTES) {
      setError(t("images.tooBig"));
      return;
    }

    setBusy(true);
    try {
      const form = new FormData();
      form.append(ownerField, ownerId);
      form.append("image", file);
      // Первая картинка сразу становится главной.
      form.append("is_main", images.length === 0 ? "true" : "false");

      await api.postForm(endpoint, form);
      await onChange();
    } catch (err) {
      setError(err.text || t("common.error"));
    } finally {
      setBusy(false);
    }
  };

  const makeMain = async (id) => {
    setError(null);
    try {
      // Сначала снимаем флаг со старой главной, потом ставим новой:
      // бэкенд не следит за единственностью, это делает клиент.
      const previous = images.find((img) => img.is_main && img.id !== id);
      if (previous) await api.patch(`${endpoint}${previous.id}/`, { is_main: false });
      await api.patch(`${endpoint}${id}/`, { is_main: true });
      await onChange();
    } catch (err) {
      setError(err.text || t("common.error"));
    }
  };

  const remove = async (id) => {
    setError(null);
    try {
      await api.delete(`${endpoint}${id}/`);
      await onChange();
    } catch (err) {
      setError(err.text || t("common.error"));
    }
  };

  return (
    <Card className="space-y-4 p-5">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-ink">{t("images.title")}</h3>
        <span className="text-xs text-slate-500">
          {images.length} / {MAX_IMAGES}
        </span>
      </div>

      {images.length > 0 && (
        <div className="flex flex-wrap gap-3">
          {images.map((img) => (
            <div key={img.id} className="w-32 space-y-1.5">
              <img
                src={mediaUrl(img.image)}
                alt=""
                className={`h-24 w-32 rounded-lg object-cover ${
                  img.is_main ? "ring-2 ring-brand-600" : ""
                }`}
              />
              <div className="flex items-center justify-between text-xs">
                {img.is_main ? (
                  <span className="font-medium text-brand-600">{t("images.main")}</span>
                ) : (
                  <button
                    type="button"
                    onClick={() => makeMain(img.id)}
                    className="text-slate-500 hover:text-brand-600"
                  >
                    {t("images.makeMain")}
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => remove(img.id)}
                  className="text-slate-400 hover:text-red-600"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {images.length < MAX_IMAGES && (
        <div>
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={upload}
            disabled={busy}
            className="block text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-brand-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-brand-700"
          />
          <p className="mt-1 text-xs text-slate-500">{t("images.hint")}</p>
        </div>
      )}

      {busy && <p className="text-sm text-slate-500">{t("common.loading")}</p>}
      {error && <Alert>{error}</Alert>}
    </Card>
  );
}
