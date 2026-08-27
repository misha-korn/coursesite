import { createContext, useContext, useEffect, useMemo, useState } from "react";

import en from "./en.js";
import es from "./es.js";
import ru from "./ru.js";

// Чтобы добавить язык: создай файл рядом, импортируй и допиши сюда одну строку.
export const DICTIONARIES = { ru, en, es };

const STORAGE_KEY = "coursesite_lang";
const LangContext = createContext(null);

function detectLang() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved && DICTIONARIES[saved]) return saved;

  const browser = (navigator.language || "en").slice(0, 2);
  return DICTIONARIES[browser] ? browser : "ru";
}

export function LangProvider({ children }) {
  const [lang, setLang] = useState(detectLang);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, lang);
    document.documentElement.lang = lang;
  }, [lang]);

  const value = useMemo(() => {
    const dict = DICTIONARIES[lang];

    // t("course.buy") -> "Купить курс".
    // Если ключа нет, возвращаем сам ключ, чтобы сразу было видно пропуск.
    const t = (path) => {
      const result = path.split(".").reduce((acc, part) => acc?.[part], dict);
      return typeof result === "string" ? result : path;
    };

    return { lang, setLang, t, languages: Object.keys(DICTIONARIES) };
  }, [lang]);

  return <LangContext.Provider value={value}>{children}</LangContext.Provider>;
}

export function useLang() {
  const ctx = useContext(LangContext);
  if (!ctx) throw new Error("useLang можно вызывать только внутри LangProvider");
  return ctx;
}
