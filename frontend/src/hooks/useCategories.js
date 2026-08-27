import { useEffect, useState } from "react";

import { api } from "../api/client.js";

// Категории нужны почти на каждой странице, а меняются редко.
// Держим их в модульной переменной, чтобы не дёргать API повторно.
let cache = null;

export function useCategories() {
  const [categories, setCategories] = useState(cache || []);

  useEffect(() => {
    if (cache) return;

    let cancelled = false;
    api
      .get("/api/categories/?page_size=100")
      .then((data) => {
        const list = data?.results ?? data ?? [];
        cache = list;
        if (!cancelled) setCategories(list);
      })
      .catch(() => {
        // Категории не критичны: без них просто не покажем название.
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const nameById = (id) => categories.find((c) => c.id === id)?.name;

  return { categories, nameById };
}
