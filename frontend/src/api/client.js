// Тонкая обёртка над fetch: подставляет JWT, сама обновляет протухший access
// по refresh-токену и разбирает ошибки DRF в читаемый текст.

// Запросы уходят на другой origin (5173 -> 8000), поэтому браузер применяет
// к ним политику CORS. Без разрешения со стороны Django ответ будет заблокирован.
// Оператор ?? (а не ||) важен: пустая строка это осмысленное значение
// "используй относительные пути", и подменять её на localhost нельзя.
export const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const ACCESS_KEY = "coursesite_access";
const REFRESH_KEY = "coursesite_refresh";

export const tokens = {
  get access() {
    return localStorage.getItem(ACCESS_KEY);
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY);
  },
  save(access, refresh) {
    if (access) localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

export class ApiError extends Error {
  constructor(status, data) {
    super(`API error ${status}`);
    this.status = status;
    this.data = data;
  }

  // DRF отдаёт ошибки по-разному: строкой, списком, словарём полей.
  // Собираем всё в одну строку для показа пользователю.
  get text() {
    const d = this.data;
    if (!d) return `HTTP ${this.status}`;
    if (typeof d === "string") return d;
    if (d.detail) return String(d.detail);

    return Object.entries(d)
      .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(", ") : msgs}`)
      .join("\n");
  }
}

async function parseBody(response) {
  const type = response.headers.get("content-type") || "";
  if (!type.includes("application/json")) return null;
  try {
    return await response.json();
  } catch {
    return null;
  }
}

// Меняем протухший access на новый. Если refresh тоже мёртв, чистим хранилище.
async function refreshAccess() {
  const refresh = tokens.refresh;
  if (!refresh) return false;

  const response = await fetch(`${API_BASE}/api/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    tokens.clear();
    return false;
  }

  const data = await response.json();
  tokens.save(data.access, data.refresh);
  return true;
}

async function request(method, path, body, { retry = true } = {}) {
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (tokens.access) headers.Authorization = `Bearer ${tokens.access}`;

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  // 401 значит "access протух" - пробуем обновить и повторить один раз.
  if (response.status === 401 && retry) {
    const ok = await refreshAccess();
    if (ok) return request(method, path, body, { retry: false });
  }

  if (!response.ok) throw new ApiError(response.status, await parseBody(response));
  if (response.status === 204) return null;

  return parseBody(response);
}

// Отдельный путь для файлов: тут нельзя ставить Content-Type руками,
// браузер должен сам проставить multipart/form-data с разделителем.
async function requestForm(method, path, formData, { retry = true } = {}) {
  const headers = {};
  if (tokens.access) headers.Authorization = `Bearer ${tokens.access}`;

  const response = await fetch(`${API_BASE}${path}`, { method, headers, body: formData });

  if (response.status === 401 && retry) {
    const ok = await refreshAccess();
    if (ok) return requestForm(method, path, formData, { retry: false });
  }

  if (!response.ok) throw new ApiError(response.status, await parseBody(response));
  return parseBody(response);
}

export const api = {
  get: (path) => request("GET", path),
  post: (path, body) => request("POST", path, body),
  patch: (path, body) => request("PATCH", path, body),
  delete: (path) => request("DELETE", path),
  patchForm: (path, formData) => requestForm("PATCH", path, formData),
};

// Собирает "/api/courses/?search=js&page=2", пропуская пустые значения.
export function withQuery(path, params) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) search.append(key, value);
  });
  const qs = search.toString();
  return qs ? `${path}?${qs}` : path;
}
